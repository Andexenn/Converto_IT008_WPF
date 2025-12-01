"""
Remove background repository
"""

import os
import time
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import List, Tuple
import asyncio
import tempfile

from sqlalchemy.orm import Session
import rembg
from PIL import Image

from Services.remove_background_service import IRemoveBackgroundSerivce
from Entities.tasks import Tasks
from Schemas.task import TaskRemoveBackground

SERVICETYPEID = 3
class RemoveBackgroundRepository(IRemoveBackgroundSerivce):
    """
    Remove background of the image
    """

    def __init__(self, db:Session, UserID: int):
        self.max_workers = max(1, multiprocessing.cpu_count() - 1)

        self.db = db
        self.user_id = UserID

    @staticmethod
    async def _run_in_executor(func, *args):
        """Helper to run sync function in executor processing"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func, *args)

    def _record_task(self, task: TaskRemoveBackground):
        """Record the task"""
        task_dict = task.model_dump(exclude_unset=True)
        cur_task = Tasks(**task_dict)
        self.db.add(cur_task)

        self.db.commit()

        return True

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

        data = await self._run_in_executor(
            self._remove_background_sync,
            input_path
        )

        task = TaskRemoveBackground(
            UserID=self.user_id,
            ServiceTypeID=SERVICETYPEID,
            OriginalFileName=data["OriginalFileName"],
            OriginalFileSize=data["OriginalFileSize"],
            OriginalFilePath=data["OriginalFilePath"],
            OutputFileName=data["OutputFileName"],
            OutputFileSize=data["OutputFileSize"],
            OutputFilePath=data["OutputFilePath"],
            TaskStatus=True,
            TaskTime=data["TaskTime"]
        )

        self._record_task(task)

        return (str(task.OutputFilePath), int(task.OutputFileSize))

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
                    data = future.result()

                    task = TaskRemoveBackground(
                        UserID=self.user_id,
                        ServiceTypeID=SERVICETYPEID,
                        OriginalFileName=data["OriginalFileName"],
                        OriginalFileSize=data["OriginalFileSize"],
                        OriginalFilePath=data["OriginalFilePath"],
                        OutputFileName=data["OutputFileName"],
                        OutputFileSize=data["OutputFileSize"],
                        OutputFilePath=data["OutputFilePath"],
                        TaskStatus=True,
                        TaskTime=data["TaskTime"]
                    )

                    self._record_task(task)

                    results.append((task.OriginalFilePath, task.OutputFilePath, task.OutputFileSize, True))
                except Exception as e:
                    print(f"Failed to compress {input_path}: {str(e)}")
                    task = TaskRemoveBackground(
                        UserID=self.user_id,
                        ServiceTypeID=SERVICETYPEID,
                        OriginalFileName=Path(input_path).stem,
                        OriginalFileSize=os.path.getsize(input_path),
                        OriginalFilePath=input_path,
                        TaskStatus=False,
                        TaskTime=0
                    )

                    self._record_task(task)
                    results.append((input_path, "", 0, False))

        return results

    @staticmethod
    def _remove_background_sync(input_path: str) -> dict:

        if not Path(input_path).exists():
            raise FileNotFoundError(f"File {input_path} not found")

        if os.path.getsize(input_path) == 0:
            raise ValueError("The input file was empty")

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'{Path(input_path).suffix}')
        output_path = temp_file.name
        temp_file.close()

        start_time = time.perf_counter()

        try:
            input_image = Image.open(input_path)
        except Exception as e:
            raise ValueError(f"{input_path} can not be opened") from e

        try:
            removed_image = rembg.remove(input_image)
            if removed_image.mode != 'RGBA':
                removed_image = removed_image.convert('RGBA')
            
            # Save as PNG (supports transparency)
            removed_image.save(output_path, format='PNG', optimize=True)
        except Exception as e:
            raise ValueError(f"File at {input_path} was cannot be opened") from e

        end_time = time.perf_counter()

        return {
            "OriginalFileName": Path(input_path).stem,
            "OriginalFileSize": os.path.getsize(input_path),
            "OriginalFilePath": input_path,
            "OutputFileName": Path(output_path).stem,
            "OutputFileSize": os.path.getsize(output_path),
            "OutputFilePath": output_path,
            "TaskStatus": (True if os.path.getsize(output_path) != 0 else False),
            "TaskTime": end_time - start_time
        }





