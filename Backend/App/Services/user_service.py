"""User service"""

from abc import ABC, abstractmethod

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