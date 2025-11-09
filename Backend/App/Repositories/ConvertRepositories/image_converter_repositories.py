from PIL import Image 
import io 
from Services.ConvertServices.image_converter_service import IImageConverterServices

class ImageConverterRepositories(IImageConverterServices):
    async def convert_webp_to_png(self, file_content: bytes, filename: str):
        try:
            image = Image.open(io.BytesIO(file_content))

            if image.mode in ('RGBA', 'LA', 'P'):
                pass 
            elif image.mode != 'RGB':
                image = image.convert('RGB')

            png_buffer = io.BytesIO()
            image.save(png_buffer, format='PNG', optimize=True)

            png_bytes = png_buffer.getvalue()
            new_filename = filename.rsplit('.', 1)[0] + '.png'

            return png_bytes, new_filename
        except Exception as e:
            raise ValueError(f"Failed to convert WEBP to PNG: {str(e)}")

