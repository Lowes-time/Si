# -*- coding: utf-8 -*-
"""
薄膜分析记录API：CRUD操作
支持按薄膜编号(film_code)查询和管理历史记录
"""
import pandas as pd
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import insert, text
from pydantic import BaseModel

from si.backend.database import get_db, engine
from si.backend.models import FilmRecord, OpticalData
from si.utils.pdf_generator import build_record_pdf

router = APIRouter(prefix="/api/records", tags=["records"])


class OpticalDataItem(BaseModel):
    """单个光学数据点"""
    wavelength: float
    reflectance: float
    fitted_reflectance: Optional[float] = None
    seq_order: int = 0


class RecordCreate(BaseModel):
    """创建薄膜分析记录的请求模型"""
    film_code: str
    material_type: str
    thickness_um: Optional[float] = None
    r_squared: Optional[float] = None
    multi_beam_level: Optional[str] = None
    theta_deg: Optional[float] = None
    notes: Optional[str] = None
    optical_data: List[OpticalDataItem] = []


class RecordResponse(BaseModel):
    """薄膜分析记录响应模型"""
    id: int
    film_code: str
    material_type: str
    thickness_um: Optional[float]
    r_squared: Optional[float]
    multi_beam_level: Optional[str]
    theta_deg: Optional[float]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class RecordListResponse(BaseModel):
    """薄膜分析记录列表响应模型（带分页）"""
    data: List[RecordResponse]
    total: int
    skip: int
    limit: int


@router.post("/", response_model=RecordResponse)
def create_record(record: RecordCreate, db: Session = Depends(get_db)):
    """
    创建新的薄膜分析记录
    
    Args:
        record: 包含薄膜编号、材质、计算结果和光学数据的记录对象
    
    Returns:
        新创建的记录信息
    """
    # 创建薄膜记录
    db_record = FilmRecord(
        film_code=record.film_code,
        material_type=record.material_type,
        thickness_um=record.thickness_um,
        r_squared=record.r_squared,
        multi_beam_level=record.multi_beam_level,
        theta_deg=record.theta_deg,
        notes=record.notes,
        created_at=datetime.now()
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)

    # 批量插入光学数据
    if record.optical_data:
        optical_records = [
            {
                "record_id": db_record.id,
                "wavelength": item.wavelength,
                "reflectance": item.reflectance,
                "fitted_reflectance": item.fitted_reflectance,
                "seq_order": item.seq_order
            }
            for item in record.optical_data
        ]
        db.execute(insert(OpticalData), optical_records)
        db.commit()

    return db_record


@router.get("/", response_model=RecordListResponse)
def read_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    查询薄膜分析记录列表（支持分页）
    
    Args:
        skip: 分页偏移量
        limit: 每页记录数限制
        search: 按薄膜编号模糊搜索
        db: 数据库会话
    
    Returns:
        包含数据和总数信息的分页响应
    """
    query = db.query(FilmRecord)
    
    if search:
        query = query.filter(FilmRecord.film_code.contains(search))
    
    # 获取总数
    total_count = query.count()
    
    # 获取分页数据
    records = query.order_by(FilmRecord.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "data": records,
        "total": total_count,
        "skip": skip,
        "limit": limit
    }


@router.get("/{record_id}")
def read_record(record_id: int, db: Session = Depends(get_db)):
    """
    获取单条记录的详细信息及关联的光学数据
    
    Args:
        record_id: 记录ID
        db: 数据库会话
    
    Returns:
        包含光学数据数组的完整记录信息
    """
    db_record = db.query(FilmRecord).filter(FilmRecord.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="记录不存在")

    # 使用pandas高效读取关联的光学数据
    with engine.connect() as conn:
        df = pd.read_sql(
            text("""
                SELECT wavelength, reflectance, fitted_reflectance, seq_order 
                FROM optical_data 
                WHERE record_id = :rec_id 
                ORDER BY seq_order, wavelength
            """),
            con=conn,
            params={"rec_id": record_id}
        )

    return {
        "id": db_record.id,
        "film_code": db_record.film_code,
        "material_type": db_record.material_type,
        "thickness_um": db_record.thickness_um,
        "r_squared": db_record.r_squared,
        "multi_beam_level": db_record.multi_beam_level,
        "theta_deg": db_record.theta_deg,
        "notes": db_record.notes,
        "created_at": db_record.created_at,
        "data": {
            "wavelength": df["wavelength"].tolist(),
            "reflectance": df["reflectance"].tolist(),
            "ref_fit": df["fitted_reflectance"].tolist() if not df["fitted_reflectance"].isna().all() else []
        }
    }


@router.delete("/{record_id}")
def delete_record(record_id: int, db: Session = Depends(get_db)):
    """
    删除薄膜分析记录（级联删除关联的光学数据）
    
    Args:
        record_id: 记录ID
        db: 数据库会话
    
    Returns:
        删除操作结果
    """
    db_record = db.query(FilmRecord).filter(FilmRecord.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    db.delete(db_record)
    db.commit()
    return {"success": True, "message": "记录已删除"}


@router.get("/{record_id}/report")
def download_report(record_id: int, db: Session = Depends(get_db)):
    """下载 PDF 检测报告"""
    db_record = db.query(FilmRecord).filter(FilmRecord.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="记录不存在")

    payload = {
        "film_code": db_record.film_code,
        "material_type": db_record.material_type,
        "thickness_um": db_record.thickness_um,
        "r_squared": db_record.r_squared,
        "multi_beam_level": db_record.multi_beam_level,
        "theta_deg": db_record.theta_deg,
        "notes": db_record.notes,
    }
    pdf_bytes = build_record_pdf(payload)
    filename = f"report_{db_record.film_code}.pdf".replace(" ", "_")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )