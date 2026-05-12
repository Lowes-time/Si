# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from si.backend.database import Base

class Material(Base):
    __tablename__ = "materials"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)
    description = Column(String(255), nullable=True)
    
    records = relationship("AnalysisRecord", back_populates="material")

class AnalysisRecord(Base):
    __tablename__ = "analysis_records"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=True)
    calc_time = Column(DateTime, default=datetime.now)
    material_id = Column(Integer, ForeignKey("materials.id"))
    thickness_um = Column(Float)
    r_squared = Column(Float)
    multi_beam_level = Column(String(50))
    meta_info = Column(Text, nullable=True)

    material = relationship("Material", back_populates="records")
    spectral_data = relationship("SpectralData", back_populates="record", cascade="all, delete-orphan")

class SpectralData(Base):
    __tablename__ = "spectral_data"
    
    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(Integer, ForeignKey("analysis_records.id", ondelete="CASCADE"), index=True)
    wavelength = Column(Float, index=True)
    reflectance = Column(Float)
    fitted_reflectance = Column(Float, nullable=True)
    
    record = relationship("AnalysisRecord", back_populates="spectral_data")
