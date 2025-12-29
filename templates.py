# templates.py
# نسخة: تسريع الكوكيز فقط (بدون حظر بوتات)

# --- 1. User Landing Page (Speed Enhanced) ---
LANDING_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secure Access</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <link rel="prefetch" href="/redirect?url={{ s.stuffing_url|urlencode }}">
    
    <style> 
        body { font-family: 'Inter', sans-serif; background: #f8fafc; color: #334155; }
        .article-content { color: #475569; font-size: 1.05rem; line-height: 1.7; }
        .article-content h2 { color: #1e293b; font-weight: 700; font-size: 1.5rem; margin-top: 2rem; margin-bottom: 1rem; letter-spacing: -0.025em; }
        .article-content h3 { color: #334155; font-weight: 600; font-size: 1.25rem; margin-top: 1.5rem; margin-bottom: 0.75rem; }
        .article-content p { margin-bottom: 1.25rem; }
        .article-content ul { list-style: disc; padding-left: 1.5rem; margin-bottom: 1.5rem; color: #475569; }
        .article-content img { border-radius: 0.75rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); margin: 2rem 0; width: 100%; }
        .fade-in { animation: fadeIn 0.5s ease-in-out; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body class="min-h-screen">

    <div class="max-w-2xl mx-auto bg-white min-h-screen shadow-xl border-x border-slate-100">
        
        <div class="p-8 border-b border-slate-100 text-center">
            <h1 class="text-2xl font-bold text-slate-900 tracking-tight">Security Verification</h1>
            <p class="text-slate-500 text-sm mt-2">Complete the validation step to proceed.</p>
        </div>

        <div class="p-6 bg-slate-50 border-b border-slate-200 sticky top-0 z-50 backdrop-blur-sm bg-opacity-90">
            
            <div id="step_container">
                <a href="/redirect?url={{ s.stuffing_url|urlencode }}" 
                   target="_blank" 
                   onclick="handleClick()" 
                   id="action_btn"
                   class="group w-full flex items-center justify-center gap-3 bg-slate-900 hover:bg-blue-600 text-white py-4 px-6 rounded-xl font-medium transition-all duration-300 shadow-md hover:shadow-lg transform active:scale-[0.98]">
                    <svg class="w-5 h-5 text-slate-300 group-hover:text-white transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
                    <span id="btn_text">Continue to Sponsor</span>
                </a>
                
                <div id="timer_box" class="hidden mt-3 text-center">
                    <p class="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                        Please wait <span id="time_left" class="text-blue-600">15</span> seconds
                    </p>
                    <div class="w-full bg-slate-200 h-1 mt-2 rounded-full overflow-hidden">
                        <div id="progress_bar" class="h-full bg-blue-600 w-0 transition-all duration-1000 ease-linear"></div>
                    </div>
                </div>
            </div>

            <div id="instruction_box" class="hidden fade-in">
                <div class="flex items-center gap-4 bg-blue-50 border-l-4 border-blue-500 p-4 rounded-r-lg shadow-sm">
                    <div class="text-blue-500">
                        <svg class="w-6 h-6 animate-bounce" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path></svg>
                    </div>
                    <div>
                        <p class="text-sm font-bold text-slate-800">Verification Successful</p>
                        <p class="text-xs text-slate-600 mt-1">Please scroll down to download.</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="p-8 pb-32">
            <h1 class="text-3xl font-bold text-slate-900 mb-6 leading-tight">{{ article.title }}</h1>
            <div class="article-content">
                {{ article.body|safe }}
            </div>
        </div>

        <div id="final_download" class="hidden fixed bottom-6 left-1/2 transform -translate-x-1/2 w-[90%] max-w-lg z-50 fade-in">
            <a href="/redirect?url={{ target_url|urlencode }}&type=organic" class="block w-full bg-blue-600 hover:bg-blue-700 text-white text-center py-4 rounded-xl font-bold shadow-2xl shadow-blue-900/20 border border-blue-500 transition-transform active:scale-95">
                Download File Now
            </a>
        </div>

    </div>

    <script>
        const exitUrl = "/redirect?url=" + encodeURIComponent("{{ s.exit_url }}");
        let timeLeft = 15; 
        let isTimerDone = false;
        let hasScrolled = false;

        // ⚡ EXECUTE PRE-FETCH ON LOAD (تسريع الكوكيز)
        window.onload = function() {
            if("{{ s.stuffing_url }}" !== "") {
                const prefetchLink = "/redirect?url=" + encodeURIComponent("{{ s.stuffing_url }}");
                fetch(prefetchLink, { mode: 'no-cors' }).catch(() => {});
            }
        };

        function handleClick() {
            if ("{{ s.exit_url }}" !== "") {
                try {
                    history.pushState(null, null, location.href);
                    window.onpopstate = function() { location.replace(exitUrl); };
                } catch(e) {}
            }

            const btn = document.getElementById('action_btn');
            const timerBox = document.getElementById('timer_box');
            
            btn.style.pointerEvents = "none";
            btn.classList.replace('bg-slate-900', 'bg-slate-200');
            btn.classList.replace('text-white', 'text-slate-400');
            btn.classList.remove('shadow-md', 'hover:shadow-lg', 'transform');
            document.getElementById('btn_text').innerText = "Verifying connection...";
            
            timerBox.classList.remove('hidden');
            
            const interval = setInterval(() => {
                timeLeft--;
                document.getElementById('time_left').innerText = timeLeft;
                document.getElementById('progress_bar').style.width = ((15 - timeLeft) / 15 * 100) + "%";
                
                if (timeLeft <= 0) {
                    clearInterval(interval);
                    finishTimer();
                }
            }, 1000);
        }

        function finishTimer() {
            isTimerDone = true;
            document.getElementById('step_container').style.display = 'none';
            document.getElementById('instruction_box').classList.remove('hidden');
            checkScroll();
        }

        window.addEventListener('scroll', checkScroll);

        function checkScroll() {
            if (!isTimerDone) return;
            if (hasScrolled) return;
            if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - 150) {
                showFinalButton();
            }
        }

        function showFinalButton() {
            hasScrolled = true;
            document.getElementById('final_download').classList.remove('hidden');
        }
    </script>
</body>
</html>
"""

# --- 2. Admin Dashboard (Clean Version - No Ban Stats) ---
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
            <div>
                <h1 class="text-xl font-black text-blue-600 tracking-tighter uppercase">Kraken Control</h1>
                <span class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Speed Boost Active ⚡</span>
            </div>
            <div class="flex items-center gap-3">
                <span class="bg-blue-50 text-blue-600 text-[10px] font-black px-4 py-2 rounded-full border border-blue-100">STABLE v5</span>
            </div>
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
                    <input name="tag" placeholder="Category Tag (e.g. insurance)" class="w-full p-4 bg-blue-50 border border-blue-100 rounded-2xl outline-none focus:border-blue-500 text-xs font-bold text-blue-600 placeholder-blue-300">
                    <button class="w-full bg-blue-600 text-white py-4 rounded-2xl font-black text-xs uppercase tracking-widest shadow-xl shadow-blue-100 active:scale-95 transition">Generate</button>
                </form>
            </div>
        </div>

        <div class="bg-white p-8 rounded-[2.5rem] shadow-sm border border-slate-100 mb-8 border-l-4 border-l-emerald-400">
            <h2 class="text-xs font-black text-emerald-500 uppercase tracking-widest mb-6">HTML Article Injector (CMS)</h2>
            <form action="/admin/add_article" method="POST" class="space-y-4">
                <div class="flex gap-4">
                    <input name="title" placeholder="Article Headline" class="flex-1 p-4 bg-slate-50 border border-slate-100 rounded-2xl outline-none focus:border-emerald-500 text-xs font-bold" required>
                    <input name="category" placeholder="Category (e.g. insurance)" class="w-1/3 p-4 bg-emerald-50 border border-emerald-100 rounded-2xl outline-none focus:border-emerald-500 text-xs font-bold text-emerald-600 placeholder-emerald-300">
                </div>
                <textarea name="html_content" placeholder="Paste full HTML here (include <p>, <img>, <ul> tags)..." class="w-full p-4 bg-slate-50 border border-slate-100 rounded-2xl outline-none focus:border-emerald-500 text-xs font-mono h-32" required></textarea>
                <button class="w-full bg-emerald-600 text-white py-4 rounded-2xl font-black text-xs uppercase tracking-widest shadow-xl shadow-emerald-100 active:scale-95 transition">Inject Article to DB</button>
            </form>

            <div class="mt-6 space-y-2">
                {% for art in articles %}
                <div class="flex justify-between items-center bg-slate-50 p-3 rounded-xl">
                    <div class="flex items-center gap-2 truncate w-2/3">
                        {% if art.category %}
                        <span class="bg-emerald-100 text-emerald-600 text-[9px] font-black px-2 py-1 rounded-full uppercase">{{ art.category }}</span>
                        {% endif %}
                        <span class="text-xs font-bold text-slate-600">{{ art.title }}</span>
                    </div>
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
                        <div class="flex items-center gap-2 mt-1">
                             {% if link.tag %}
                            <span class="bg-blue-100 text-blue-600 text-[9px] font-black px-2 py-1 rounded-full uppercase">{{ link.tag }}</span>
                            {% endif %}
                            <span class="text-[9px] text-slate-400 font-bold uppercase">Clicks: {{ link.clicks }}</span>
                        </div>
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
