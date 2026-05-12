# -*- coding: utf-8 -*-
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from si.backend.database import get_db
from si.backend.models import Material, AnalysisRecord

router = APIRouter(prefix="/api/materials", tags=["materials"])

class MaterialBase(BaseModel):
    name: str
    description: Optional[str] = None

class MaterialCreate(MaterialBase):
    pass

class MaterialUpdate(MaterialBase):
    pass

class MaterialResponse(MaterialBase):
    id: int

    class Config:
        from_attributes = True

@router.get("/", response_model=List[MaterialResponse])
def get_materials(db: Session = Depends(get_db)):
    return db.query(Material).order_by(Material.id.asc()).all()

@router.post("/", response_model=MaterialResponse)
def create_material(material: MaterialCreate, db: Session = Depends(get_db)):
    existing = db.query(Material).filter(Material.name == material.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Material with this name already exists")
    db_material = Material(name=material.name, description=material.description)
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    return db_material

@router.put("/{material_id}", response_model=MaterialResponse)
def update_material(material_id: int, material: MaterialUpdate, db: Session = Depends(get_db)):
    db_material = db.query(Material).filter(Material.id == material_id).first()
    if not db_material:
        raise HTTPException(status_code=404, detail="Material not found")
        
    if material.name != db_material.name:
        existing = db.query(Material).filter(Material.name == material.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Material with this name already exists")
            
    db_material.name = material.name
    db_material.description = material.description
    db.commit()
    db.refresh(db_material)
    return db_material

@router.delete("/{material_id}")
def delete_material(material_id: int, db: Session = Depends(get_db)):
    db_material = db.query(Material).filter(Material.id == material_id).first()
    if not db_material:
        raise HTTPException(status_code=404, detail="Material not found")
        
    # Check if any records are using this material
    usage_count = db.query(AnalysisRecord).filter(AnalysisRecord.material_id == material_id).count()
    if usage_count > 0:
        raise HTTPException(status_code=400, detail=f"Cannot delete material: currently used by {usage_count} analysis records.")
        
    db.delete(db_material)
    db.commit()
    return {"success": True}
