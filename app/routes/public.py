from flask import Blueprint, request, redirect, render_template_string
from app.utils.helpers import is_bot, get_laundry_html

public_bp = Blueprint('public', __name__)

# الصفحة الرئيسية (سنضيف التصميم الاحترافي لاحقاً)
@public_bp.route('/')
def home():
    return "<h1 style='font-family:sans-serif;text-align:center;padding:50px'>TRAFICOON Enterprise System<br><span style='color:green'>● Live</span></h1>"

# رابط الغسالة (The Redirector)
@public_bp.route('/redirect')
def redirect_engine():
    url = request.args.get('url')
    traffic_type = request.args.get('type')
    
    if not url: return redirect('/')
    
    # حقن UTM (قناع جوجل)
    if "aliexpress.com" in url or traffic_type == "organic":
        if "utm_source" not in url:
            sep = "&" if "?" in url else "?"
            url += f"{sep}utm_source=google&utm_medium=organic&utm_campaign=search_result"
    
    # استدعاء الغسالة من ملف helpers
    return get_laundry_html(url)
