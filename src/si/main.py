# -*- coding: utf-8 -*-
"""
半导体薄膜厚度光学测量分析系统 V1.0 — 后端 API 服务
基于多光束干涉校正的半导体外延层厚度光谱反演系统后端
"""
import sys
import os

# 将 src 目录添加到 Python 路径，以便直接运行
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from si.backend.api.data import router as data_router
from si.backend.api.preprocess import router as preprocess_router
from si.backend.api.calculation import router as calculation_router
from si.backend.api.records import router as records_router
from si.backend.config import APP_NAME, APP_VERSION, CORS_ORIGINS
from si.backend.exceptions import register_handlers
from si.backend.database import engine, Base
from si.backend.seed import init_database

# 导入模型以确保SQLAlchemy能够发现并创建表
import si.backend.models

# 初始化数据库
Base.metadata.create_all(bind=engine)
init_database()

app = FastAPI(title=APP_NAME, version=APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册异常处理器
register_handlers(app)

# 注册API路由
app.include_router(data_router)
app.include_router(preprocess_router)
app.include_router(calculation_router)
app.include_router(records_router)


@app.get("/")
def root():
    """健康检查接口"""
    return {"service": APP_NAME, "version": APP_VERSION, "status": "running"}


def start():
    """启动FastAPI服务器"""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    start()