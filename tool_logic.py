import io
import qrcode
from PIL import Image
from core_db import record_usage

class ToolEngine:
    @staticmethod
    def convert_webp(image_bytes: bytes) -> bytes:
        img = Image.open(io.BytesIO(image_bytes))
        if img.mode in ("RGBA", "P"): img = img.convert("RGB")
        out = io.BytesIO()
        img.save(out, format="WEBP", quality=85)
        record_usage("webp-pro")
        return out.getvalue()

    @staticmethod
    def generate_qr(data: str) -> bytes:
        qr = qrcode.QRCode(box_size=10, border=2)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        out = io.BytesIO()
        img.save(out, format="PNG")
        record_usage("qr-generator")
        return out.getvalue()
