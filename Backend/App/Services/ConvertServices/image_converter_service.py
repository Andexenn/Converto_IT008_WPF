from abc import ABC, abstractmethod
from typing import BinaryIO, Tuple
import io 

class IImageConverterServices(ABC):
    @abstractmethod
    async def convert_webp_to_png(self, file_content: bytes, filename: str) -> Tuple[bytes, str]:
        pass 

    

