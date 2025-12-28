# frontend.py
# V10: Dynamic Magazine Interface (Real CMS & Corporate Facade)

HOME_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TRAFICOON | Tech & Finance Insights</title>
    <meta name="description" content="Leading source for technology analysis, secure distribution protocols, and financial insights.">
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=Merriweather:ital@0;1&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #f8fafc; color: #0f172a; }
        .serif { font-family: 'Merriweather', serif; }
        .card-hover:hover { transform: translateY(-4px); box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04); }
        .line-clamp-3 { display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
    </style>
</head>
<body class="antialiased flex flex-col min-h-screen">

    <!-- Navbar -->
    <nav class="bg-white border-b border-slate-200 sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
            <a href="/" class="flex items-center gap-2">
                <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-black text-xl">T</div>
                <span class="font-black text-xl tracking-tighter text-slate-900">TRAFICOON<span class="text-blue-600">.</span></span>
            </a>
            <div class="hidden md:flex gap-6 text-sm font-medium text-slate-600">
                <a href="/" class="hover:text-blue-600 transition {% if not active_category %}text-blue-600 font-bold{% endif %}">Latest</a>
                {% for niche in niches %}
                <a href="/?category={{ niche }}" class="hover:text-blue-600 transition capitalize {% if active_category == niche %}text-blue-600 font-bold{% endif %}">{{ niche }}</a>
                {% endfor %}
            </div>
            <a href="#newsletter" class="bg-slate-900 text-white px-4 py-2 rounded-lg text-xs font-bold uppercase tracking-widest hover:bg-slate-800 transition">Subscribe</a>
        </div>
    </nav>

    <!-- Main Content Grid -->
    <main class="flex-grow max-w-7xl mx-auto px-6 py-12 w-full">
        
        <!-- Section Header -->
        <div class="mb-10 border-b border-slate-200 pb-4 flex justify-between items-end">
            <div>
                <h1 class="text-3xl font-black text-slate-900 mb-2">
                    {% if active_category %}
                        {{ active_category|capitalize }} Archive
                    {% else %}
                        Latest Reports
                    {% endif %}
                </h1>
                <p class="text-slate-500 text-sm">Expert analysis, market trends, and distribution standards.</p>
            </div>
        </div>

        <!-- Dynamic Article Grid -->
        {% if articles %}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {% for art in articles %}
            <article class="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden transition duration-300 card-hover flex flex-col h-full">
                <!-- Thumbnail -->
                <a href="/read/{{ art._id }}" class="block h-48 overflow-hidden relative group">
                    {% if art.image %}
                    <img src="{{ art.image }}" alt="{{ art.title }}" class="w-full h-full object-cover transition duration-700 group-hover:scale-105" loading="lazy">
                    {% else %}
                    <div class="w-full h-full bg-slate-100 flex items-center justify-center text-slate-300">
                        <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                    </div>
                    {% endif %}
                    <span class="absolute top-4 left-4 bg-white/90 backdrop-blur px-3 py-1 text-[10px] font-bold uppercase tracking-widest rounded-full text-blue-600 shadow-sm">
                        {{ art.category|default('General') }}
                    </span>
                </a>
                
                <!-- Content -->
                <div class="p-6 flex-grow flex flex-col">
                    <h2 class="text-lg font-bold text-slate-900 mb-3 leading-tight hover:text-blue-600 transition">
                        <a href="/read/{{ art._id }}">{{ art.title }}</a>
                    </h2>
                    <p class="text-slate-500 text-sm mb-4 line-clamp-3 serif flex-grow leading-relaxed">
                        {{ art.meta_desc|default('Click to read the full report and access related resources.') }}
                    </p>
                    
                    <div class="pt-4 border-t border-slate-50 flex items-center justify-between text-xs text-slate-400 font-medium">
                        <div class="flex items-center gap-2">
                            <div class="w-2 h-2 bg-green-500 rounded-full"></div>
                            <span>{{ art.created_at.strftime('%Y-%m-%d') if art.created_at else 'Recently' }}</span>
                        </div>
                        <a href="/read/{{ art._id }}" class="text-blue-600 font-bold hover:underline">Read Report →</a>
                    </div>
                </div>
            </article>
            {% endfor %}
        </div>
        {% else %}
        <!-- Empty State (No Articles Yet) -->
        <div class="text-center py-20 bg-white rounded-3xl border border-dashed border-slate-200 shadow-sm">
            <div class="text-slate-300 mb-4">
                <svg class="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
            </div>
            <h3 class="text-lg font-bold text-slate-900">System Initializing</h3>
            <p class="text-slate-500 mt-2">Our editorial team is currently indexing new reports.<br>Please check back shortly.</p>
        </div>
        {% endif %}

    </main>

    <!-- Footer -->
    <footer class="bg-white border-t border-slate-200 py-12 mt-auto">
        <div class="max-w-7xl mx-auto px-6 text-center">
            <p class="text-slate-400 text-sm font-medium">© 2025 TRAFICOON Media. All rights reserved.</p>
            <div class="flex justify-center gap-6 mt-4 text-xs text-slate-400">
                <a href="#" class="hover:text-blue-600 transition">Privacy Policy</a>
                <a href="#" class="hover:text-blue-600 transition">Terms of Service</a>
                <a href="#" class="hover:text-blue-600 transition">Editorial Standards</a>
            </div>
        </div>
    </footer>

</body>
</html>
"""
