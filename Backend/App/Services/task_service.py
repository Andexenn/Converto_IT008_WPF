"""task service interface"""

from abc import ABC, abstractmethod
from typing import List

from Schemas.task import TaskByUserID, TaskBase

class ITaskService(ABC):
    """Task service interface"""

    @abstractmethod
    async def get_all_task_by_user(self, user_id: int) -> List[TaskByUserID]:
        """
        Get all task from a user
            
        Paramenters:
        ------------
            user_id(int): the user id 

        Returns:
        --------
            TaskByUserID type
        """ 

    @abstractmethod
    async def get_all_task(self) -> List[TaskBase]:
        """
        Get all task

        Returns:
        --------
            Return all tasks from all user
        """

    @abstractmethod
    async def get_all_task_by_service(self, service_type_id: int) -> List[TaskBase]:
        """
        Get all task from of a service type

        Returns:
        --------
            Return all tasks from a specific service
        """


