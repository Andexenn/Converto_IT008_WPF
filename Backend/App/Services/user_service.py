"""User service"""

from abc import ABC, abstractmethod
from fastapi import BackgroundTasks
from Schemas.user import UserData, UserPref

class IUserService(ABC):
    """Class user service"""

    @abstractmethod
    async def get_user(self, user_id: int) -> UserData:
        """
        Get the data of a user

        Parameters:
        -----------
            user_id(int): ID of the user

        Returns:
        --------
            UserData: All necessary information
        """

    @abstractmethod
    async def get_user_preference(self, user_id: int) -> UserPref:
        """
        Get preferences of the user

        Parameters:
        -----------
            user_id(int): ID of the user

        Returns:
        --------
            UserPreferences:  Preference of the user
        """

    @abstractmethod
    async def update_user_data(self, user_data: UserData) -> UserData:
        """
        Update the information of the user
        """

    @abstractmethod
    async def update_user_preferences(self, user_preferences: UserPref) -> UserPref:
        """
        Update preferences of the user
        """

    @abstractmethod
    async def send_email(self, email: str, email_type: str, background_tasks: BackgroundTasks) -> dict:
        """Send email to user"""

    @abstractmethod
    async def verify_email_user(self, email: str ) -> bool:
        """Verify if the email exists"""

    @abstractmethod
    async def delete_user(self, user_id: int) -> None:
        """Delete user from database"""