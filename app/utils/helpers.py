import urllib.parse

def get_laundry_html(target_url):
    # تنظيف وترميز الهدف بشكل آمن
    clean_url = target_url.strip()
    # لا حاجة لترميز إضافي في meta refresh داخل HTML
    safe_target = clean_url.replace('"', '%22')  # لتجنب حقن HTML

    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <!-- مهم جدًا: منع إرسال مصدر الزيارة -->
        <meta name="referrer" content="no-referrer">
        <title></title>
        <style>
            body {{
                margin: 0;
                padding: 0;
                background: #fff;
                font-family: Arial, sans-serif;
            }}
        </style>
    </head>
    <body>
        <!-- عنصر شفاف لخداع بوتات التتبع -->
        <img src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7" width="1" height="1" alt="">

        <script>
            // مسح السجل (لمنع العودة للرابط الأصلي)
            try {{
                if (window.history.replaceState) {{
                    window.history.replaceState(null, null, "./");
                }}
            }} catch (e) {{}}

            // تأخير عشوائي بين 400ms و 900ms لمحاكاة سلوك بشري
            setTimeout(function() {{
                // التوجيه بدون إرسال referrer
                window.location.replace("{safe_target}");
            }}, Math.floor(Math.random() * 500) + 400);
        </script>
    </body>
    </html>
    '''
