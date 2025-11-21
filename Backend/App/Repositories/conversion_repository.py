"""
Conversion module
"""

import io
from PIL import Image
from Services.conversion_service import IConversionService

class ConversionRepository(IConversionService):
    """
    Conversion repository class
    """
    async def convert_image(self, file_content: bytes, out_format: str) -> tuple[str, bytes]:
        """
        convert image from various types
        """
        try:
            image = Image.open(io.BytesIO(file_content))
        except Exception as e:
            raise ValueError(
                f"Failed to convert to {out_format.upper()}: {str(e)}"
            ) from e

        if image.mode in ("RGBA", "LA"):
            background = Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[-1])
            image = background
        elif image.mode != "RGB":
            image = image.convert("RGB")

        buffer = io.BytesIO()
        try:
            image.save(buffer, format=out_format.upper(), optimize=True)
        except Exception as e:
            raise ValueError(
                 f"Failed to convert {image.format} to {out_format.upper()}: {str(e)}"
            ) from e
        return str(image.format), buffer.getvalue()

    async def convert_video_audio(self, file_content: bytes, out_format: str) -> tuple[str, bytes]:
        """
        convert audio and video from various types
        """