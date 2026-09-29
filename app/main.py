from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import cases, system, health

app = FastAPI(
    title="CredentialIQ AI API (Python Engine)",
    description="Agentic Healthcare Provider Credentialing Proof of Concept - Python Engine",
    version="1.0.0-poc",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cases.router)
app.include_router(system.router)
app.include_router(health.router)

@app.get("/")
async def root():
    return {
        "name": "CredentialIQ AI API (Python)",
        "status": "Running",
        "docs": "/docs",
        "health": "/health"
    }
