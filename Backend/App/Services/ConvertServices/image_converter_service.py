from abc import ABC, abstractmethod
from typing import BinaryIO
import io 

class IImageConverterServices(ABC):
    @abstractmethod
    async def convert_webp_to_png(self, file_content: bytes, filename: str) -> tuple[bytes, str]:
        pass 

    

