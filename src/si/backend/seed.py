# -*- coding: utf-8 -*-
from si.backend.database import SessionLocal, engine, Base
from si.backend.models import Material

def seed_materials():
    db = SessionLocal()
    try:
        # 预设的材料数据
        default_materials = ["Si", "SiC", "SiO2", "Si3N4"]
        
        for mat_name in default_materials:
            existing = db.query(Material).filter(Material.name == mat_name).first()
            if not existing:
                new_mat = Material(name=mat_name)
                db.add(new_mat)
        
        db.commit()
        print("材料数据初始化完成。")
    except Exception as e:
        db.rollback()
        print(f"初始化材料数据时出错: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    seed_materials()
