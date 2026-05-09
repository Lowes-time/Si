# -*- coding: utf-8 -*-
"""全局异常处理"""
from fastapi import Request
from fastapi.responses import JSONResponse


async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": f"服务器内部错误: {str(exc)}"},
    )


def register_handlers(app):
    app.add_exception_handler(Exception, generic_exception_handler)
