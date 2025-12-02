"""Task handler"""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from Database.connection import get_db
from Core.dependencies import get_current_user
from Repositories.task_repository import TaskRepository
from Services.task_service import ITaskService
from Schemas.task import TaskByUserID, TaskBase
from Entities.user import User

router = APIRouter()

@router.get('/task/task_by_user', response_model=List[TaskByUserID])
async def get_all_task_by_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)) -> List[TaskByUserID]:
    """
    Get all task by user_id

    Parameters:
    -----------
        user_id(int): the user id 
        db(Session): the working session

    Returns:
    --------
        A list of TaskByUserID 
    """

    task_service: ITaskService = TaskRepository(db)
    return await task_service.get_all_task_by_user(current_user.UserID)

@router.get('/task/task_by_service/{service_type_id}', response_model=List[TaskBase])
async def get_all_task_by_service(
    service_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[TaskBase]:
    
    task_service: ITaskService = TaskRepository(db)
    return await task_service.get_all_task_by_service(service_type_id)

@router.get('/task/all_tasks', response_model=List[TaskBase])
async def get_all_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[TaskBase]:
    
    task_service: ITaskService = TaskRepository(db)
    return await task_service.get_all_task()
