"""
Agente RAG que combina búsqueda en documentos con LLM.
"""
from typing import List, Dict, Optional
import logging

from agent.llm_client import get_llm_client
from rag import get_vector_store

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """Eres un asistente experto en normativa AESA (Agencia Estatal de Seguridad Aérea) para drones, especializado en las categorías A1, A2 y A3.

Tu objetivo es ayudar a los usuarios con consultas sobre:
- Requisitos y limitaciones de cada categoría
- Distancias de seguridad
- Zonas permitidas y restringidas
- Procedimientos operacionales
- Formación y certificación necesarias

INSTRUCCIONES IMPORTANTES:
1. Basa tus respuestas ÚNICAMENTE en la información proporcionada en el contexto de los documentos AESA
2. Si la información no está en el contexto, di claramente "No encuentro esa información en la documentación que tengo disponible"
3. Cita siempre la fuente cuando sea posible (ej: "Según el reglamento AESA...")
4. Sé claro, preciso y conciso
5. Si detectas que la consulta requiere intervención humana (casos muy específicos, interpretaciones legales complejas), sugiérelo
6. Usa un tono profesional pero amigable

Recuerda: La seguridad aérea es prioritaria, así que es mejor ser conservador en las respuestas que arriesgarse a dar información incorrecta."""


class RAGAgent:
    """Agente que combina RAG con LLM para responder consultas."""
    
    def __init__(self):
        """Inicializa el agente RAG."""
        self.llm = get_llm_client()
        self.vector_store = get_vector_store()
        logger.info("✅ Agente RAG inicializado")
    
    def search_relevant_context(
        self,
        query: str,
        n_results: int = 5,
        document_type: Optional[str] = None
    ) -> tuple[str, List[Dict]]:
        """
        Busca contexto relevante en los documentos.
        
        Args:
            query: Consulta del usuario
            n_results: Número de resultados a buscar
            document_type: Filtrar por tipo de documento (opcional)
        
        Returns:
            Tupla de (contexto_combinado, fuentes)
        """
        logger.info(f"🔍 Buscando contexto para: '{query[:100]}...'")
        
        # Buscar en el vector store
        where_filter = {"document_type": document_type} if document_type else None
        
        results = self.vector_store.search(
            query=query,
            n_results=n_results,
            where=where_filter
        )
        
        # Combinar los documentos encontrados
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]
        
        if not documents:
            logger.warning("⚠️ No se encontraron documentos relevantes")
            return "", []
        
        # Crear contexto combinado
        context_parts = []
        sources = []
        
        for i, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances)):
            relevance = 1 - dist
            
            context_parts.append(
                f"--- Fragmento {i+1} (Relevancia: {relevance:.0%}) ---\n"
                f"Fuente: {meta.get('source', 'Desconocida')}\n"
                f"{doc}\n"
            )
            
            sources.append({
                "source": meta.get('source', 'Desconocida'),
                "document_type": meta.get('document_type', 'unknown'),
                "relevance": relevance,
                "chunk_index": meta.get('chunk_index', 0)
            })
        
        context = "\n".join(context_parts)
        
        logger.info(f"✅ Encontrados {len(documents)} fragmentos relevantes")
        
        return context, sources
    
    def generate_response(
        self,
        user_query: str,
        conversation_history: Optional[List[Dict]] = None,
        document_type: Optional[str] = None
    ) -> Dict:
        """
        Genera una respuesta usando RAG + LLM.
        
        Args:
            user_query: Pregunta del usuario
            conversation_history: Historial previo de la conversación
            document_type: Filtrar búsqueda por tipo de documento
        
        Returns:
            Diccionario con content, metadata y sources
        """
        logger.info(f"💬 Generando respuesta para: '{user_query[:100]}...'")
        
        # 1. Buscar contexto relevante
        context, sources = self.search_relevant_context(
            query=user_query,
            n_results=5,
            document_type=document_type
        )
        
        # 2. Construir mensajes para el LLM
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        
        # Añadir historial de conversación si existe
        if conversation_history:
            for msg in conversation_history[-10:]:  # Últimos 10 mensajes
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Añadir contexto y consulta actual
        if context:
            user_message = f"""CONTEXTO DE DOCUMENTOS AESA:
{context}

---

CONSULTA DEL USUARIO:
{user_query}

Responde basándote en el contexto proporcionado."""
        else:
            user_message = f"""CONSULTA DEL USUARIO:
{user_query}

NOTA: No se encontró información específica en los documentos. Responde indicando que no tienes esa información disponible y sugiere consultar con AESA directamente."""
        
        messages.append({"role": "user", "content": user_message})
        
        # 3. Generar respuesta con el LLM
        llm_response = self.llm.chat_completion(
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        # 4. Construir respuesta completa
        response = {
            "content": llm_response["content"],
            "sources": sources,
            "metadata": {
                **llm_response["metadata"],
                "sources_count": len(sources),
                "has_context": bool(context)
            }
        }
        
        logger.info(f"✅ Respuesta generada. Tokens: {response['metadata']['tokens_total']}")
        
        return response
    
    def should_escalate(self, response: Dict) -> tuple[bool, str]:
        """
        Determina si la consulta debe escalarse a un humano.
        
        Args:
            response: Respuesta generada
        
        Returns:
            Tupla de (should_escalate, reason)
        """
        content = response["content"].lower()
        sources_count = response["metadata"]["sources_count"]
        
        # Reglas de escalado
        if sources_count == 0:
            return True, "No se encontró información relevante en la documentación"
        
        if "no encuentro" in content or "no tengo información" in content:
            return True, "El agente no pudo encontrar información específica"
        
        if "consulta con aesa" in content or "contacta con" in content:
            return True, "La consulta requiere verificación oficial"
        
        # Palabras clave que indican casos complejos
        complex_keywords = ["legal", "demanda", "accidente", "sanción", "multa"]
        if any(keyword in content for keyword in complex_keywords):
            return True, "Consulta de naturaleza legal o compleja"
        
        return False, ""


# Instancia global del agente
_rag_agent = None

def get_rag_agent() -> RAGAgent:
    """
    Dependency para obtener el agente RAG.
    Usa singleton pattern.
    """
    global _rag_agent
    
    if _rag_agent is None:
        _rag_agent = RAGAgent()
    
    return _rag_agent
