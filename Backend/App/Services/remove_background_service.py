"""Remove background module"""

from abc import ABC, abstractmethod
from typing import List, Tuple 

class IRemoveBackgroundSerivce(ABC):
    """Remove background class"""

    @abstractmethod
    async def remove_background(self, input_path: str) -> Tuple[str, int]:
        """
        Remove background from the image

        Parameter:
        ----------
            input_path(str): the path to the original file

        Return:
        -------
            Tuple[str, int]: the output path and the size of the file
        """

    @abstractmethod
    async def remove_backgrounds_batch(self, input_paths: List[str]) -> List[Tuple[str, str, int, bool]]:
        """
        Remove background with a batch of images

        Parameter:
        ----------
            input_paths(List[str]): the list of input path

        Return:
        -------
            List[Tuple[str, str, int, bool]]: Return a list of tuple after remove background
        """
