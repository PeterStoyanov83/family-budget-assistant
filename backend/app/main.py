from fastapi import FastAPI, Request
from fastapi.responses import Response

from app.core.config import settings
from app.routers import auth, lists, products, promotions

app = FastAPI(
    title="Family AI Budget Assistant",
    description="AI-powered family shopping optimizer for the Bulgarian market",
    version="0.1.0",
)


def _is_allowed_origin(origin: str) -> bool:
    explicit = {o.strip() for o in settings.cors_origins.split(",")}
    return origin in explicit or origin.endswith(".up.railway.app")


@app.middleware("http")
async def cors_middleware(request: Request, call_next):
    origin = request.headers.get("origin", "")

    if request.method == "OPTIONS":
        res = Response(status_code=200)
        if _is_allowed_origin(origin):
            res.headers["Access-Control-Allow-Origin"] = origin
            res.headers["Access-Control-Allow-Credentials"] = "true"
            res.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,PATCH,DELETE,OPTIONS"
            res.headers["Access-Control-Allow-Headers"] = "*"
            res.headers["Access-Control-Max-Age"] = "600"
        return res

    response = await call_next(request)
    if _is_allowed_origin(origin):
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(promotions.router)
app.include_router(lists.router)


@app.get("/health")
async def health():
    return {"status": "ok", "version": app.version, "build": "cors-v3"}


@app.get("/metrics")
async def metrics():
    return {"status": "ok"}
