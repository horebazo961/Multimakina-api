from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Multimakina Cloud Secure API")

# Configuración obligatoria de CORS para conectar Frontend (Vercel) con Backend (Render)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite conexiones desde cualquier dominio (Vercel, móvil, etc.)
    allow_credentials=True,
    allow_methods=["*"],  # Permite GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],
)

# ... (tus rutas y lógica existente de base de datos)