from fastapi import APIRouter, Depends
from ..core.deps import get_current_active_user
from ..models.user import User, UserRead

router = APIRouter()

@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_active_user)):
    return current_user 