from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from atguigu.app.routers import run


app = FastAPI(title="Ecommerce AI Service")

app.include_router(run.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5174",
        "http://127.0.0.1:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
