from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..core.deps import get_current_active_user, get_current_admin_user
from ..db.session import get_session
from ..models.project import Project, ProjectCreate, ProjectRead
from ..models.user import User

router = APIRouter()

@router.get("/", response_model=List[ProjectRead])
def list_projects(
    *,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100
):
    projects = db.exec(select(Project).offset(skip).limit(limit)).all()
    return projects

@router.get("/{project_id}", response_model=ProjectRead)
def get_project(
    *,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
    project_id: int
):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.post("/", response_model=ProjectRead)
def create_project(
    *,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user),
    project_in: ProjectCreate
):
    project = Project(
        name=project_in.name,
        description=project_in.description,
        created_by_id=current_user.id
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

@router.put("/{project_id}", response_model=ProjectRead)
def update_project(
    *,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user),
    project_id: int,
    project_in: ProjectCreate
):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project.name = project_in.name
    project.description = project_in.description
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

@router.delete("/{project_id}")
def delete_project(
    *,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user),
    project_id: int
):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(project)
    db.commit()
    return {"ok": True} 