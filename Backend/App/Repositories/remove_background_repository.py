"""
Remove background repository
"""

import io
import os 
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path 
from typing import List, Tuple 
import asyncio
import tempfile

import rembg
from PIL import Image

from Services.remove_background_service import IRemoveBackgroundSerivce

class RemoveBackgroundRepository(IRemoveBackgroundSerivce):
    """
    Remove background of the image 
    """

    def __init__(self):
        self.max_workers = max(1, multiprocessing.cpu_count() - 1)

    @staticmethod
    async def _run_in_executor(func, *args):
        """Helper to run sync function in executor processing"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func, *args)

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

        return await self._run_in_executor(
            self._remove_background_sync,
            input_path
        )
    
    async def remove_backgrounds_batch(self, input_paths: List[str]) -> List[Tuple[str, str, int, bool]]:
        if not input_paths:
            return []
        
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_path = {
                executor.submit(
                    self._remove_background_sync,
                    input_path
                ) : input_path for input_path in input_paths
            }

            results = []

            for future in as_completed(future_to_path):
                input_path = future_to_path[future]

                try:
                    output_path, file_size = future.result()
                    results.append((input_path, output_path, file_size, True))
                except Exception as e:
                    print(f"Failed to remove background: {str(e)}")
                    results.append((input_path, None, 0, False))
                    
            return results

    @staticmethod
    def _remove_background_sync(input_path: str) -> Tuple[str, int]:

        if not Path(input_path).exists():
            raise FileNotFoundError(f"File {input_path} not found")
        
        if os.path.getsize(input_path) == 0:
            raise ValueError("The input file was empty")
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'{Path(input_path).suffix}')
        output_path = temp_file.name 
        temp_file.close()

        try:
            input_image = Image.open(input_path)
        except Exception as e:
            raise ValueError(f"{input_path} can not be opened") from e
        
        try:
            removed_image = rembg.remove(input_image)
            removed_image.save(output_path) #pylint: disable=reportAttributeAccessIssue
        except Exception as e:
            raise ValueError(f"File at {input_path} was cannot be opened") from e 
        
        return output_path, os.path.getsize(output_path)
    



        
