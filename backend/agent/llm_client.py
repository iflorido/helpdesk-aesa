"""
Cliente LLM para interactuar con OpenAI.
"""
from openai import OpenAI
from typing import List, Dict, Optional
import logging

from core.config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """Cliente para interactuar con OpenAI API."""
    
    def __init__(self):
        """Inicializa el cliente de OpenAI."""
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY no está configurado en .env")
        
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o-mini"  # Modelo más económico y rápido
        logger.info(f"✅ Cliente OpenAI inicializado con modelo: {self.model}")
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict:
        """
        Genera una respuesta del modelo.
        
        Args:
            messages: Lista de mensajes [{"role": "user|assistant|system", "content": "..."}]
            temperature: Creatividad (0-2, default 0.7)
            max_tokens: Máximo de tokens en la respuesta
        
        Returns:
            Diccionario con la respuesta y metadata
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            content = response.choices[0].message.content
            
            metadata = {
                "model": response.model,
                "tokens_prompt": response.usage.prompt_tokens,
                "tokens_completion": response.usage.completion_tokens,
                "tokens_total": response.usage.total_tokens,
                "finish_reason": response.choices[0].finish_reason
            }
            
            logger.info(f"✅ Respuesta generada. Tokens: {metadata['tokens_total']}")
            
            return {
                "content": content,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"❌ Error llamando a OpenAI: {e}")
            raise
    
    def chat_completion_streaming(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000
    ):
        """
        Genera una respuesta del modelo con streaming.
        
        Args:
            messages: Lista de mensajes
            temperature: Creatividad
            max_tokens: Máximo de tokens
        
        Yields:
            Chunks de texto conforme se generan
        """
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"❌ Error en streaming de OpenAI: {e}")
            raise


# Instancia global del cliente
_llm_client = None

def get_llm_client() -> LLMClient:
    """
    Dependency para obtener el cliente LLM.
    Usa singleton pattern.
    """
    global _llm_client
    
    if _llm_client is None:
        _llm_client = LLMClient()
    
    return _llm_client
