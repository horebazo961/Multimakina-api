# Multimakina API

Sistema de gestión vehicular para talleres (Multimakina).

## Arquitectura objetivo (gratuita para pruebas)

| Capa | Servicio | Plan |
|------|----------|------|
| Frontend | Vercel | Free |
| Backend  | Render  | Free |
| Base de datos | Supabase (Postgres) | Free |

## Requisitos

- Python 3.11+
- Cuenta en Supabase (gratis)
- Cuenta en Render (gratis)
- Cuenta en Vercel (gratis)

## Variables de entorno obligatorias

Copia `.env.example` a `.env` y completa:

```bash
DATABASE_URL=postgresql://...
CORS_ORIGINS=http://localhost:3000,https://tu-dominio.vercel.app
SECRET_KEY=una-clave-muy-larga-y-aleatoria
```

**Nunca subas el archivo `.env` real al repositorio.**

## Desarrollo local (backend)

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

## Despliegue backend en Render (Free)

1. New → Web Service → conecta este repositorio.
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Environment Variables:
   - `DATABASE_URL` = connection string de Supabase (Session Pooler, puerto 6543)
   - `CORS_ORIGINS` = `http://localhost:3000,https://tu-app.vercel.app`
   - `SECRET_KEY` = genera una clave larga

## Frontend

El frontend (Next.js) usa la variable `NEXT_PUBLIC_API_URL` apuntando a la URL de Render.

## Seguridad

- No hay secretos en el código.
- DATABASE_URL solo se lee de variables de entorno.
- CORS restringido por orígenes explícitos + regex de Vercel.

## Estado

Base limpia lista para pruebas gratuitas (octubre 2026).
