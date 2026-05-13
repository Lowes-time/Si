# -*- coding: utf-8 -*-
"""
数据库初始化模块
用于在服务启动时初始化数据库表结构
"""
from si.backend.database import engine, Base

def init_database():
    """初始化数据库表结构"""
    Base.metadata.create_all(bind=engine)
    print("数据库表初始化完成。")


if __name__ == "__main__":
    init_database()