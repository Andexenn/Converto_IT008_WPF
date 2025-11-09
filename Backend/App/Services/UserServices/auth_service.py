from abc import ABC, abstractmethod
from typing import Optional 
from Schemas.user import UserCreate, UserResponse, UserLogin, UserLoginResponse

class IAuthService(ABC):
    @abstractmethod
    async def sign_up(self, user_data: UserCreate) -> UserResponse:
        pass 

    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        pass 

    @abstractmethod 
    async def user_exists(self, email: str) -> bool:
        pass 

    @abstractmethod
    async def login(self, user_dat: UserLogin) -> UserLoginResponse:
        pass