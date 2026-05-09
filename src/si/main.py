# -*- coding: utf-8 -*-
"""
半导体薄膜厚度光学测量分析系统 V1.0 — 后端 API 服务
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from si.backend.api.data import router as data_router
from si.backend.api.preprocess import router as preprocess_router
from si.backend.api.calculation import router as calculation_router
from si.backend.config import APP_NAME, APP_VERSION, CORS_ORIGINS
from si.backend.exceptions import register_handlers

app = FastAPI(title=APP_NAME, version=APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_handlers(app)

app.include_router(data_router)
app.include_router(preprocess_router)
app.include_router(calculation_router)


@app.get("/")
def root():
    return {"service": APP_NAME, "version": APP_VERSION}


def start():
    import uvicorn
    uvicorn.run("si.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    start()
