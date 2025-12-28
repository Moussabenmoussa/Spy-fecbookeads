# frontend.py
# Corporate Landing Page with Auto-Translation & Dynamic Niches

HOME_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TRAFICOON | Enterprise Traffic Intelligence</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #f8fafc; color: #0f172a; }
        .hero-bg { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: white; }
        .btn-primary { background-color: #2563eb; color: white; transition: all 0.2s; }
        .btn-primary:hover { background-color: #1d4ed8; }
        .input-field { background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); color: white; }
        .input-field:focus { border-color: #3b82f6; outline: none; background: rgba(255,255,255,0.15); }
        .glass-panel { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); }
        /* Hide scrollbar for clean look */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #f1f1f1; }
        ::-webkit-scrollbar-thumb { background: #888; border-radius: 4px; }
    </style>
</head>
<body class="antialiased">

    <nav class="absolute top-0 w-full z-50 p-6">
        <div class="max-w-7xl mx-auto flex justify-between items-center">
            <div class="flex items-center gap-2">
                <img src="YOUR_LOGO_URL_HERE" alt="TRAFICOON" class="h-10 w-auto object-contain">
                <span class="text-white font-bold text-xl tracking-tight hidden" id="text-logo">TRAFICOON</span>
            </div>
            <div class="hidden md:flex gap-8 text-sm font-medium text-slate-300">
                <a href="#features" data-i18n="features">Features</a>
                <a href="#pricing" data-i18n="pricing">Pricing</a>
                <a href="#" class="hover:text-white transition" data-i18n="login">Login</a>
            </div>
        </div>
    </nav>

    <section class="hero-bg min-h-screen flex items-center pt-20 pb-12 relative overflow-hidden">
        <div class="absolute top-0 right-0 w-2/3 h-full bg-blue-600/10 skew-x-12 translate-x-20"></div>

        <div class="max-w-7xl mx-auto px-6 grid md:grid-cols-2 gap-12 items-center relative z-10">
            
            <div>
                <span class="bg-blue-900/50 text-blue-300 text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider border border-blue-800" data-i18n="badge">System v5.0 Stable</span>
                <h1 class="text-5xl md:text-6xl font-extrabold mt-6 leading-tight">
                    <span data-i18n="hero_title">Traffic Intelligence &</span><br>
                    <span class="text-blue-500" data-i18n="hero_subtitle">Filtration Protocol</span>
                </h1>
                <p class="text-slate-400 mt-6 text-lg leading-relaxed max-w-lg" data-i18n="hero_desc">
                    The enterprise-grade solution to sanitize social traffic, eliminate bot activity, and route visitors through a secure organic context.
                </p>

                <div class="mt-10 glass-panel p-6 rounded-2xl shadow-2xl">
                    <form action="/public/shorten" method="POST" class="space-y-4">
                        
                        <div>
                            <label class="text-xs font-bold text-slate-400 uppercase tracking-widest block mb-2" data-i18n="label_url">Target URL</label>
                            <input name="target_url" type="url" required class="input-field w-full p-4 rounded-lg text-sm" placeholder="https://example.com/offer">
                        </div>

                        <div>
                            <label class="text-xs font-bold text-slate-400 uppercase tracking-widest block mb-2" data-i18n="label_niche">Content Category</label>
                            <div class="relative">
                                <select name="category" class="input-field w-full p-4 rounded-lg text-sm appearance-none cursor-pointer text-slate-300">
                                    {% for niche in niches %}
                                    <option value="{{ niche }}" class="bg-slate-800 text-white">{{ niche|upper }}</option>
                                    {% endfor %}
                                </select>
                                <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-slate-400">
                                    <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
                                </div>
                            </div>
                        </div>

                        <button class="btn-primary w-full py-4 rounded-lg font-bold text-sm uppercase tracking-widest shadow-lg hover:shadow-blue-500/30" data-i18n="btn_generate">
                            Generate Secure Link
                        </button>
                        <p class="text-center text-[10px] text-slate-500 mt-3" data-i18n="limit_note">
                            Free Tier Limit: 1 Link / 24 Hours. Login for unlimited access.
                        </p>
                    </form>
                </div>
            </div>

            <div class="hidden md:block relative">
                <div class="border border-slate-700 rounded-xl p-8 bg-slate-900/50 backdrop-blur-md">
                    <div class="flex items-center gap-4 mb-6 border-b border-slate-800 pb-4">
                        <div class="w-3 h-3 rounded-full bg-red-500"></div>
                        <div class="w-3 h-3 rounded-full bg-yellow-500"></div>
                        <div class="w-3 h-3 rounded-full bg-green-500"></div>
                        <span class="text-xs text-slate-500 font-mono ml-auto">status: active</span>
                    </div>
                    <div class="space-y-4 font-mono text-xs">
                        <div class="flex justify-between text-green-400"><span>> Initializing Handshake...</span><span>[OK]</span></div>
                        <div class="flex justify-between text-blue-400"><span>> Spoofing Source Headers...</span><span>[DONE]</span></div>
                        <div class="flex justify-between text-purple-400"><span>> Injecting Contextual Data...</span><span>[DONE]</span></div>
                        <div class="flex justify-between text-slate-500"><span>> Verification Complete.</span></div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <section id="features" class="py-20 bg-white">
        <div class="max-w-7xl mx-auto px-6">
            <div class="text-center mb-16">
                <h2 class="text-3xl font-bold text-slate-900" data-i18n="why_us_title">System Architecture</h2>
                <p class="text-slate-500 mt-2" data-i18n="why_us_sub">Built for high-volume arbitrage and media buying.</p>
            </div>

            <div class="grid md:grid-cols-3 gap-8">
                <div class="p-8 bg-slate-50 rounded-2xl border border-slate-100 hover:shadow-xl transition duration-300">
                    <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-6 text-blue-600">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path></svg>
                    </div>
                    <h3 class="text-xl font-bold text-slate-900 mb-2" data-i18n="feat_1_title">Traffic Sanitization</h3>
                    <p class="text-slate-500 text-sm leading-relaxed" data-i18n="feat_1_desc">Advanced referrer scrubbing technology ensures your traffic source remains anonymous, protecting ad accounts from restriction.</p>
                </div>

                <div class="p-8 bg-slate-50 rounded-2xl border border-slate-100 hover:shadow-xl transition duration-300">
                    <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-6 text-purple-600">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                    </div>
                    <h3 class="text-xl font-bold text-slate-900 mb-2" data-i18n="feat_2_title">Organic Spoofing</h3>
                    <p class="text-slate-500 text-sm leading-relaxed" data-i18n="feat_2_desc">Injects organic search signals into request headers, categorizing social traffic as high-quality search visitors.</p>
                </div>

                <div class="p-8 bg-slate-50 rounded-2xl border border-slate-100 hover:shadow-xl transition duration-300">
                    <div class="w-12 h-12 bg-emerald-100 rounded-lg flex items-center justify-center mb-6 text-emerald-600">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
                    </div>
                    <h3 class="text-xl font-bold text-slate-900 mb-2" data-i18n="feat_3_title">Contextual Routing</h3>
                    <p class="text-slate-500 text-sm leading-relaxed" data-i18n="feat_3_desc">Dynamic content injection based on user category selection to decrease bounce rate and increase engagement.</p>
                </div>
            </div>
        </div>
    </section>

    <section id="pricing" class="py-20 bg-slate-900 text-white">
        <div class="max-w-4xl mx-auto px-6 text-center">
            <h2 class="text-3xl font-bold mb-6 text-amber-400" data-i18n="pro_title">Why Upgrade to Enterprise?</h2>
            <div class="bg-slate-800 p-8 rounded-2xl border border-amber-500/20 shadow-2xl">
                <h3 class="text-2xl font-bold mb-4" data-i18n="pro_sub">Commerce Injection Protocol</h3>
                <p class="text-slate-300 mb-8 leading-relaxed" data-i18n="pro_desc">
                    Unlock our proprietary <strong>Passive Revenue Engine</strong>. Our system automatically embeds global commerce cookies (AliExpress & more) into every visitor session. You earn commissions on future purchases made by your traffic, generating a secondary income stream with zero extra effort.
                </p>
                <button class="bg-amber-500 hover:bg-amber-600 text-slate-900 font-bold py-3 px-8 rounded-full transition" data-i18n="btn_contact">
                    Contact Sales for Access
                </button>
            </div>
        </div>
    </section>

    <footer class="bg-slate-950 py-12 border-t border-slate-900 text-center">
        <p class="text-slate-600 text-sm">© 2025 TRAFICOON Systems. All rights reserved.</p>
    </footer>

    <script>
        const translations = {
            "ar": {
                "features": "المميزات",
                "pricing": "الخطط",
                "login": "دخول",
                "badge": "النظام v5.0 مستقر",
                "hero_title": "ذكاء الترافيك &",
                "hero_subtitle": "بروتوكول الفلترة",
                "hero_desc": "الحل المؤسسي لتنظيف الزيارات الاجتماعية، القضاء على البوتات، وتوجيه الزوار عبر سياق بحث عضوي آمن.",
                "label_url": "رابط الهدف",
                "label_niche": "تصنيف المحتوى",
                "btn_generate": "إنشاء رابط آمن",
                "limit_note": "الحد المجاني: رابط واحد / 24 ساعة. سجل للدخول غير المحدود.",
                "why_us_title": "هيكلية النظام",
                "why_us_sub": "مبني خصيصاً للأربيتراج وأحجام الترافيك العالية.",
                "feat_1_title": "تعقيم الزيارات",
                "feat_1_desc": "تقنية مسح المصدر المتقدمة تضمن بقاء مصدر زياراتك مجهولاً، مما يحمي الحسابات الإعلانية من التقييد.",
                "feat_2_title": "التمويه العضوي",
                "feat_2_desc": "حقن إشارات بحث عضوية في رأس الطلب، لتصنيف زيارات التواصل الاجتماعي كزيارات بحث عالية الجودة.",
                "feat_3_title": "التوجيه السياقي",
                "feat_3_desc": "حقن محتوى ديناميكي بناءً على اختيار تصنيف الزائر لتقليل معدل الارتداد وزيادة التفاعل.",
                "pro_title": "لماذا الترقية للمؤسسات؟",
                "pro_sub": "بروتوكول الحقن التجاري",
                "pro_desc": "افتح محرك الدخل السلبي الحصري. يقوم نظامنا تلقائياً بزرع ملفات تعريف الارتباط التجارية العالمية (AliExpress والمزيد) في جلسة كل زائر. تربح عمولات على المشتريات المستقبلية التي يقوم بها زوارك، مما يولد دخلاً ثانوياً بدون أي جهد إضافي.",
                "btn_contact": "تواصل مع المبيعات"
            }
        };

        // Detect Language
        const userLang = navigator.language || navigator.userLanguage; 
        if (userLang.startsWith("ar")) {
            document.documentElement.lang = "ar";
            document.documentElement.dir = "rtl";
            
            // Apply Translations
            document.querySelectorAll("[data-i18n]").forEach(el => {
                const key = el.getAttribute("data-i18n");
                if (translations["ar"][key]) {
                    el.innerText = translations["ar"][key];
                }
            });
            
            // Adjust styles for RTL
            document.body.style.fontFamily = "'Tahoma', 'Segoe UI', sans-serif";
        }
    </script>
</body>
</html>
"""
