import time
from collections import defaultdict, deque
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .config import FRONTEND_ORIGINS, RATE_LIMIT_PER_MIN, RATE_LIMIT_HEAVY_PER_MIN
from .routers.ai import router as ai_router
from .routers.student import router as student_router
from .routers.teacher import router as teacher_router

app = FastAPI(title="LearnLens AI Service", version="2.0.0", description="Learning diagnosis, grounded lessons, spaced retesting, and class insights.")
_hits: dict[str, deque] = defaultdict(deque)
_HEAVY = ("/work/analyze", "/diagnostic/", "/lesson/", "/quiz/", "/diagnosis", "/auth/join", "/teacher/classes", "/feedback")

@app.middleware("http")
async def rate_limit(request: Request, call_next):
    # shortcut: per-instance memory, so limits are per server process; upgrade to Redis/Upstash if you scale out.
    if request.method == "OPTIONS" or request.url.path == "/health":
        return await call_next(request)
    ip = (request.headers.get("x-forwarded-for") or (request.client.host if request.client else "unknown")).split(",")[0].strip()
    heavy = request.method == "POST" and request.url.path.startswith(_HEAVY)
    key, limit, now = f"{ip}|{'heavy' if heavy else 'all'}", (RATE_LIMIT_HEAVY_PER_MIN if heavy else RATE_LIMIT_PER_MIN), time.monotonic()
    hits = _hits[key]
    while hits and now - hits[0] > 60:
        hits.popleft()
    if len(hits) >= limit:
        return JSONResponse({"detail": "Too many requests. Please wait a minute and try again."}, status_code=429, headers={"Retry-After": "60"})
    hits.append(now)
    if len(_hits) > 5000:  # bound memory
        for k in [k for k, v in _hits.items() if not v or now - v[-1] > 60]:
            _hits.pop(k, None)
    return await call_next(request)

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-Teacher-Key", "Authorization"],
)
app.include_router(student_router)
app.include_router(teacher_router)
app.include_router(ai_router)
