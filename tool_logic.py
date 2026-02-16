import io
import qrcode
import re
from PIL import Image
from core_db import record_interaction

class AuraServices:
    """
    هذا الكود هو "القيمة الحقيقية" التي يراها مراجع أدسنس.
    نحن لا نقدم نصوصاً فقط، بل وظائف برمجية (Backend Functions).
    """
    
    @staticmethod
    def process_image_webp(image_stream: bytes, quality: int = 85) -> bytes:
        """تحويل وضغط الصور لصيغة WebP - معيار جوجل للسرعة"""
        img = Image.open(io.BytesIO(image_stream))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        
        output = io.BytesIO()
        img.save(output, format="WEBP", quality=quality)
        record_interaction("webp_pro")
        return output.getvalue()

    @staticmethod
    def generate_secure_qr(payload: str) -> bytes:
        """توليد كود QR عالي الدقة للروابط والبيانات"""
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(payload)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="#1e293b", back_color="white")
        output = io.BytesIO()
        img.save(output, format="PNG")
        record_interaction("qr_generator")
        return output.getvalue()

    @staticmethod
    def extract_link_meta(target_url: str):
        """تحليل الروابط واستخراج البيانات الوصفية للسيو"""
        # منطق استخراج معرف يوتيوب كمثال لأداة سيو
        video_id = None
        patterns = [r"v=([a-zA-Z0-9_-]+)", r"be/([a-zA-Z0-9_-]+)"]
        for p in patterns:
            match = re.search(p, target_url)
            if match:
                video_id = match.group(1)
                break
        
        if video_id:
            record_interaction("meta_extractor")
            return {
                "id": video_id,
                "thumb": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
            }
        return None
