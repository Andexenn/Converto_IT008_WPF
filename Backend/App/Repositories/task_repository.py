"""Task repository"""

from typing import List

from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from Schemas.task import TaskBase, TaskByUserID
from Services.task_service import ITaskService
from Entities.tasks import Tasks
from Entities.user import User 

class TaskRepository(ITaskService):
    """Task repository class"""
    def __init__(self, db: Session):
        self.db = db

    async def get_all_task_by_user(self, user_id: int) -> List[TaskByUserID]:
        try:
            user_tasks = self.db.query(Tasks).filter(Tasks.UserID == user_id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to query user tasks: {str(e)}"
            ) from e
        
        results = [
            TaskByUserID(
                ServiceTypeID=user_task.ServiceTypeID,
                OriginalFilePath=user_task.OriginalFilePath,
                OriginalFileSize=user_task.OriginalFileSize,
                OutputFilePath=user_task.OutputFilePath,
                OutputFileSize=user_task.OutputFileSize,
                TaskStatus=user_task.TaskStatus,
                TaskTime=user_task.TaskTime,
                CreatedAt=user_task.CreatedAt
            ) for user_task in user_tasks
        ]

        return results

    async def get_all_task(self) -> List[TaskBase]:
        try:
            tasks = (
                self.db.query(Tasks)
                .options(
                    joinedload(Tasks.User),
                    joinedload(Tasks.TaskType)
                )
                .order_by(desc(Tasks.CreatedAt))
                .all()
            )

            results = [
                TaskBase(
                UserID=task.UserID,
                ServiceTypeID=task.ServiceTypeID,
                OriginalFileName=task.OriginalFileName,
                OriginalFilePath=task.OriginalFilePath,
                OriginalFileSize=task.OriginalFileSize,
                OutputFilePath=task.OutputFilePath,
                OutputFileSize=task.OutputFileSize,
                TaskStatus=task.TaskStatus,
                TaskTime=task.TaskTime
                ) for task in tasks
            ]
            
            return results
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to query all tasks: {str(e)}"
            ) from e 

    async def get_all_task_by_service(self, service_type_id: int) -> List[TaskBase]:
        try:
            service_tasks = self.db.query(Tasks).filter(Tasks.ServiceTypeID == service_type_id).order_by(desc(Tasks.CreatedAt))
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Fail to query task by service: {str(e)}"
            ) from e

        results = [
            TaskBase(
                UserID=service_task.UserID,
                ServiceTypeID=service_task.ServiceTypeID,
                OriginalFileName=service_task.OriginalFileName,
                OriginalFilePath=service_task.OriginalFilePath,
                OriginalFileSize=service_task.OriginalFileSize,
                OutputFilePath=service_task.OutputFilePath,
                OutputFileSize=service_task.OutputFileSize,
                TaskStatus=service_task.TaskStatus,
                TaskTime=service_task.TaskTime
            ) for service_task in service_tasks
        ]

        return results



