from flask import Flask, render_template_string, request
import os
import urllib.parse
from youtubesearchpython import VideosSearch
from groq import Groq

app = Flask(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_API_KEY)

def get_detailed_ai_roadmap(search_topic , level="مبتدئ"):
    prompt = f"""
    أنت مستشار أكاديمي وخبير تعليمي رفيع المستوى. بصفتك موجهًا ومستشارًا في مجال '{search_topic}', قم بإعداد "خارطة طريق شمولية واحترافية" باللغة العربية مخصصة لشخص مستواه حالياً: [{level}].

    يرجى تنظيم الإجابة باستخدام تنسيق Markdown العادي وواضح (استخدم ## للعناوين و - للنقاط و - [ ] لمربعات الإنجاز):

    **الملخص التنفيذي:**
    - أفكار جوهرية عن أهمية مجال '{search_topic}' لمستوى ({level}).

     **مراحل خارطة الطريق (6 خطوات):**
    1.  المرحلة الأولى: التأسيس والبناء
    2.  المرحلة الثانية: التوسع والتمكين
    3.  المرحلة الثالثة: الاحتراف وسوق العمل

    💡 **ملاحظة:** أضف في كل مرحلة 2-3 مهام قابلة للتحديد كـ Checkbox باستخدام الصيغة: `- [ ] اسم المهارة أو الدورة`
    """

    try:
        print(f"جاري إرسال الطلب إلى Groq AI...")
        
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=4000
        )
        
        content = completion.choices[0].message.content
        if content and len(content.strip()) > 0:
            print("تم توليد خريطة الطريق بنجاح!")
            return content

    except Exception as e:
        print(f"⚠️ خطأ في الاتصال بـ Groq: {str(e)}")
        return "Sorry Eror in backend , plase Send Eror for support.acadix@protonmail.com"

def search_courses(search_topic):
    courses = []
    try:
        videos_search = VideosSearch(search_topic, limit=6)
        search_result = videos_search.result()
        if search_result and 'result' in search_result:
            for video in search_result.get('result', []):
                if video and isinstance(video, dict):
                    title = video.get('title')
                    link = video.get('link')
                    if title and link:
                        courses.append({'platform': 'يوتيوب (YouTube)', 'title': str(title), 'link': str(link)})
    except Exception as e:
        print("YouTube Search Warning:", str(e))

    if not courses:
        encoded_topic = urllib.parse.quote(search_topic)
        courses.append({
            'platform': 'يوتيوب (YouTube)', 
            'title': f"عرض أفضل الفيديوهات والروابط التعليمية لـ '{search_topic}' على يوتيوب", 
            'link': f"https://www.youtube.com/results?search_query={encoded_topic}"
        })

    encoded_topic = urllib.parse.quote(search_topic)
    platforms_search = [
        {'platform': 'منصة مَعارف (M3aarf)', 'title': f"مسارات ودورات '{search_topic}' المتوفرة", 'link': f"https://www.m3aarf.com/?search_for={encoded_topic}"},
        {'platform': 'منصة إدراك (Edraak)', 'title': f"مساقات وبرامج '{search_topic}' المجانية", 'link': f"https://www.edraak.org/explore/?query={encoded_topic}"},
        {'platform': 'كورسيرا (Coursera)', 'title': f"شهادات وبرامج أكاديمية لـ '{search_topic}'", 'link': f"https://www.coursera.org/search?query={encoded_topic}"},
        {'platform': 'يوديمي (Udemy)', 'title': f"أبرز الدورات التدريبية لـ '{search_topic}'", 'link': f"https://www.udemy.com/courses/search/?q={encoded_topic}"}
    ]
    courses.extend(platforms_search)
    return courses

HTML_TEMPLATE = """
<!doctype html>
<html lang="ar" dir="rtl">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Acadix - خارطة طريقك التعليمية</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap" rel="stylesheet" />
    <style>
      :root {
        --bg: #0c0d10;
        --surface: rgba(255, 255, 255, 0.05);
        --border: rgba(255, 255, 255, 0.1);
        --text: #e8e9ee;
        --muted: #9ca3af;
        --violet: #8b5cf6;
        --blue: #3b82f6;
        --green: #22c55e;
        --ease: cubic-bezier(0.2, 0.7, 0.2, 1);
      }

      * { box-sizing: border-box; margin: 0; padding: 0; }
      html, body { background: var(--bg); }
      body {
        font-family: 'Tajawal', Tahoma, Arial, sans-serif;
        color: var(--text);
        line-height: 1.5;
        min-height: 100vh;
        overflow-x: hidden;
      }
      h1, h2, h3, h4 { line-height: 1.2; font-weight: 700; }
      button, input, select { font: inherit; color: inherit; }
      svg { fill: none; stroke: currentColor; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }
      .icon { width: 18px; height: 18px; flex: none; }
      .sr-only { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); opacity: 0; }
      .muted { color: var(--muted); }

      .bg { position: fixed; inset: 0; z-index: -1; overflow: hidden; pointer-events: none; }
      .bg::before {
        content: '';
        position: absolute;
        inset: 0;
        background-image:
          linear-gradient(rgba(255, 255, 255, 0.04) 1px, transparent 1px),
          linear-gradient(90deg, rgba(255, 255, 255, 0.04) 1px, transparent 1px);
        background-size: 48px 48px;
        mask-image: radial-gradient(ellipse at center, #000 30%, transparent 80%);
        -webkit-mask-image: radial-gradient(ellipse at center, #000 30%, transparent 80%);
      }
      .blob {
        position: absolute;
        width: 520px;
        height: 520px;
        border-radius: 50%;
        filter: blur(110px);
        opacity: 0.35;
        animation: pulse 8s ease-in-out infinite;
      }
      .blob-violet { background: var(--violet); top: -120px; right: -120px; }
      .blob-blue { background: var(--blue); bottom: -160px; left: -120px; animation-delay: -4s; }

      .glass {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(18px) saturate(140%);
        -webkit-backdrop-filter: blur(18px) saturate(140%);
        border: 1px solid var(--border);
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.45);
      }

      .app { display: grid; grid-template-columns: 260px 1fr; min-height: 100vh; }

      .sidebar {
        position: sticky;
        top: 0;
        height: 100vh;
        padding: 32px 20px;
        display: flex;
        flex-direction: column;
        gap: 32px;
        border-inline-end: 1px solid var(--border);
        background: rgba(12, 13, 16, 0.6);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
      }
      .logo { display: flex; align-items: center; gap: 12px; font-weight: 700; font-size: 22px; }
      .logo-mark {
        width: 44px;
        height: 44px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(59, 130, 246, 0.2));
        border: 1px solid rgba(139, 92, 246, 0.4);
        border-radius: 12px;
        box-shadow: 0 0 20px rgba(139, 92, 246, 0.35);
        overflow: hidden;
      }
      .logo-mark img { width: 100%; height: 100%; object-fit: cover; border-radius: 10px; }
      .nav { display: flex; flex-direction: column; gap: 8px; }
      .nav-btn {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 16px;
        border-radius: 12px;
        border: 1px solid transparent;
        background: transparent;
        color: var(--muted);
        font-size: 16px;
        font-weight: 500;
        cursor: pointer;
        transition: color 0.3s, background 0.3s, border-color 0.3s, transform 0.3s var(--ease);
      }
      .nav-btn:hover { color: var(--text); background: var(--surface); transform: translateX(-3px); }
      .nav-btn[aria-current='page'] {
        color: #fff;
        background: linear-gradient(90deg, rgba(139, 92, 246, 0.28), rgba(59, 130, 246, 0.08));
        border-color: rgba(139, 92, 246, 0.45);
        box-shadow: 0 0 20px rgba(139, 92, 246, 0.2);
      }
      .sidebar-foot { margin-top: auto; color: var(--muted); font-size: 13px; }

      .main { padding: 48px 56px 80px; min-width: 0; }
      .view { display: none; max-width: 1000px; margin: 0 auto; }
      .view.active { display: block; animation: fadeIn 0.5s ease both; }

      .eyebrow {
        display: inline-flex;
        padding: 6px 14px;
        border-radius: 999px;
        border: 1px solid rgba(139, 92, 246, 0.4);
        background: rgba(139, 92, 246, 0.1);
        color: #c4b5fd;
        font-size: 14px;
      }
      .hero { text-align: center; margin-bottom: 40px; }
      .hero h1 { font-size: clamp(32px, 5vw, 56px); margin: 20px 0 12px; }
      .hero p { color: var(--muted); font-size: 18px; max-width: 620px; margin: 0 auto; }
      .gradient-text {
        background: linear-gradient(90deg, #c4b5fd, #60a5fa);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
      }

      .search {
        display: flex;
        flex-direction: column;
        gap: 12px;
        padding: 12px;
        border-radius: 20px;
        transition: box-shadow 0.4s, border-color 0.4s;
      }
      .search:focus-within {
        border-color: var(--violet);
        box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.6), 0 0 36px rgba(139, 92, 246, 0.55);
      }
      .search-row { display: flex; align-items: center; gap: 12px; padding: 0 12px; color: var(--muted); }
      .search-input {
        flex: 1;
        min-width: 0;
        background: transparent;
        border: none;
        outline: none;
        font-size: 19px;
        padding: 16px 0;
        color: var(--text);
      }
      .search-input::placeholder { color: #8b92a0; }
      .search-controls { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
      .select-wrap select {
        appearance: none;
        background-color: rgba(255, 255, 255, 0.06);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 12px 40px 12px 16px;
        cursor: pointer;
        color: var(--text);
      }
      .select-wrap select option { background: #16171d; color: var(--text); }
      .generate-btn {
        margin-inline-start: auto;
        padding: 14px 26px;
        border-radius: 12px;
        border: none;
        font-weight: 700;
        color: #fff;
        background: linear-gradient(135deg, #7c3aed, #3b82f6);
        box-shadow: 0 10px 30px rgba(124, 58, 237, 0.35);
        cursor: pointer;
        transition: transform 0.25s var(--ease);
      }
      .generate-btn:hover { transform: translateY(-2px); box-shadow: 0 14px 36px rgba(124, 58, 237, 0.5); }

      .tags { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; margin-top: 24px; }
      .tags-inline { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 16px; }
      .tag {
        padding: 8px 16px;
        border-radius: 999px;
        border: 1px solid var(--border);
        background: var(--surface);
        font-size: 15px;
        cursor: pointer;
        color: var(--text);
        transition: transform 0.25s var(--ease), border-color 0.25s;
      }
      .tag:hover { transform: translateY(-3px); border-color: rgba(139, 92, 246, 0.6); }

      .output { margin-top: 48px; }
      .roadmap-box { padding: 32px; border-radius: 20px; background: rgba(255,255,255,0.03); border: 1px solid var(--border); margin-bottom: 32px; }
      .roadmap-box h2 { font-size: 26px; margin-bottom: 16px; color: #c4b5fd; }
      .roadmap-content { white-space: pre-line; line-height: 1.8; font-size: 16px; color: var(--text); }

      .resource-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 20px; margin-top: 20px; }
      .resource {
        padding: 20px;
        border-radius: 16px;
        text-decoration: none;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid var(--border);
        transition: transform 0.3s;
        display: flex;
        flex-direction: column;
        gap: 8px;
      }
      .resource:hover { transform: translateY(-5px); border-color: var(--violet); }
      .resource h4 { font-size: 17px; color: #fff; }
      .resource p { color: var(--muted); font-size: 13px; }

      .category-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 20px; }
      .category { padding: 24px; border-radius: 20px; }
      .category h3 { font-size: 20px; margin-bottom: 12px; color: #c4b5fd; }

      @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
      @keyframes pulse { 0%, 100% { opacity: 0.25; } 50% { opacity: 0.5; } }
    </style>
  </head>
  <body>
    <div class="bg" aria-hidden="true">
      <span class="blob blob-violet"></span>
      <span class="blob blob-blue"></span>
    </div>

    <div class="app">
      <aside class="sidebar">
        <div class="logo">
          <div class="logo-mark">
            <svg viewBox="0 0 500 500" width="100%" height="100%" style="display:block;">
              <defs>
                <linearGradient id="gradA" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#9333ea" />
                  <stop offset="100%" stop-color="#3b82f6" />
                </linearGradient>
              </defs>
              <polygon points="250,30 430,400 320,400 250,230 180,400 70,400" fill="url(#gradA)" opacity="0.9"/>
              <path d="M 310,180 L 370,250 L 350,270" stroke="#a78bfa" stroke-width="24" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
              <circle cx="310" cy="180" r="14" fill="#c084fc"/>
              <circle cx="350" cy="270" r="14" fill="#c084fc"/>
              <polygon points="250,290 330,340 250,390 170,340" fill="#7c3aed"/>
              <rect x="235" y="380" width="30" height="40" fill="#6d28d9"/>
              <path d="M 120,440 Q 250,470 380,440" stroke="#a855f7" stroke-width="16" fill="none" stroke-linecap="round"/>
            </svg>
          </div>
          <span style="background: linear-gradient(90deg, #fff, #c4b5fd); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800;">Acadix</span>
        </div>
        <nav class="nav" aria-label="التنقل الرئيسي">
          <button class="nav-btn" type="button" data-nav="home" aria-current="page">
            <svg class="icon" viewBox="0 0 24 24"><path d="M3 11l9-8 9 8v10a1 1 0 0 1-1 1h-5v-6h-6v6H4a1 1 0 0 1-1-1z" /></svg>
            <span>الرئيسية</span>
          </button>
          <button class="nav-btn" type="button" data-nav="explore">
            <svg class="icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" /><polygon points="16 8 14 14 8 16 10 10 16 8" /></svg>
            <span>الاستكشاف</span>
          </button>
          <button class="nav-btn" type="button" data-nav="library">
            <svg class="icon" viewBox="0 0 24 24"><path d="M4 4h6a4 4 0 0 1 4 4v12a3 3 0 0 0-3-3H4z" /><path d="M20 4h-6a4 4 0 0 0-4 4v12a3 3 0 0 1 3-3h7z" /></svg>
            <span>المكتبة</span>
          </button>
        </nav>
        <p class="sidebar-foot">مجاني بالكامل، بدون تسجيل</p>
      </aside>

      <main class="main">
        <section class="view active" id="view-home">
          <header class="hero">
            <span class="eyebrow">خارطة طريق فورية</span>
            <h1>ماذا تريد أن <span class="gradient-text">تتعلم</span> اليوم؟</h1>
            <p>اكتب أي مهارة أو مجال، واختر مستواك، وستحصل على خارطة طريق واضحة مع مصادر مقترحة.</p>
          </header>

          <!-- تم تصحيح النموذج ليرسل البيانات بشكل صحيح إلى Flask -->
          <form class="search glass" id="search-form" method="POST" autocomplete="off">
            <div class="search-row">
              <svg class="icon" viewBox="0 0 24 24"><circle cx="11" cy="11" r="7" /><path d="M21 21l-4.3-4.3" /></svg>
              <input id="topic-input" name="topic" class="search-input" type="text" maxlength="80" placeholder="مثال: تطوير الويب، الإنجليزية، التصميم..." required />
            </div>
            <div class="search-controls">
              <div class="select-wrap">
                <select id="level-select" name="level">
                  <option value="مبتدئ">مبتدئ</option>
                  <option value="متوسط">متوسط</option>
                  <option value="متقدم">متقدم</option>
                </select>
              </div>
              <button class="generate-btn" type="submit">ولّد خارطة الطريق</button>
            </div>
          </form>

          <div class="tags">
            <button class="tag" type="button" onclick="quickSearch('Python')">Python</button>
            <button class="tag" type="button" onclick="quickSearch('تصميم UI/UX')">تصميم UI/UX</button>
            <button class="tag" type="button" onclick="quickSearch('الذكاء الاصطناعي')">الذكاء الاصطناعي</button>
            <button class="tag" type="button" onclick="quickSearch('التسويق الرقمي')">التسويق الرقمي</button>
            <button class="tag" type="button" onclick="quickSearch('اللغة الإنجليزية')">اللغة الإنجليزية</button>
            <button class="tag" type="button" onclick="quickSearch('تطوير الويب')">تطوير الويب</button>
            <button class="tag" type="button" onclick="quickSearch('الأمن السيبراني')">الأمن السيبراني</button>
            <button class="tag" type="button" onclick="quickSearch('تحليل البيانات')">تحليل البيانات</button>
          </div>

          {% if searched %}
          <div class="output" id="output">
            <div class="roadmap-box glass">
              <h2>خارطة الطريق المقترحة</h2>
              <div class="roadmap-content">{{ roadmap | safe }}</div>
            </div>

            <div class="roadmap-box glass">
              <h2>مصادر تعلم مقترحة</h2>
              <div class="resource-grid">
                {% for course in courses %}
                <a href="{{ course.link }}" target="_blank" class="resource">
                  <h4>{{ course.platform }}</h4>
                  <p>{{ course.title }}</p>
                </a>
                {% endfor %}
              </div>
            </div>
          </div>
          {% endif %}
        </section>

        <section class="view" id="view-explore">
          <header class="section-head">
            <h1>استكشف المجالات</h1>
            <p>اختر مجالاً أو مهارة، وسننشئ لك خارطة طريق جاهزة فوراً.</p>
          </header>
          <div class="category-grid">
            <div class="category glass">
              <h3>البرمجة</h3>
              <div class="tags-inline">
                <button class="tag" type="button" onclick="quickSearch('Python')">Python</button>
                <button class="tag" type="button" onclick="quickSearch('JavaScript')">JavaScript</button>
                <button class="tag" type="button" onclick="quickSearch('تطوير الويب')">تطوير الويب</button>
              </div>
            </div>
            <div class="category glass">
              <h3>التصميم</h3>
              <div class="tags-inline">
                <button class="tag" type="button" onclick="quickSearch('UI/UX')">UI/UX</button>
                <button class="tag" type="button" onclick="quickSearch('تصميم الجرافيك')">تصميم الجرافيك</button>
              </div>
            </div>
            <div class="category glass">
              <h3>الذكاء الاصطناعي</h3>
              <div class="tags-inline">
                <button class="tag" type="button" onclick="quickSearch('تحليل البيانات')">تحليل البيانات</button>
                <button class="tag" type="button" onclick="quickSearch('الذكاء الاصطناعي')">الذكاء الاصطناعي</button>
              </div>
            </div>
          </div>
        </section>

        <section class="view" id="view-library">
          <header class="section-head">
            <h1>مكتبتك</h1>
            <p>المخرجات السابقة والروابط المحفوظة.</p>
          </header>
          <div class="glass" style="padding: 24px; border-radius: 16px; text-align: center; color: var(--muted);">
            مكتبة الحفظ المحلية جاهزة.
          </div>
        </section>
      </main>
    </div>

    <script>
      // التنقل بين الأقسام
      const navButtons = document.querySelectorAll('[data-nav]');
      const views = document.querySelectorAll('.view');

      navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
          navButtons.forEach(b => b.removeAttribute('aria-current'));
          btn.setAttribute('aria-current', 'page');
          const target = btn.getAttribute('data-nav');
          views.forEach(v => {
            v.classList.toggle('active', v.id === `view-${target}`);
          });
        });
      });

      // دالة البحث السريع عند الضغط على الوسوم أو التصنيفات
      function quickSearch(topic) {
        document.getElementById('topic-input').value = topic;
        document.getElementById('search-form').submit();
      }
    </script>
    <script>
  // التنقل بين الأقسام (الرئيسية، الاستكشاف، المكتبة)
  const navButtons = document.querySelectorAll('[data-nav]');
  const views = document.querySelectorAll('.view');

  navButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      navButtons.forEach(b => b.removeAttribute('aria-current'));
      btn.setAttribute('aria-current', 'page');
      const target = btn.getAttribute('data-nav');
      views.forEach(v => {
        v.classList.toggle('active', v.id === `view-${target}`);
      });
      if (target === 'library') {
        renderLibrary();
      }
    });
  });

  // البحث السريع عند الضغط على الوسوم
  function quickSearch(topic) {
    document.getElementById('topic-input').value = topic;
    document.getElementById('search-form').submit();
  }

  // حفظ الخريطة الحالية في المكتبة تلقائياً عند توليدها
  document.addEventListener("DOMContentLoaded", () => {
    const roadmapBox = document.querySelector('.roadmap-content');
    const topicInput = document.getElementById('topic-input');
    
    if (roadmapBox && topicInput && topicInput.value.trim() !== "") {
      const topic = topicInput.value.trim();
      const content = roadmapBox.innerHTML;
      const date = new Date().toLocaleDateString('ar-JO');
      
      let library = JSON.parse(localStorage.getItem('acadix_library') || '[]');
      
      // عدم تكرار نفس الموضوع
      if (!library.some(item => item.topic === topic)) {
        library.unshift({ topic, content, date });
        localStorage.setItem('acadix_library', JSON.stringify(library));
      }
    }
  });

  // دالة عرض الخرائط المحفوظة في صفحة "المكتبة"
  function renderLibrary() {
    const libraryContainer = document.getElementById('library-list');
    if (!libraryContainer) return;

    let library = JSON.parse(localStorage.getItem('acadix_library') || '[]');

    if (library.length === 0) {
      libraryContainer.innerHTML = `
        <div class="glass" style="padding: 32px; border-radius: 16px; text-align: center; color: var(--muted);">
          <h3>مكتبتك فارغة حالياً</h3>
          <p>أي خارطة طريق تولدها ستظهر هنا تلقائياً.</p>
        </div>
      `;
      return;
    }

    let html = '';
    library.forEach((item, index) => {
      html += `
        <div class="glass" style="padding: 20px; border-radius: 16px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
          <div>
            <h3 style="color: #c4b5fd; font-size: 18px; margin-bottom: 4px;">${item.topic}</h3>
            <span style="color: var(--muted); font-size: 13px;">تاريخ التوليد: ${item.date}</span>
          </div>
          <button onclick="deleteItem(${index})" style="background: rgba(239, 68, 68, 0.2); border: 1px solid rgba(239, 68, 68, 0.4); color: #fca5a5; padding: 8px 16px; border-radius: 8px; cursor: pointer;">حذف</button>
        </div>
      `;
    });
    libraryContainer.innerHTML = html;
  }

  // حذف عنصر من المكتبة
  function deleteItem(index) {
    let library = JSON.parse(localStorage.getItem('acadix_library') || '[]');
    library.splice(index, 1);
    localStorage.setItem('acadix_library', JSON.stringify(library));
    renderLibrary();
  }
</script>
  </body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    searched = False
    courses = []
    roadmap = ""
    try:
        if request.method == "POST":
            topic = request.form.get("topic")
            level = request.form.get("level", "مبتدئ")
            if topic:
                roadmap = get_detailed_ai_roadmap(topic, level)
                courses = search_courses(topic)
                searched = True
    except Exception as e:
        print(f"Error: {str(e)}")
        roadmap = "حدث خطأ غير متوقع، يرجى المحاولة مرة أخرى."
        searched = True
    return render_template_string(HTML_TEMPLATE, searched=searched, roadmap=roadmap, courses=courses)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)