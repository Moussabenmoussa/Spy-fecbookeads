# templates.py

# --- 1. User Landing Page (With HTML Injection Support & Back-Hijack) ---
LANDING_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secure Access</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap" rel="stylesheet">
    <style> 
        body { font-family: 'Inter', sans-serif; background: #f1f5f9; } 
        /* تنسيق المقالات المحقونة */
        .article-content img { max-width: 100%; border-radius: 1rem; margin: 1rem 0; }
        .article-content h2, .article-content h3 { font-weight: 800; color: #1e293b; margin-top: 1.5rem; margin-bottom: 0.5rem; }
        .article-content p { margin-bottom: 1rem; line-height: 1.6; }
        .article-content ul { list-style: disc; padding-left: 1.5rem; margin-bottom: 1rem; }
    </style>
</head>
<body class="min-h-screen flex items-center justify-center p-4">
    <div class="max-w-md w-full bg-white rounded-3xl p-8 shadow-2xl text-center relative overflow-hidden">
        
        <div class="mb-8">
            <div class="w-20 h-20 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-4 text-3xl shadow-sm">🚀</div>
            <h1 class="text-2xl font-black text-slate-800">Human Verification</h1>
            <p class="text-slate-400 text-sm mt-2">Complete the step below to unlock your download.</p>
        </div>

        <div id="step_1" class="transition-all duration-500">
            <div class="bg-orange-50 border border-orange-100 p-4 rounded-2xl mb-6">
                <p class="text-orange-600 text-xs font-bold uppercase tracking-widest mb-1">Step 1/2</p>
                <p class="text-slate-600 text-sm font-medium">Activate the download server by viewing our sponsor.</p>
            </div>
            
            <a href="/redirect?url={{ s.stuffing_url|urlencode }}" target="_blank" onclick="startTimer()" class="block w-full bg-slate-900 hover:bg-slate-800 text-white py-5 rounded-xl font-bold shadow-lg transform transition active:scale-95 flex items-center justify-center gap-2">
                <span>Open Sponsor Page</span>
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
            </a>
            <p class="text-xs text-slate-400 mt-4">Link unlocks in <span id="timer_display" class="font-bold text-slate-600">10</span> seconds after clicking.</p>
        </div>

        <div id="step_2" class="hidden opacity-0 transform translate-y-10 transition-all duration-500">
            <div class="bg-green-50 border border-green-100 p-4 rounded-2xl mb-6">
                <p class="text-green-600 text-xs font-bold uppercase tracking-widest mb-1">Success</p>
                <p class="text-slate-600 text-sm font-medium">Server activated successfully.</p>
            </div>
            
            <a href="/redirect?url={{ target_url|urlencode }}" class="block w-full bg-blue-600 hover:bg-blue-700 text-white py-5 rounded-xl font-bold shadow-xl shadow-blue-200 animate-bounce">
                Download File Now
            </a>
        </div>
        
        <div class="mt-10 pt-10 border-t border-slate-100 text-left">
            <h2 class="text-lg font-bold text-slate-800 mb-4">{{ article.title }}</h2>
            <div class="text-slate-500 text-sm article-content">
                {{ article.body|safe }}
            </div>
        </div>

    </div>

    <script>
        const exitUrl = "/redirect?url=" + encodeURIComponent("{{ s.exit_url }}");
        let timeLeft = 10; 

        function startTimer() {
            // Back-Hijack Logic
            if ("{{ s.exit_url }}" !== "") {
                try {
                    history.pushState(null, null, location.href);
                    window.onpopstate = function() { location.replace(exitUrl); };
                } catch(e) {}
            }

            const btn = document.querySelector('#step_1 a');
            btn.style.opacity = "0.5";
            btn.style.pointerEvents = "none";
            btn.innerText = "Verifying...";

            const timerDisplay = document.getElementById('timer_display');
            const interval = setInterval(() => {
                timeLeft--;
                timerDisplay.innerText = timeLeft;
                
                if (timeLeft <= 0) {
                    clearInterval(interval);
                    showDownload();
                }
            }, 1000);
        }

        function showDownload() {
            document.getElementById('step_1').style.display = 'none';
            const step2 = document.getElementById('step_2');
            step2.classList.remove('hidden');
            setTimeout(() => { step2.classList.remove('opacity-0', 'translate-y-10'); }, 50);
        }
    </script>
</body>
</html>
"""

# --- 2. Admin Dashboard (Updated with Article Manager) ---
ADMIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Elite Master Panel</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
    <style> body { font-family: 'Inter', sans-serif; background: #f8fafc; } </style>
</head>
<body class="p-4 text-slate-800">
    <div class="max-w-4xl mx-auto">
        <header class="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100 mb-6 flex justify-between items-center">
            <h1 class="text-xl font-black text-blue-600 tracking-tighter uppercase">Kraken Control</h1>
            <span class="bg-blue-50 text-blue-600 text-[10px] font-black px-4 py-2 rounded-full border border-blue-100">STABLE v3</span>
        </header>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div class="bg-white p-8 rounded-[2.5rem] shadow-sm border border-slate-100">
                <h2 class="text-xs font-black text-slate-400 uppercase tracking-widest mb-6">Monetization</h2>
                <form action="/admin/update_settings" method="POST" class="space-y-4">
                    <input name="stuffing_url" value="{{ s.stuffing_url }}" placeholder="AliExpress Product Link" class="w-full p-4 bg-slate-50 border border-slate-100 rounded-2xl outline-none focus:border-blue-500 text-xs font-mono">
                    <input name="exit_url" value="{{ s.exit_url }}" placeholder="Exit Ad Link (Tonic)" class="w-full p-4 bg-slate-50 border border-slate-100 rounded-2xl outline-none focus:border-blue-500 text-xs font-mono">
                    <button class="w-full bg-slate-900 text-white py-4 rounded-2xl font-black text-xs uppercase tracking-widest active:scale-95 transition">Save Settings</button>
                </form>
            </div>

            <div class="bg-white p-8 rounded-[2.5rem] shadow-sm border border-slate-100">
                <h2 class="text-xs font-black text-slate-400 uppercase tracking-widest mb-6">Create Link</h2>
                <form action="/admin/create_link" method="POST" class="space-y-4">
                    <input name="title" placeholder="Asset Name" class="w-full p-4 bg-slate-50 border border-slate-100 rounded-2xl outline-none focus:border-blue-500 text-xs" required>
                    <input name="target_url" placeholder="Final Download Link" class="w-full p-4 bg-slate-50 border border-slate-100 rounded-2xl outline-none focus:border-blue-500 text-xs" required>
                    <button class="w-full bg-blue-600 text-white py-4 rounded-2xl font-black text-xs uppercase tracking-widest shadow-xl shadow-blue-100 active:scale-95 transition">Generate</button>
                </form>
            </div>
        </div>

        <div class="bg-white p-8 rounded-[2.5rem] shadow-sm border border-slate-100 mb-8 border-l-4 border-l-emerald-400">
            <h2 class="text-xs font-black text-emerald-500 uppercase tracking-widest mb-6">HTML Article Injector (CMS)</h2>
            <form action="/admin/add_article" method="POST" class="space-y-4">
                <input name="title" placeholder="Article Headline (e.g. Netflix Review 2025)" class="w-full p-4 bg-slate-50 border border-slate-100 rounded-2xl outline-none focus:border-emerald-500 text-xs font-bold" required>
                <textarea name="html_content" placeholder="Paste full HTML here (include <p>, <img>, <ul> tags)..." class="w-full p-4 bg-slate-50 border border-slate-100 rounded-2xl outline-none focus:border-emerald-500 text-xs font-mono h-32" required></textarea>
                <button class="w-full bg-emerald-600 text-white py-4 rounded-2xl font-black text-xs uppercase tracking-widest shadow-xl shadow-emerald-100 active:scale-95 transition">Inject Article to DB</button>
            </form>

            <div class="mt-6 space-y-2">
                {% for art in articles %}
                <div class="flex justify-between items-center bg-slate-50 p-3 rounded-xl">
                    <span class="text-xs font-bold text-slate-600 truncate w-2/3">{{ art.title }}</span>
                    <a href="/admin/delete_article/{{ art._id }}" class="text-[10px] text-red-500 font-bold hover:underline">DELETE</a>
                </div>
                {% endfor %}
            </div>
        </div>

        <div class="space-y-4 pb-20">
            <h2 class="text-xs font-black text-slate-400 uppercase tracking-widest px-2">Active Assets</h2>
            {% for link in links %}
            <div class="bg-white p-6 rounded-[2.5rem] shadow-sm border border-slate-100">
                <div class="flex justify-between items-center mb-4">
                    <div>
                        <span class="font-black text-slate-800 text-sm">{{ link.title }}</span>
                        <span class="block text-[9px] text-blue-500 font-bold mt-1 uppercase">Clicks: {{ link.clicks }}</span>
                    </div>
                    <a href="/admin/delete/{{ link._id }}" class="text-red-300 hover:text-red-500">🗑️</a>
                </div>
                <div class="flex gap-2">
                    <input id="u_{{ link._id }}" value="{{ host_url }}v/{{ link.slug }}" class="flex-1 p-3 bg-slate-50 border border-slate-100 rounded-xl text-[9px] font-mono outline-none" readonly>
                    <button onclick="copy('u_{{ link._id }}')" class="bg-blue-600 text-white px-5 rounded-xl text-[10px] font-bold">COPY</button>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    <script>
        function copy(id) {
            var c = document.getElementById(id); c.select(); document.execCommand("copy");
            alert("Link copied!");
        }
    </script>
</body>
</html>
"""
