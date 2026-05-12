# -*- coding: utf-8 -*-
import json
import io
import pandas as pd
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import insert, text
from pydantic import BaseModel

from si.backend.database import get_db, engine
from si.backend.models import AnalysisRecord, Material, SpectralData

router = APIRouter(prefix="/api/records", tags=["records"])

class RecordCreate(BaseModel):
    name: Optional[str] = None
    material: str
    thickness_um: float
    r_squared: float
    multi_beam_level: str
    data_json: dict

class RecordResponse(BaseModel):
    id: int
    name: Optional[str] = None
    calc_time: datetime
    material: str
    thickness_um: float
    r_squared: float
    multi_beam_level: str

    class Config:
        from_attributes = True

@router.post("/", response_model=RecordResponse)
def create_record(record: RecordCreate, db: Session = Depends(get_db)):
    mat = db.query(Material).filter(Material.name == record.material).first()
    if not mat:
        mat = Material(name=record.material)
        db.add(mat)
        db.commit()
        db.refresh(mat)
        
    db_record = AnalysisRecord(
        name=record.name,
        material_id=mat.id,
        thickness_um=record.thickness_um,
        r_squared=record.r_squared,
        multi_beam_level=record.multi_beam_level
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    
    data_json = record.data_json
    wavelengths = data_json.get("wavelength", [])
    reflectances = data_json.get("reflectance", [])
    ref_fits = data_json.get("ref_fit", [])
    
    spectral_records = []
    for i in range(len(wavelengths)):
        fit_val = ref_fits[i] if i < len(ref_fits) else None
        spectral_records.append({
            "record_id": db_record.id,
            "wavelength": wavelengths[i],
            "reflectance": reflectances[i],
            "fitted_reflectance": fit_val
        })
        
    if spectral_records:
        db.execute(insert(SpectralData), spectral_records)
        db.commit()

    return {
        "id": db_record.id,
        "name": db_record.name,
        "calc_time": db_record.calc_time,
        "material": mat.name,
        "thickness_um": db_record.thickness_um,
        "r_squared": db_record.r_squared,
        "multi_beam_level": db_record.multi_beam_level
    }

@router.get("/", response_model=List[RecordResponse])
def read_records(
    skip: int = 0, 
    limit: int = 100, 
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(AnalysisRecord, Material.name.label('material_name')).join(Material)
    if search:
        query = query.filter(AnalysisRecord.name.contains(search))
    results = query.order_by(AnalysisRecord.calc_time.desc()).offset(skip).limit(limit).all()
    
    out = []
    for record, mat_name in results:
        out.append({
            "id": record.id,
            "name": record.name,
            "calc_time": record.calc_time,
            "material": mat_name,
            "thickness_um": record.thickness_um,
            "r_squared": record.r_squared,
            "multi_beam_level": record.multi_beam_level
        })
    return out

@router.get("/{record_id}")
def read_record(record_id: int, db: Session = Depends(get_db)):
    query = db.query(AnalysisRecord, Material.name.label('material_name')).join(Material).filter(AnalysisRecord.id == record_id).first()
    if not query:
        raise HTTPException(status_code=404, detail="Record not found")
        
    db_record, mat_name = query
    
    # 关键性能优化：使用 pandas.read_sql 直接读取
    with engine.connect() as conn:
        df = pd.read_sql(
            text("SELECT wavelength, reflectance, fitted_reflectance AS ref_fit FROM spectral_data WHERE record_id = :rec_id ORDER BY wavelength"), 
            con=conn, 
            params={"rec_id": record_id}
        )
    
    data = {
        "wavelength": df["wavelength"].tolist(),
        "reflectance": df["reflectance"].tolist(),
        "ref_fit": df["ref_fit"].tolist() if df["ref_fit"].notna().any() else []
    }
    
    result = {
        "id": db_record.id,
        "name": db_record.name,
        "calc_time": db_record.calc_time,
        "material": mat_name,
        "thickness_um": db_record.thickness_um,
        "r_squared": db_record.r_squared,
        "multi_beam_level": db_record.multi_beam_level,
        "data": data
    }
    return result

@router.delete("/{record_id}")
def delete_record(record_id: int, db: Session = Depends(get_db)):
    db_record = db.query(AnalysisRecord).filter(AnalysisRecord.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="Record not found")
    db.delete(db_record)
    db.commit()
    return {"success": True}
