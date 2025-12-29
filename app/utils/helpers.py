import urllib.parse

def get_laundry_html(target_url):
    # --- The Authority Bouncing Strategy (V3) ---
    # الهدف: جعل المصدر يظهر كـ "google.com" بدلاً من موقعك.
    # الطريقة: نرسل الزائر لرابط إعادة توجيه خاص بجوجل، ومنه يذهب لهدفك.
    
    # 1. تشفير رابطك ليقبله جوجل
    encoded_target = urllib.parse.quote(target_url)
    
    # 2. استخدام بوابة "Google Images" (أقل كشفاً للتحويلات)
    # ملاحظة: قد تظهر صفحة "Redirect Notice" لبعض المستخدمين، لكن المصدر سيُسجل كـ Google.
    google_bounce_url = f"https://images.google.com/url?q={encoded_target}"
    
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="referrer" content="unsafe-url"> <title>Loading...</title>
        <style>
            body {{ background-color: #ffffff; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }}
            .spinner {{ width: 40px; height: 40px; border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; animation: spin 1s linear infinite; }}
            @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
            .msg {{ margin-top: 20px; font-family: arial; color: #555; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="spinner"></div>
        <div class="msg">Establishing Secure Connection...</div>

        <a id="bouncer" href="{google_bounce_url}" style="display:none;" rel="noreferrer"></a>

        <script>
            // خداع المتصفح: مسح التاريخ الحالي حتى لا يعود الزائر للخلف
            if (window.history.replaceState) {{
                window.history.replaceState(null, null, window.location.href);
            }}

            // تنفيذ القفزة (Bounce)
            setTimeout(function() {{
                var link = document.getElementById('bouncer');
                
                // محاولة النقر البرمجي
                if(document.createEvent) {{
                    var evt = document.createEvent("MouseEvents");
                    evt.initEvent("click", true, true);
                    link.dispatchEvent(evt);
                }} else {{
                    link.click();
                }}
            }}, 800); // انتظار أقل من ثانية
        </script>
    </body>
    </html>
    '''
