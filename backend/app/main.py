from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import auth, lists, products, promotions

app = FastAPI(
    title="Family AI Budget Assistant",
    description="AI-powered family shopping optimizer for the Bulgarian market",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(promotions.router)
app.include_router(lists.router)


@app.get("/health")
async def health():
    return {"status": "ok", "version": app.version}


@app.get("/metrics")
async def metrics():
    return {"status": "ok"}
