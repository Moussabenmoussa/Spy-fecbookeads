# frontend.py
# V10.1: Client Access Modal + Cleaning Animation + Logo Update

HOME_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TRAFICOON | Enterprise Traffic Intelligence</title>
    <meta name="description" content="Leading source for technology analysis, secure distribution protocols, and financial insights.">
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&family=Merriweather:ital@0;1&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #f8fafc; color: #0f172a; }
        .serif { font-family: 'Merriweather', serif; }
        .mono { font-family: 'JetBrains Mono', monospace; }
        
        /* Button Animation */
        .btn-shine {
            position: relative; overflow: hidden;
        }
        .btn-shine::after {
            content: ''; position: absolute; top: 0; left: -100%; width: 50%; height: 100%;
            background: linear-gradient(to right, rgba(255,255,255,0) 0%, rgba(255,255,255,0.3) 50%, rgba(255,255,255,0) 100%);
            transform: skewX(-25deg); animation: shine 3s infinite;
        }
        @keyframes shine { 100% { left: 200%; } }
        
        /* Modal Animation */
        .modal-enter { opacity: 0; transform: scale(0.95); }
        .modal-enter-active { opacity: 1; transform: scale(1); transition: all 0.3s ease-out; }
        .modal-exit { opacity: 0; transform: scale(0.95); transition: all 0.2s ease-in; }
        
        /* Cleaning Scanner Animation */
        .scanner-line {
            height: 2px; width: 100%; background: #10b981;
            position: absolute; top: 0; left: 0;
            box-shadow: 0 0 10px #10b981;
            animation: scan 1.5s ease-in-out infinite;
        }
        @keyframes scan { 0%, 100% { top: 0%; opacity: 0; } 50% { top: 100%; opacity: 1; } }

        .card-hover:hover { transform: translateY(-4px); box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); }
        .line-clamp-3 { display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
    </style>
</head>
<body class="antialiased flex flex-col min-h-screen">

    <!-- Navbar -->
    <nav class="bg-white/80 backdrop-blur border-b border-slate-200 sticky top-0 z-40">
        <div class="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
            <!-- Logo -->
            <a href="/" class="flex items-center gap-3 group">
                <img src="https://b.top4top.io/p_3649zxju10.png" alt="TRAFICOON" class="h-10 w-auto object-contain transition group-hover:scale-105">
                <span class="font-black text-xl tracking-tighter text-slate-900 hidden md:block">TRAFICOON<span class="text-blue-600">.</span></span>
            </a>
            
            <div class="hidden md:flex gap-6 text-sm font-medium text-slate-600">
                <a href="/" class="hover:text-blue-600 transition {% if not active_category %}text-blue-600 font-bold{% endif %}">Latest</a>
                {% for niche in niches %}
                <a href="/?category={{ niche }}" class="hover:text-blue-600 transition capitalize {% if active_category == niche %}text-blue-600 font-bold{% endif %}">{{ niche }}</a>
                {% endfor %}
            </div>

            <!-- Client Access Button -->
            <button onclick="openModal()" class="btn-shine bg-gradient-to-r from-slate-900 to-slate-800 text-white px-6 py-3 rounded-xl text-xs font-bold uppercase tracking-widest hover:shadow-lg hover:shadow-blue-500/20 transition transform active:scale-95 flex items-center gap-2 border border-slate-700">
                <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path></svg>
                Client Access
            </button>
        </div>
    </nav>

    <!-- Main Content Grid -->
    <main class="flex-grow max-w-7xl mx-auto px-6 py-12 w-full">
        <div class="mb-10 border-b border-slate-200 pb-4 flex justify-between items-end">
            <div>
                <h1 class="text-3xl font-black text-slate-900 mb-2">
                    {% if active_category %}{{ active_category|capitalize }} Archive{% else %}Latest Reports{% endif %}
                </h1>
                <p class="text-slate-500 text-sm">Expert analysis, market trends, and distribution standards.</p>
            </div>
        </div>

        {% if articles %}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {% for art in articles %}
            <article class="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden transition duration-300 card-hover flex flex-col h-full">
                <a href="/read/{{ art._id }}" class="block h-48 overflow-hidden relative group">
                    {% if art.image %}
                    <img src="{{ art.image }}" alt="{{ art.title }}" class="w-full h-full object-cover transition duration-700 group-hover:scale-105" loading="lazy">
                    {% else %}
                    <div class="w-full h-full bg-slate-100 flex items-center justify-center text-slate-300">
                        <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                    </div>
                    {% endif %}
                    <span class="absolute top-4 left-4 bg-white/90 backdrop-blur px-3 py-1 text-[10px] font-bold uppercase tracking-widest rounded-full text-blue-600 shadow-sm">{{ art.category|default('General') }}</span>
                </a>
                <div class="p-6 flex-grow flex flex-col">
                    <h2 class="text-lg font-bold text-slate-900 mb-3 leading-tight hover:text-blue-600 transition"><a href="/read/{{ art._id }}">{{ art.title }}</a></h2>
                    <p class="text-slate-500 text-sm mb-4 line-clamp-3 serif flex-grow leading-relaxed">{{ art.meta_desc|default('Click to read the full report.') }}</p>
                    <div class="pt-4 border-t border-slate-50 flex items-center justify-between text-xs text-slate-400 font-medium">
                        <div class="flex items-center gap-2"><div class="w-2 h-2 bg-green-500 rounded-full"></div><span>{{ art.created_at.strftime('%Y-%m-%d') if art.created_at else 'Recently' }}</span></div>
                        <a href="/read/{{ art._id }}" class="text-blue-600 font-bold hover:underline">Read Report →</a>
                    </div>
                </div>
            </article>
            {% endfor %}
        </div>
        {% else %}
        <div class="text-center py-20 bg-white rounded-3xl border border-dashed border-slate-200 shadow-sm">
            <h3 class="text-lg font-bold text-slate-900">System Initializing</h3>
            <p class="text-slate-500 mt-2">Reports are being indexed.</p>
        </div>
        {% endif %}
    </main>

    <footer class="bg-white border-t border-slate-200 py-12 mt-auto text-center">
        <p class="text-slate-400 text-sm font-medium">© 2025 TRAFICOON Media. All rights reserved.</p>
    </footer>

    <!-- ⚡ SMART MODAL (Popup) ⚡ -->
    <div id="modalBackdrop" class="hidden fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 transition-opacity duration-300">
        <div id="modalContent" class="bg-white w-full max-w-md rounded-2xl shadow-2xl overflow-hidden transform scale-95 transition-transform duration-300 border border-slate-100">
            
            <!-- Modal Header -->
            <div class="bg-slate-50 p-6 border-b border-slate-100 flex justify-between items-center relative">
                <img src="https://b.top4top.io/p_3649zxju10.png" class="h-8 w-auto">
                <button onclick="closeModal()" class="text-slate-400 hover:text-red-500 transition"><svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg></button>
                <div id="scannerLine" class="hidden scanner-line"></div> <!-- The Scanner -->
            </div>

            <!-- Modal Body -->
            <div class="p-8">
                <!-- Step 1: Input Form -->
                <div id="stepForm">
                    <h2 class="text-xl font-black text-slate-900 mb-2">Secure Link Sanitizer</h2>
                    <p class="text-slate-500 text-xs mb-6">Create a whitened, tracking-safe link for your campaigns.</p>
                    
                    <form id="cleanForm" onsubmit="generateLink(event)" class="space-y-4">
                        <div>
                            <label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest block mb-1">Destination URL</label>
                            <input name="target_url" type="url" required class="w-full p-4 bg-slate-50 border border-slate-200 rounded-xl text-sm outline-none focus:border-blue-500 transition" placeholder="https://">
                        </div>
                        <div>
                            <label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest block mb-1">Context Niche</label>
                            <div class="relative">
                                <select name="category" class="w-full p-4 bg-slate-50 border border-slate-200 rounded-xl text-sm outline-none focus:border-blue-500 appearance-none cursor-pointer">
                                    <option value="general">Select Context...</option>
                                    {% for niche in niches %}
                                    <option value="{{ niche }}">{{ niche|upper }}</option>
                                    {% endfor %}
                                </select>
                                <div class="absolute right-4 top-4 pointer-events-none text-slate-400">▼</div>
                            </div>
                        </div>
                        <button type="submit" class="btn-shine w-full bg-blue-600 hover:bg-blue-700 text-white py-4 rounded-xl font-bold text-sm uppercase tracking-widest shadow-lg shadow-blue-200 transition active:scale-95">
                            Sanitize & Generate
                        </button>
                    </form>
                </div>

                <!-- Step 2: Processing Animation -->
                <div id="stepProcess" class="hidden text-center py-8">
                    <div class="w-16 h-16 border-4 border-blue-100 border-t-blue-600 rounded-full animate-spin mx-auto mb-4"></div>
                    <p class="text-sm font-bold text-slate-800 animate-pulse" id="processText">Initializing Handshake...</p>
                    <div class="mt-4 space-y-1">
                        <p class="text-[10px] text-slate-400 mono" id="log1">_</p>
                        <p class="text-[10px] text-slate-400 mono" id="log2"></p>
                    </div>
                </div>

                <!-- Step 3: Result -->
                <div id="stepResult" class="hidden text-center">
                    <div class="w-12 h-12 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-4">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                    </div>
                    <h3 class="text-lg font-bold text-slate-900 mb-2">Link Sanitized Successfully</h3>
                    <p class="text-xs text-slate-500 mb-4">Your link is now ready for safe distribution.</p>
                    
                    <div id="finalLinkContainer" class="bg-slate-50 p-4 rounded-xl border border-slate-200 mb-4 break-all font-mono text-xs text-blue-600"></div>
                    
                    <button onclick="resetModal()" class="text-xs text-slate-400 hover:text-slate-600 font-bold underline">Create Another</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        const backdrop = document.getElementById('modalBackdrop');
        const content = document.getElementById('modalContent');
        
        function openModal() {
            backdrop.classList.remove('hidden');
            setTimeout(() => {
                content.classList.remove('scale-95');
                content.classList.add('scale-100');
            }, 10);
        }

        function closeModal() {
            content.classList.remove('scale-100');
            content.classList.add('scale-95');
            setTimeout(() => {
                backdrop.classList.add('hidden');
                resetModal();
            }, 300);
        }

        function resetModal() {
            document.getElementById('stepForm').classList.remove('hidden');
            document.getElementById('stepProcess').classList.add('hidden');
            document.getElementById('stepResult').classList.add('hidden');
            document.getElementById('scannerLine').classList.add('hidden');
            document.getElementById('cleanForm').reset();
        }

        async function generateLink(e) {
            e.preventDefault();
            const form = e.target;
            const formData = new FormData(form);

            // 1. Show Process
            document.getElementById('stepForm').classList.add('hidden');
            document.getElementById('stepProcess').classList.remove('hidden');
            document.getElementById('scannerLine').classList.remove('hidden');

            // 2. Fake Logs for "Cleaning" Effect
            const logs = ["Scrubbing Referrer Headers...", "Injecting Organic Tags...", "Encrypting Route...", "Finalizing..."];
            const txt = document.getElementById('processText');
            const l1 = document.getElementById('log1');
            const l2 = document.getElementById('log2');

            for (let i = 0; i < logs.length; i++) {
                txt.innerText = logs[i];
                l1.innerText = "> " + logs[i];
                if(i>0) l2.innerText = "> " + logs[i-1] + " [OK]";
                await new Promise(r => setTimeout(r, 800)); // Delay for effect
            }

            // 3. Actual Server Call
            try {
                const response = await fetch('/public/shorten', {
                    method: 'POST',
                    body: formData
                });
                const html = await response.text();
                
                // Extract link from response (simple parsing)
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const linkVal = doc.querySelector('input').value;

                // 4. Show Result
                document.getElementById('stepProcess').classList.add('hidden');
                document.getElementById('scannerLine').classList.add('hidden');
                document.getElementById('stepResult').classList.remove('hidden');
                
                document.getElementById('finalLinkContainer').innerHTML = `
                    <div class="flex items-center gap-2">
                        <input value="${linkVal}" id="resLink" class="bg-transparent w-full outline-none" readonly>
                        <button onclick="navigator.clipboard.writeText('${linkVal}'); alert('Copied!');" class="text-blue-600 font-bold uppercase text-[10px]">Copy</button>
                    </div>
                `;

            } catch (err) {
                alert("Error generating link. Please try again.");
                resetModal();
            }
        }
    </script>
</body>
</html>
"""
