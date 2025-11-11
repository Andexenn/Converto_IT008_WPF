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
    async def convert(self, file_content: bytes, out_format: str) -> tuple[str, bytes]:
        try:
            image = Image.open(io.BytesIO(file_content))
        except Exception as e:
            raise ValueError(
                f"Failed to convert to {out_format.upper()}: {str(e)}"
            ) from e

        if image.mode in ('RGBA', 'LA', 'P'):
            pass
        elif image.mode != 'RGB':
            image = image.convert('RGB')

        buffer = io.BytesIO()
        try:
            image.save(buffer, format=out_format.upper(), optimize=True)
        except Exception as e:
            raise ValueError(
                 f"Failed to convert {image.format} to {out_format.upper()}: {str(e)}"
            ) from e
        return str(image.format), buffer.getvalue()
