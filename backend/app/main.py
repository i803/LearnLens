from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import FRONTEND_ORIGINS
from .routers.ai import router as ai_router
from .routers.student import router as student_router
from .routers.teacher import router as teacher_router

app = FastAPI(title="LearnLens AI Service", version="2.0.0", description="Learning diagnosis, grounded lessons, spaced retesting, and class insights.")
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
