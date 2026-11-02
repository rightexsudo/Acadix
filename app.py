from flask import Flask, render_template_string, request
import os
import json
import time
import threading
import urllib.parse
from youtubesearchpython import VideosSearch
from groq import Groq, RateLimitError

app = Flask(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_API_KEY)

# ---------- نماذج Groq: سلسلة احتياطية (لكل موديل حصة مجانية مستقلة) ----------
MODELS = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
]
LEVELS = ("مبتدئ", "متوسط", "متقدم")
_lock = threading.Lock()
_resting = {}   # الموديل -> وقت العودة إليه بعد نفاد حصته
_cache = {}     # مفتاح -> (وقت, نص الخريطة)
_hits = {}      # IP -> أوقات الطلبات الجديدة
CACHE_TTL = 6 * 3600

_pop = os.path.join(os.path.dirname(os.path.abspath(__file__)), "popular.json")
try:
    with open(_pop, encoding="utf-8") as f:
        POPULAR = json.load(f)   # خرائط جاهزة للمواضيع الشائعة (بلا استهلاك API)
except Exception:
    POPULAR = {}

def ask_groq(prompt):
    now = time.time()
    for model in MODELS:
        if _resting.get(model, 0) > now:
            continue
        try:
            extra = {"extra_body": {"reasoning_effort": "low"}} if "gpt-oss" in model else {}
            r = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2200,
                **extra,
            )
            text = r.choices[0].message.content
            if text and text.strip():
                return text
        except RateLimitError:
            _resting[model] = now + 600   # يرتاح 10 دقائق
            print(f"حد الاستخدام: {model}")
        except Exception as e:
            print(f"خطأ في {model}: {e}")
    return None

def all_busy():
    now = time.time()
    return all(_resting.get(m, 0) > now for m in MODELS)

def _key(topic, level):
    return f"{topic.strip().lower()}|{level}"

def lookup(topic, level):
    k = _key(topic, level)
    if k in POPULAR:
        return POPULAR[k]
    with _lock:
        hit = _cache.get(k)
        if hit and time.time() - hit[0] < CACHE_TTL:
            return hit[1]
    return None

def generate(topic, level):
    text = get_detailed_ai_roadmap(topic, level)
    if text:
        with _lock:
            if len(_cache) > 500:
                _cache.clear()
            _cache[_key(topic, level)] = (time.time(), text)
    return text

def too_many(ip, limit=6, window=3600):
    now = time.time()
    with _lock:
        recent = [t for t in _hits.get(ip, []) if now - t < window]
        blocked = len(recent) >= limit
        if not blocked:
            recent.append(now)
        _hits[ip] = recent
        if len(_hits) > 5000:
            _hits.clear()
        return blocked

@app.route("/health")
def health():
    return "ok"

def get_detailed_ai_roadmap(search_topic , level="مبتدئ"):
    prompt = f"""
    أنت مستشار أكاديمي وخبير تعليمي رفيع المستوى. بصفتك موجهًا ومستشارًا في مجال '{search_topic}', قم بإعداد "خارطة طريق شمولية واحترافية" باللغة العربية مخصصة لشخص مستواه حالياً: [{level}].

    التزم بهذه البنية بالضبط (Markdown):

    ## الملخص التنفيذي
    - ثلاث نقاط موجزة عن أهمية '{search_topic}' لمستوى ({level}).

    ## المرحلة 1: عنوان قصير
    جملة واحدة تصف المرحلة.
    - [ ] مهمة قصيرة وواضحة
    - [ ] مهمة قصيرة وواضحة

    كرر نفس الشكل للمراحل 2 إلى 4 (تأسيس، توسع، احتراف، سوق العمل)، من 3 إلى 5 مهام لكل مرحلة، ولا تضف أي نص خارج هذه البنية.
    """

    return ask_groq(prompt)

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

HTML_TEMPLATE = r"""
<!doctype html>
<html lang="ar" dir="rtl">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Acadix - خارطة طريقك التعليمية</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Aref+Ruqaa:wght@400;700&family=IBM+Plex+Sans+Arabic:wght@400;500;600&display=swap" rel="stylesheet" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <style>
:root{--bg:#060918;--panel:#0c1230;--line:#232c5c;--text:#ece7d6;--muted:#98a0c4;--gold:#f2c14e;--violet:#7b5cff;--ease:cubic-bezier(.2,.7,.2,1)}
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:var(--bg)}
body{font-family:'IBM Plex Sans Arabic',Tahoma,Arial,sans-serif;color:var(--text);line-height:1.6;min-height:100dvh;overflow-x:hidden}
h1,h2,h3,h4{font-family:'Aref Ruqaa','IBM Plex Sans Arabic',serif;line-height:1.35;font-weight:700}
button,input,select{font:inherit;color:inherit}
svg{fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.icon{width:18px;height:18px;flex:none}
.muted{color:var(--muted)}
:focus-visible{outline:2px solid var(--gold);outline-offset:3px}
.bg{position:fixed;inset:0;z-index:-1;pointer-events:none;background:radial-gradient(ellipse at 80% 0,#1a1450 0,transparent 55%),radial-gradient(ellipse at 10% 100%,#0e2250 0,transparent 50%)}
.bg canvas{position:absolute;inset:0;width:100%;height:100%}
.blob{display:none}
.glass{background:rgba(12,18,48,.72);border:1px solid var(--line);border-radius:18px}
.app{display:grid;grid-template-columns:230px 1fr;min-height:100dvh}
.sidebar{position:sticky;top:0;height:100dvh;padding:30px 18px;display:flex;flex-direction:column;gap:30px;border-inline-end:1px solid var(--line);background:rgba(6,9,24,.7)}
.logo{display:flex;align-items:center;gap:12px;font-size:24px;font-family:'Aref Ruqaa',serif}
.logo-mark{width:42px;height:42px;border:1px solid var(--line);border-radius:12px;overflow:hidden;background:#0c1230}
.nav{display:flex;flex-direction:column;gap:6px}
.nav-btn{display:flex;align-items:center;gap:12px;padding:11px 14px;border-radius:12px;border:1px solid transparent;background:none;color:var(--muted);cursor:pointer;transition:.25s}
.nav-btn:hover{color:var(--text);background:rgba(255,255,255,.04)}
.nav-btn[aria-current=page]{color:var(--gold);border-color:var(--line);background:rgba(242,193,78,.06)}
.sidebar-foot{margin-top:auto;color:var(--muted);font-size:13px}
.main{padding:48px 48px 90px;min-width:0}
.view{display:none;max-width:980px;margin:0 auto}
.view.active{display:block;animation:fi .5s both}
.section-head{margin-bottom:28px}.section-head h1{font-size:34px}.section-head p{color:var(--muted)}
.eyebrow{color:var(--gold);font-size:15px}
.hero{text-align:center;margin:20px 0 36px}
.hero h1{font-size:clamp(36px,6vw,64px);margin:10px 0 14px}
.hero p{color:var(--muted);font-size:18px;max-width:600px;margin:auto}
.gradient-text{color:var(--gold);text-shadow:0 0 28px rgba(242,193,78,.55)}
.search{display:flex;flex-direction:column;gap:10px;padding:12px;transition:.3s}
.search:focus-within{border-color:var(--gold);box-shadow:0 0 40px rgba(242,193,78,.18)}
.search-row{display:flex;align-items:center;gap:12px;padding:0 12px;color:var(--muted)}
.search-input{flex:1;min-width:0;background:none;border:0;outline:0;font-size:19px;padding:14px 0}
.search-input::placeholder{color:#6f78a3}
.search-controls{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.select-wrap select{appearance:none;background:rgba(255,255,255,.05);border:1px solid var(--line);border-radius:12px;padding:11px 16px;cursor:pointer}
.select-wrap select option{background:#0c1230}
.generate-btn{margin-inline-start:auto;padding:13px 26px;border-radius:12px;border:0;font-weight:600;background:var(--gold);color:#1b1500;cursor:pointer;transition:.25s var(--ease)}
.generate-btn:hover{transform:translateY(-2px);box-shadow:0 10px 30px rgba(242,193,78,.35)}
.tags,.tags-inline{display:flex;flex-wrap:wrap;gap:10px}.tags{justify-content:center;margin-top:22px}.tags-inline{margin-top:14px}
.tag{padding:7px 15px;border-radius:999px;border:1px solid var(--line);background:rgba(255,255,255,.03);cursor:pointer;font-size:15px;transition:.25s}
.tag:hover{border-color:var(--gold);color:var(--gold)}
.category-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:18px}
.category{padding:22px}.category h3{font-size:22px;color:var(--gold)}
/* sky */
#sky{margin-top:44px}
.sky-head{display:flex;align-items:center;gap:22px;flex-wrap:wrap;margin-bottom:22px}
.sky-head h2{font-size:clamp(26px,4vw,40px);flex:1;min-width:200px}
.ring{width:96px;height:96px;position:relative;flex:none}
.ring svg{width:100%;height:100%;transform:rotate(-90deg)}
.ring b{position:absolute;inset:0;display:grid;place-items:center;font-size:20px;color:var(--gold)}
.ring circle{stroke-width:5}.ring .tr{stroke:var(--line)}.ring .pg{stroke:var(--gold);transition:stroke-dashoffset .8s var(--ease);filter:drop-shadow(0 0 6px rgba(242,193,78,.7))}
.sum{padding:20px 24px;margin-bottom:22px;color:var(--muted)}.sum li{margin-inline-start:18px}.sum strong{color:var(--text)}
.phases{position:relative;display:flex;flex-direction:column;gap:20px}
.phase{display:grid;grid-template-columns:220px 1fr;gap:8px;padding:20px;position:relative;transition:border-color .5s,box-shadow .5s}
.phase.done{border-color:rgba(242,193,78,.6);box-shadow:0 0 50px rgba(242,193,78,.12)}
.const{width:100%;height:auto;overflow:visible}
.const line{stroke:var(--line);stroke-width:1.5;stroke-dasharray:4 5;transition:.6s}
.const line.on{stroke:var(--gold);stroke-dasharray:none;filter:drop-shadow(0 0 4px var(--gold))}
.const circle{fill:#3a4482;stroke:none;transition:.5s}
.const circle.on{fill:var(--gold);r:7;filter:drop-shadow(0 0 8px var(--gold));animation:tw 3s infinite}
.pname{font-size:13px;color:var(--gold);margin-top:4px;text-align:center}
.phase h3{font-size:24px}.phase .d{color:var(--muted);margin:2px 0 12px}
.task{display:flex;gap:12px;align-items:flex-start;padding:9px 6px;cursor:pointer;border-radius:10px}
.task:hover{background:rgba(255,255,255,.04)}
.task input{appearance:none;width:20px;height:20px;margin-top:4px;border:1.5px solid var(--muted);border-radius:50%;flex:none;display:grid;place-items:center;cursor:pointer;transition:.3s}
.task input:checked{background:var(--gold);border-color:var(--gold);box-shadow:0 0 12px var(--gold)}
.task input:checked+span{color:var(--muted);text-decoration:line-through}
.note{color:var(--muted);font-size:15px;margin-top:6px}
.beacons h3{font-size:26px;margin:36px 0 14px}
.resource-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:14px}
.resource{display:flex;flex-direction:column;gap:6px;padding:16px;border-radius:14px;text-decoration:none;border:1px solid var(--line);background:rgba(12,18,48,.7);transition:.3s}
.resource:hover{transform:translateY(-4px);border-color:var(--gold)}
.resource h4{font-size:17px;color:var(--gold);font-family:'IBM Plex Sans Arabic';font-weight:600}.resource p{font-size:14px;color:var(--muted)}
.tools{display:flex;justify-content:flex-end;margin-bottom:12px}
.err{padding:26px;text-align:center;color:#f4a3a3}
.lib{display:flex;align-items:center;gap:14px;padding:16px 20px;margin-bottom:12px}
.lib div{flex:1}.lib h3{font-size:22px;color:var(--gold)}.lib small{color:var(--muted)}
.lib button{padding:8px 16px;border-radius:10px;border:1px solid var(--line);background:none;cursor:pointer}
.lib .del:hover{border-color:#f87171;color:#f87171}
.loader{position:fixed;inset:0;z-index:50;display:none;place-items:center;background:rgba(6,9,24,.92);text-align:center}
.loader.on{display:grid}
.loader svg{width:min(320px,70vw)}
.loader polyline{stroke:var(--gold);stroke-width:2;stroke-dasharray:420;stroke-dashoffset:420;animation:dr 2.4s ease-in-out infinite}
.loader circle{fill:var(--gold);animation:tw 1.6s infinite}
.loader p{font-family:'Aref Ruqaa',serif;font-size:26px;margin-top:14px}
@keyframes fi{from{opacity:0}to{opacity:1}}
@keyframes tw{50%{opacity:.55}}
@keyframes dr{0%{stroke-dashoffset:420}60%,100%{stroke-dashoffset:0}}
@media(max-width:820px){
.app{display:block}
.sidebar{position:fixed;inset:auto 0 0 0;height:auto;z-index:20;flex-direction:row;padding:8px;border:0;border-top:1px solid var(--line);background:rgba(6,9,24,.94)}
.logo,.sidebar-foot{display:none}.nav{flex-direction:row;flex:1;justify-content:space-around}
.nav-btn{flex-direction:column;gap:2px;padding:6px 14px;font-size:13px}
.main{padding:28px 18px 110px}.phase{grid-template-columns:1fr}.const{max-width:240px;margin:auto}
}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style>
  </head>
  <body>
    <script id="boot" type="application/json">{{ payload | tojson }}</script>
    <div class="loader" id="loader" role="status"><div><svg viewBox="0 0 200 90"><polyline points="10,70 55,30 95,60 140,20 190,50"/><circle cx="10" cy="70" r="4"/><circle cx="55" cy="30" r="4"/><circle cx="95" cy="60" r="4"/><circle cx="140" cy="20" r="4"/><circle cx="190" cy="50" r="4"/></svg><p id="lmsg">نرصد السماء…</p></div></div>
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
            <span class="eyebrow">ارسم سماءك التعليمية</span>
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
            <button class="tag" type="button" onclick="quickSearch('java programming')">java programming</button>
          </div>

          <div id="sky" aria-live="polite"></div>
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
          <div id="library-list"></div>
        </section>
      </main>
    </div>

    <script>
const $=(q,e=document)=>e.querySelector(q), boot=JSON.parse($('#boot').textContent);
const STARS=['سُهيل','الشِّعرى','الدَّبَران','السِّماك','النَّسر الطائر','النَّسر الواقع','ذَنَب الدجاجة','قلب العقرب'];
const el=(t,c,x)=>{const e=document.createElement(t);if(c)e.className=c;if(x!=null)e.textContent=x;return e};
const svg=(t,a={})=>{const e=document.createElementNS('http://www.w3.org/2000/svg',t);for(const k in a)e.setAttribute(k,a[k]);return e};
const store={get(k,d){try{return JSON.parse(localStorage.getItem(k))??d}catch(e){return d}},set(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}};
/* nav */
const views=document.querySelectorAll('.view'),btns=document.querySelectorAll('[data-nav]');
function show(n){if(!$('#view-'+n))n='home';btns.forEach(b=>b.dataset.nav===n?b.setAttribute('aria-current','page'):b.removeAttribute('aria-current'));views.forEach(v=>v.classList.toggle('active',v.id==='view-'+n));if(n==='library')renderLib()}
btns.forEach(b=>b.addEventListener('click',()=>{location.hash=b.dataset.nav}));
addEventListener('hashchange',()=>show(location.hash.slice(1)));
/* starfield */
(function(){const c=document.createElement('canvas'),x=c.getContext('2d');$('.bg').prepend(c);let W,H,S=[],px=0,py=0;
const rs=()=>{const d=devicePixelRatio||1;W=c.width=innerWidth*d;H=c.height=innerHeight*d;S=Array.from({length:Math.min(160,innerWidth/6)},()=>({x:Math.random()*W,y:Math.random()*H,r:(Math.random()*1.3+.3)*d,p:Math.random()*6,z:Math.random()*.8+.2}))};
rs();addEventListener('resize',rs);addEventListener('pointermove',e=>{px=e.clientX/innerWidth-.5;py=e.clientY/innerHeight-.5});
const still=matchMedia('(prefers-reduced-motion:reduce)').matches;
(function f(t){x.clearRect(0,0,W,H);for(const s of S){const a=still?.7:.45+.45*Math.sin(t/900+s.p);x.fillStyle='rgba(236,231,214,'+a+')';x.beginPath();x.arc(s.x-px*30*s.z,s.y-py*30*s.z,s.r,0,7);x.fill()}if(!still&&!document.hidden)requestAnimationFrame(f);else if(!still)setTimeout(()=>requestAnimationFrame(f),500)})(0)})();
/* parse markdown -> structure (no HTML is ever injected) */
function parse(md){const D={sum:[],phases:[],notes:[]};let cur=null,sec='sum';
const clean=t=>t.replace(/`/g,'').replace(/^\s*(\d+[.)]|[-*•])\s+/,'').trim();
for(let raw of md.split('\n')){const l=raw.trim();if(!l)continue;
const h=l.match(/^#{1,4}\s*(.+)$/)||l.match(/^\*\*(.+?)\*\*:?$/);
if(h){const t=h[1].replace(/\*\*/g,'').replace(/:$/,'').trim();
if(/المرحلة|phase|stage/i.test(t)){cur={t:t.replace(/^المرحلة\s*[^:：]*[:：]\s*/,'')||t,d:'',tasks:[]};D.phases.push(cur);sec='p'}
else{sec=D.phases.length?'n':'sum';cur=null}continue}
const m=l.match(/^[-*]\s*\[( |x|X)\]\s*(.+)$/);
if(m){if(!cur){cur={t:'مهام',d:'',tasks:[]};D.phases.push(cur);sec='p'}cur.tasks.push(m[2].replace(/\*\*|`/g,'').trim());continue}
const txt=clean(l).replace(/\*\*/g,'');
if(sec==='p'&&cur){if(!cur.d)cur.d=txt;else cur.tasks.push(txt)}else if(sec==='n')D.notes.push(txt);else D.sum.push(txt)}
return D}
function rng(a){return()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
function hash(s){let h=7;for(const c of s)h=Math.imul(h^c.charCodeAt(0),16777619);return h>>>0}
/* render sky */
function render(data){const box=$('#sky');box.replaceChildren();if(!data.roadmap){const e=el('div','glass err',data.notice||'تعذّر توليد الخارطة الآن. حاول مجدداً، أو راسلنا: support.acadix@protonmail.com');box.append(e);return}
const D=parse(data.roadmap),key='acadix_done:'+data.topic+'|'+data.level,done=new Set(store.get(key,[]));
const total=D.phases.reduce((n,p)=>n+p.tasks.length,0),R=36,C=2*Math.PI*R;
const tools=el('div','tools'),dl=el('button','tag','📷 حفظ كصورة');dl.type='button';dl.onclick=downloadRoadmapImage;tools.append(dl);
const head=el('div','sky-head'),h2=el('h2',null,data.topic),ring=el('div','ring');
const rs=svg('svg',{viewBox:'0 0 80 80'}),tr=svg('circle',{cx:40,cy:40,r:R,class:'tr'}),pg=svg('circle',{cx:40,cy:40,r:R,class:'pg','stroke-dasharray':C,'stroke-dashoffset':C});rs.append(tr,pg);const pct=el('b',null,'0%');ring.append(rs,pct);head.append(h2,ring);
const cap=el('div','sky-cap');cap.id='cap';
box.append(tools,el('div','cap'),head);const cap0=box.lastChild.previousSibling;cap0.remove();
if(D.sum.length){const s=el('div','glass sum'),u=el('ul');D.sum.forEach(x=>u.append(el('li',null,x)));s.append(u);box.append(s)}
const wrap=el('div','phases'),upd=()=>{const n=done.size;const p=total?Math.round(n/total*100):0;pct.textContent=p+'%';pg.setAttribute('stroke-dashoffset',C*(1-p/100));store.set(key,[...done]);wrap.querySelectorAll('.phase').forEach(f=>f.classList.toggle('done',f.querySelectorAll('.task input').length>0&&[...f.querySelectorAll('.task input')].every(i=>i.checked)))};
D.phases.forEach((p,pi)=>{const r=rng(hash(data.topic)+pi*97),n=Math.max(p.tasks.length,3),pts=[];
for(let i=0;i<n;i++)pts.push([14+i*(172/(n-1))+(r()-.5)*10,16+r()*98]);
const card=el('article','phase glass'),side=el('div'),g=svg('svg',{viewBox:'0 0 200 130',class:'const','aria-hidden':'true'}),ls=[],cs=[];
for(let i=0;i<n-1;i++){const l=svg('line',{x1:pts[i][0],y1:pts[i][1],x2:pts[i+1][0],y2:pts[i+1][1]});ls.push(l);g.append(l)}
pts.forEach(q=>{const c=svg('circle',{cx:q[0],cy:q[1],r:4.5});cs.push(c);g.append(c)});
side.append(g,el('div','pname',STARS[(pi+hash(data.topic))%STARS.length]));
const body=el('div'),h3=el('h3',null,'المرحلة '+(pi+1)+': '+p.t);body.append(h3);if(p.d)body.append(el('p','d',p.d));
p.tasks.forEach((t,ti)=>{const id=pi+':'+ti,lb=el('label','task'),cb=el('input');cb.type='checkbox';cb.checked=done.has(id);
const sync=()=>{cs.forEach((c,i)=>c.classList.toggle('on',i<p.tasks.length&&done.has(pi+':'+i)));ls.forEach((l,i)=>l.classList.toggle('on',done.has(pi+':'+i)&&done.has(pi+':'+(i+1))))};
cb.onchange=()=>{cb.checked?done.add(id):done.delete(id);sync();upd()};lb.append(cb,el('span',null,t));body.append(lb);card._s=sync});
card.append(side,body);wrap.append(card);card._s&&card._s()});
box.append(wrap);
if(D.notes.length){const nn=el('div','note');nn.textContent='💡 '+D.notes.join(' · ');box.append(nn)}
const bc=el('div','beacons');bc.append(el('h3',null,'منارات للتعلّم'));const gr=el('div','resource-grid');
(data.courses||[]).forEach(c=>{if(!/^https?:\/\//.test(c.link))return;const a=el('a','resource');a.href=c.link;a.target='_blank';a.rel='noopener noreferrer';a.append(el('h4',null,c.platform),el('p',null,c.title));gr.append(a)});
bc.append(gr);box.append(bc);
card0=null;wrap.querySelectorAll('.phase').forEach(f=>f._s&&f._s());upd();
box.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion:reduce)').matches?'auto':'smooth',block:'start'})}
var card0;
/* library */
function saveLib(d){if(!d.roadmap)return;let L=store.get('acadix_library',[]).filter(x=>!(x.topic===d.topic&&x.level===d.level));L.unshift({topic:d.topic,level:d.level,roadmap:d.roadmap,courses:d.courses,date:new Date().toLocaleDateString('ar-JO')});store.set('acadix_library',L.slice(0,30))}
function renderLib(){const box=$('#library-list');box.replaceChildren();const L=store.get('acadix_library',[]);
if(!L.length){box.append(el('div','glass err','مكتبتك فارغة. أي خارطة تولّدها ستُحفظ هنا تلقائياً.'));box.firstChild.style.color='var(--muted)';return}
L.forEach((it,i)=>{const r=el('div','glass lib'),d=el('div');d.append(el('h3',null,it.topic),el('small',null,it.level+' · '+it.date));
const o=el('button',null,'فتح'),x=el('button','del','حذف');
o.onclick=()=>{location.hash='home';$('#topic-input').value=it.topic;$('#level-select').value=it.level;render(it)};
x.onclick=()=>{L.splice(i,1);store.set('acadix_library',L);renderLib()};r.append(d,o,x);box.append(r)})}
/* forms */
function quickSearch(t){$('#topic-input').value=t;$('#search-form').requestSubmit()}
const msgs=['نرصد السماء…','نصل النجوم بعضها ببعض…','نبحث عن منارات للتعلّم…'];
$('#search-form').addEventListener('submit',()=>{$('#loader').classList.add('on');let i=0;setInterval(()=>{$('#lmsg').textContent=msgs[++i%msgs.length]},2600)});
addEventListener('pageshow',()=>$('#loader').classList.remove('on'));
function downloadRoadmapImage(){const e=$('#sky');if(!e||!window.html2canvas)return;html2canvas(e,{backgroundColor:'#060918',scale:2}).then(c=>{const a=document.createElement('a');a.download='acadix-roadmap.png';a.href=c.toDataURL('image/png');a.click()})}
/* start */
if(boot.searched){$('#topic-input').value=boot.topic||'';$('#level-select').value=boot.level||'مبتدئ';render(boot);saveLib(boot)}
show(location.hash.slice(1)||'home');
</script>
  </body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    searched = False
    courses = []
    roadmap = ""
    topic = ""
    level = "مبتدئ"
    notice = ""
    try:
        if request.method == "POST":
            topic = (request.form.get("topic") or "").strip()[:80]
            level = request.form.get("level", "مبتدئ")
            if level not in LEVELS:
                level = "مبتدئ"
            if topic:
                searched = True
                roadmap = lookup(topic, level)
                if not roadmap:
                    ip = request.headers.get("X-Forwarded-For", "").split(",")[0].strip() or request.remote_addr
                    if too_many(ip):
                        notice = "وصلت إلى حد الخرائط الجديدة هذه الساعة. جرّب موضوعاً من الوسوم الشائعة أو عد لاحقاً."
                    else:
                        roadmap = generate(topic, level)
                        if not roadmap and all_busy():
                            notice = "الخدمة مشغولة الآن بسبب كثرة الطلبات. جرّب بعد دقائق."
                if roadmap:
                    courses = search_courses(topic)
    except Exception as e:
        print(f"Error: {str(e)}")
        roadmap = ""
        searched = True
    payload = {"searched": searched, "topic": topic, "level": level,
               "roadmap": roadmap or "", "courses": courses, "notice": notice}
    return render_template_string(HTML_TEMPLATE, payload=payload)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)