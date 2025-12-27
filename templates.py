# templates.py

# --- 1. User Landing Page (Pop-up Blocker Proof) ---
LANDING_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secure Access</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet">
    <style> body { font-family: 'Inter', sans-serif; background: #f1f5f9; } </style>
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
            
            <a href="/redirect?url={{ s.stuffing_url|urlencode }}" 
               target="_blank" 
               onclick="handleClick()" 
               class="block w-full bg-slate-900 hover:bg-slate-800 text-white py-5 rounded-xl font-bold shadow-lg transform transition active:scale-95 flex items-center justify-center gap-2">
                <span>Open Sponsor Page</span>
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
            </a>
            <p class="text-xs text-slate-400 mt-4">Download unlocks in <span id="timer_display" class="font-bold text-slate-600">10</span> seconds after clicking.</p>
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

    </div>

    <script>
        const exitUrl = "/redirect?url=" + encodeURIComponent("{{ s.exit_url }}");
        let timeLeft = 10; 

        function handleClick() {
            // 1. تفعيل مصيدة الرجوع (Back Hijack) - تعمل 100% لأنها بضغطة زر
            if ("{{ s.exit_url }}" !== "") {
                try {
                    history.pushState(null, null, location.href);
                    window.onpopstate = function() {
                        location.replace(exitUrl);
                    };
                } catch(e) {}
            }

            // 2. تغيير واجهة الزر ليعرف المستخدم أننا بدأنا
            // نستخدم setTimeout بسيط لنسمح للرابط الأصلي بالفتح أولاً قبل تغيير الواجهة
            setTimeout(() => {
                const btn = document.querySelector('#step_1 a');
                // لا نخفي الزر بل نغير شكله فقط ليبقى الرابط يعمل
                btn.style.opacity = "0.5";
                btn.style.pointerEvents = "none"; 
                btn.innerText = "Verifying...";
                
                // بدء العداد
                startTimer();
            }, 100);
        }

        function startTimer() {
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
            setTimeout(() => {
                step2.classList.remove('opacity-0', 'translate-y-10');
            }, 50);
        }
    </script>
</body>
</html>
"""

# --- 2. Admin Dashboard (Original) ---
ADMIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Master Control Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
    <style> body { font-family: 'Inter', sans-serif; background: #f8fafc; } </style>
</head>
<body class="p-4 text-slate-800">
    <div class="max-w-2xl mx-auto">
        <header class="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100 mb-6 flex justify-between items-center">
            <h1 class="text-xl font-extrabold text-blue-600 font-mono">Elite_Linker v2.0</h1>
            <span class="text-[10px] font-bold bg-blue-600 text-white px-3 py-1 rounded-full uppercase">Admin Active</span>
        </header>

        <div class="bg-white p-6 rounded-3xl shadow-sm border border-slate-100 mb-6">
            <h2 class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">Global Monetization</h2>
            <form action="/admin/update_settings" method="POST" class="space-y-4">
                <input name="stuffing_url" value="{{ s.stuffing_url }}" placeholder="AliExpress Product Link (Tracking URL)" class="w-full p-4 bg-slate-50 border border-slate-100 rounded-2xl outline-none focus:border-blue-500 text-sm">
                <input name="exit_url" value="{{ s.exit_url }}" placeholder="Exit Ad Link (Adsterra/Tonic)" class="w-full p-4 bg-slate-50 border border-slate-100 rounded-2xl outline-none focus:border-blue-500 text-sm">
                <button class="w-full bg-slate-900 text-white py-4 rounded-2xl font-bold hover:bg-blue-600 transition">Save Global Parameters</button>
            </form>
        </div>

        <div class="bg-white p-6 rounded-3xl shadow-sm border border-slate-100 mb-8">
            <h2 class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">Generate Secure Download</h2>
            <form action="/admin/create_link" method="POST" class="space-y-4">
                <input name="title" placeholder="Display Title (e.g. Premium App)" class="w-full p-4 bg-slate-50 border border-slate-100 rounded-2xl outline-none focus:border-blue-500 text-sm" required>
                <input name="target_url" placeholder="Direct Reward URL (What they get)" class="w-full p-4 bg-slate-50 border border-slate-100 rounded-2xl outline-none focus:border-blue-500 text-sm" required>
                <button class="w-full bg-blue-600 text-white py-4 rounded-2xl font-bold hover:bg-blue-700 shadow-lg shadow-blue-200 transition">Create Asset Link</button>
            </form>
        </div>

        <div class="space-y-4">
            <h2 class="text-xs font-bold text-slate-400 uppercase tracking-widest px-2">Active Assets</h2>
            {% for link in links %}
            <div class="bg-white p-5 rounded-3xl shadow-sm border border-slate-100">
                <div class="flex justify-between items-center mb-3">
                    <span class="font-bold text-slate-800 text-sm">{{ link.title }}</span>
                    <span class="text-[10px] text-blue-500 font-bold">CLICKS: {{ link.clicks }}</span>
                    <a href="/admin/delete/{{ link._id }}" class="text-red-400 hover:text-red-600 text-xs">Delete</a>
                </div>
                <div class="flex items-center gap-2">
                    <input id="url_{{ link._id }}" value="{{ host_url }}v/{{ link.slug }}" class="flex-1 p-3 bg-slate-50 border border-slate-100 rounded-xl text-[10px] font-mono outline-none" readonly>
                    <button onclick="copyLink('url_{{ link._id }}')" class="bg-blue-600 text-white px-4 py-3 rounded-xl text-xs font-bold shadow-md">Copy</button>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    <script>
        function copyLink(id) {
            var copyText = document.getElementById(id); copyText.select();
            document.execCommand("copy"); alert("Link Copied!");
        }
    </script>
</body>
</html>
"""
