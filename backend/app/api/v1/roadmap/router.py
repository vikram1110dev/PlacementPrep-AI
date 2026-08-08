from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.dependencies.auth import get_current_user
from app.models.auth import User
from app.schemas.base import StandardResponse
from app.schemas.roadmap import (
    RoadmapSetupRequest, RoadmapResponse, TaskStatusUpdateRequest
)
from app.services.roadmap_service import RoadmapService

router = APIRouter(prefix="/roadmap", tags=["Roadmap"])

@router.post("/generate", response_model=StandardResponse)
def generate_roadmap(request: RoadmapSetupRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = RoadmapService(db)
    roadmap = service.generate_roadmap(current_user.id, request)
    return StandardResponse(success=True, message="Roadmap generated", data=RoadmapResponse.from_orm(roadmap).dict())

@router.get("/current", response_model=StandardResponse)
def get_current_roadmap(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = RoadmapService(db)
    roadmap = service.get_current_roadmap(current_user.id)
    if not roadmap:
        return StandardResponse(success=True, message="No active roadmap", data=None)
    return StandardResponse(success=True, message="Roadmap retrieved", data=RoadmapResponse.from_orm(roadmap).dict())

@router.get("/{roadmap_id}", response_model=StandardResponse)
def get_roadmap_by_id(roadmap_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = RoadmapService(db)
    roadmap = service.get_roadmap_by_id(current_user.id, roadmap_id)
    return StandardResponse(success=True, message="Roadmap retrieved", data=RoadmapResponse.from_orm(roadmap).dict())

@router.post("/task/{task_id}/status", response_model=StandardResponse)
def update_task_status(task_id: str, request: TaskStatusUpdateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = RoadmapService(db)
    result = service.update_task_status(current_user.id, task_id, request)
    return StandardResponse(success=True, message=result["message"], data=None)

@router.post("/regenerate", response_model=StandardResponse)
def regenerate_roadmap(request: RoadmapSetupRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = RoadmapService(db)
    roadmap = service.generate_roadmap(current_user.id, request)
    return StandardResponse(success=True, message="Roadmap regenerated", data=RoadmapResponse.from_orm(roadmap).dict())
