from fastapi import APIRouter

from si.algorithms.optical_constants import OpticalConstants

router = APIRouter(prefix="/api", tags=["materials"])


@router.get("/materials")
def list_materials():
    """返回系统支持的半导体材料列表"""
    items = OpticalConstants.list_supported_materials()
    return {"success": True, "data": items}
