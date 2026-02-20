# 🚀 Helpdesk AESA Frontend

Frontend React + TypeScript + TailwindCSS para el sistema de helpdesk AESA A2.

## 📦 Stack Tecnológico

- **React 18** con Vite
- **TypeScript** para tipado seguro
- **TailwindCSS** con paleta AESA personalizada
- **React Router** para navegación
- **Zustand** para gestión de estado
- **React Query** para cache de datos
- **Axios** para llamadas API

## 🎨 Diseño

- Paleta de colores AESA oficial
- Glass morphism effects
- Transiciones suaves estilo Apple
- Diseño responsive
- Inter font

## 🚀 Instalación

```bash
cd frontend
npm install
```

## ⚙️ Configuración

Crea un archivo `.env` en la raíz de frontend:

```env
VITE_API_URL=http://localhost:8000
```

## 🏃 Desarrollo

```bash
npm run dev
```

El frontend estará disponible en http://localhost:3000

## 📁 Estructura Pendiente

Necesitas crear estos archivos adicionales (los compartiré a continuación):

```
src/
├── components/
│   ├── Layout.tsx
│   ├── Navbar.tsx
│   └── ui/
│       ├── Button.tsx
│       ├── Input.tsx
│       └── Card.tsx
├── pages/
│   ├── LoginPage.tsx
│   ├── RegisterPage.tsx
│   ├── DashboardPage.tsx
│   └── ChatPage.tsx
└── lib/
    └── utils.ts
```

## 🎯 Características

- ✅ Login/Registro con JWT
- ✅ Dashboard con lista de tickets
- ✅ Chat en tiempo real con el agente
- ✅ Diseño glass morphism
- ✅ Responsive
- ✅ Gestión de estado global

## 🔗 Conexión con Backend

El frontend se conecta automáticamente al backend en `http://localhost:8000` gracias al proxy de Vite.

## 📝 Notas

- Los componentes usan la paleta AESA definida en tailwind.config.js
- El token JWT se guarda en localStorage
- React Query maneja el cache de peticiones
