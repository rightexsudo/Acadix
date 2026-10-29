from flask import Flask, render_template_string, request
import os
import urllib.parse
from youtubesearchpython import VideosSearch
from groq import Groq

app = Flask(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_API_KEY)

def get_detailed_ai_roadmap(search_topic):
    prompt = f"""
    أنت مستشار أكاديمي وخبير تعليمي رفيع المستوى. بصفتك موجهًا ومستشارًا في مجال '{search_topic}', قم بإعداد "خارطة طريق شمولية واحترافية" باللغة العربية للراغبين في إتقان هذا المجال من الصفر وحتى الاحتراف.

    يرجى تنظيم الإجابة وفق الهيكل التالي وبشكل مباشر وواضح:

    🎯 **الملخص التنفيذي:**
    - أفكار جوهرية عن أهمية مجال '{search_topic}' في سوق العمل والتطبيق العملي.

    🗺️ **مراحل خارطة الطريق (6 خطوات):**
    1. 🟢 المرحلة الأولى: التأسيس والبناء (المبتدئ)
    2. 🟡 المرحلة الثانية: التوسع والتمكين (المتوسط)
    3. 🔴 المرحلة الثالثة: الاحتراف وسوق العمل (المتقدم)
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
            print("✅ تم توليد خريطة الطريق بنجاح!")
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
            'platform': 'يوتيوب (YouTube - بحث مباشر)', 
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
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Acadix</title>
    <link href="https://fonts.googleapis.com/css2?family=Abril+Fatface&display=swap" rel="stylesheet">
    <!-- مكتبة تحويل العناصر إلى صور -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body {
            background-color: #0b0c10;
            background-image: repeating-linear-gradient(135deg, rgba(180, 185, 210, 0.12) 0px, rgba(180, 185, 210, 0.12) 3px, transparent 3px, transparent 14px);
            color: #e2e8f0; display: flex; height: 100vh; overflow: hidden;
        }
        
        .sidebar { width: 270px; background: rgba(14, 15, 20, 0.95); border-left: 1px solid rgba(255,255,255,0.08); display: flex; flex-direction: column; padding: 20px; }
        
        .logo-area { display: flex; align-items: center; margin-bottom: 30px; padding-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.08); }
        .brand-name { font-family: 'Abril Fatface', serif; font-size: 28px; font-weight: 400; color: #fff; letter-spacing: 1px; }
        .brand-name span { color: #c084fc; }

        .nav-links { list-style: none; display: flex; flex-direction: column; gap: 8px; flex-grow: 1; }
        .nav-link { color: #94a3b8; text-decoration: none; padding: 12px 14px; border-radius: 10px; font-size: 14px; display: flex; align-items: center; gap: 10px; transition: 0.2s; cursor: pointer; }
        .nav-link:hover, .nav-link.active { background: rgba(138, 64, 187, 0.2); color: #c084fc; font-weight: 600; }

        .main-content { flex-grow: 1; overflow-y: auto; padding: 30px; display: flex; flex-direction: column; gap: 25px; }
        .main-content::-webkit-scrollbar { width: 6px; }
        .main-content::-webkit-scrollbar-thumb { background: #8A40BB; border-radius: 10px; }
        
        .tab-section { display: none; flex-direction: column; gap: 20px; }
        .tab-section.active-tab { display: flex; }

        .hero-banner { background: linear-gradient(135deg, rgba(138,64,187,0.15), rgba(59,130,246,0.1)); border: 1px solid rgba(255,255,255,0.08); border-radius: 20px; padding: 30px; }
        .hero-title { font-size: 28px; font-weight: 700; color: #fff; margin-bottom: 8px; }
        .hero-title span { color: #c084fc; }
        .hero-desc { font-size: 14px; color: #94a3b8; margin-bottom: 20px; line-height: 1.6; }
        
        .search-box-flex { display: flex; gap: 10px; }
        .search-input { flex-grow: 1; padding: 14px 18px; background: rgba(13, 14, 18, 0.9); border: 1.5px solid #8A40BB; border-radius: 12px; color: #fff; font-size: 15px; outline: none; }
        .search-input:focus { border-color: #c084fc; box-shadow: 0 0 15px rgba(192, 132, 252, 0.3); }
        .submit-btn { padding: 0 24px; background: linear-gradient(135deg, #8A40BB, #3b82f6); color: #fff; border: none; border-radius: 12px; font-weight: 600; cursor: pointer; transition: 0.2s; }
        .submit-btn:hover { opacity: 0.9; }

        .tags-row { display: flex; gap: 8px; margin-top: 12px; flex-wrap: wrap; }
        .tag-pill { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); padding: 6px 12px; border-radius: 20px; font-size: 12px; color: #cbd5e1; cursor: pointer; transition: 0.2s; }
        .tag-pill:hover { background: #8A40BB; color: #fff; border-color: #8A40BB; }

        .ai-roadmap-box { background: rgba(138, 64, 187, 0.08); border: 1px solid rgba(192, 132, 252, 0.25); border-radius: 16px; padding: 20px; }
        .ai-content { font-size: 14px; color: #cbd5e1; line-height: 1.8; white-space: pre-line; }

        .courses-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 12px; margin-top: 15px; }
        .course-card { background: rgba(18, 19, 26, 0.9); border: 1px solid rgba(138, 64, 187, 0.2); border-radius: 12px; padding: 14px; transition: 0.2s; }
        .course-card:hover { border-color: #3b82f6; transform: translateY(-2px); }
        .course-platform { font-size: 11px; color: #3b82f6; font-weight: 600; margin-bottom: 4px; }
        .course-title { font-size: 13px; color: #fff; margin-bottom: 10px; line-height: 1.4; }
        .course-link { display: inline-block; background: #8A40BB; color: white; text-decoration: none; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 600; }
        
        .section-box { background: rgba(22, 23, 30, 0.85); border: 1px solid rgba(255,255,255,0.06); border-radius: 16px; padding: 16px; }
        .section-title { font-size: 14px; font-weight: 600; color: #60a5fa; margin-bottom: 12px; }
    </style>
</head>
<body>

    <!-- القائمة الجانبية -->
    <div class="sidebar">
        <div class="logo-area">
            <div class="brand-name"><span style="color:#c084fc;">A</span>cadix</div>
        </div>
        
        <div class="nav-links">
            <div class="nav-link active" onclick="switchTab('home')"> الرئيسية (Home)</div>
            <div class="nav-link" onclick="switchTab('explore')"> استكشاف (Explore)</div>
            <div class="nav-link" onclick="switchTab('roadmaps')"> خريطة الطرق (Roadmaps)</div>
            <div class="nav-link" onclick="switchTab('library')"> المكتبة (Library)</div>
        </div>
    </div>

    <!-- منطقة المحتوى الرئيسية -->
    <div class="main-content">
        
        <!-- قسم الرئيسية -->
        <div id="home-tab" class="tab-section active-tab">
            <div class="hero-banner">
                <h1 class="hero-title">التعلم المدعوم بالذكاء الاصطناعي <span>يبدأ من هنا</span></h1>
                <p class="hero-desc">Acadix محرك بحث تعليمي ذكي يساعدك على اكتشاف، تعلم، وإتقان أي مجال مع خرائط طريق مخصصة ومصادر مجانية.</p>
                
                <form method="POST" id="searchForm">
                    <div class="search-box-flex">
                        <input type="text" name="topic" class="search-input" placeholder="ما المجال أو المهارة التي ترغب باحترافه اليوم؟" required>
                        <button type="submit" class="submit-btn">بحث وتوليد</button>
                    </div>
                </form>
                
                <div class="tags-row">
                    <span class="tag-pill" onclick="quickSearch('الذكاء الاصطناعي')">الذكاء الاصطناعي</span>
                    <span class="tag-pill" onclick="quickSearch('علوم البيانات')">علوم البيانات</span>
                    <span class="tag-pill" onclick="quickSearch('تطوير الويب')">تطوير الويب</span>
                    <span class="tag-pill" onclick="quickSearch('الأمن السيبراني')">الأمن السيبراني</span>
                    <span class="tag-pill" onclick="quickSearch('تصميم UI/UX')">تصميم UI/UX</span>
                </div>
            </div>

            {% if searched %}
            <div class="ai-roadmap-box" id="roadmapContainer">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid rgba(192, 132, 252, 0.2); padding-bottom: 8px;">
                    <div class="section-title" style="margin-bottom: 0;"> خارطة الطريق التعليمية الشاملة</div>
                    <button onclick="downloadRoadmapAsImage()" style="background: linear-gradient(135deg, #8A40BB, #3b82f6); color: white; border: none; padding: 6px 14px; border-radius: 8px; font-size: 12px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 6px;">
                        تحميل كصورة
                    </button>
                </div>
                <div class="ai-content">{{ roadmap }}</div>
            </div>

            <div>
                <div class="section-title" style="margin-top: 15px;"> مصادر التعلم المباشرة والدورات المقترحة:</div>
                <div class="courses-grid">
                    {% for course in courses %}
                        <div class="course-card">
                            <div class="course-platform">{{ course.platform }}</div>
                            <div class="course-title">{{ course.title }}</div>
                            <a href="{{ course.link }}" target="_blank" class="course-link">الانتقال للمحتوى ↗</a>
                        </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}
        </div>

        <!-- قسم استكشاف -->
        <div id="explore-tab" class="tab-section">
            <div class="section-box">
                <div class="section-title"> استكشاف المجالات الأكثر طلباً</div>
                <div class="courses-grid">
                    <div class="course-card" onclick="quickSearch('برمجة الذكاء الاصطناعي')" style="cursor:pointer;">
                        <div class="course-platform">تكنولوجيا</div>
                        <div class="course-title"> الذكاء الاصطناعي وتعلم الآلة</div>
                    </div>
                    <div class="course-card" onclick="quickSearch('تطوير المواقع Full Stack')" style="cursor:pointer;">
                        <div class="course-platform">برمجة</div>
                        <div class="course-title"> تطوير المواقع التطبيقية الكاملة</div>
                    </div>
                    <div class="course-card" onclick="quickSearch('الأمن السيبراني والختبار الاختراق')" style="cursor:pointer;">
                        <div class="course-platform">أمن المعلومات</div>
                        <div class="course-title"> الأمن السيبراني والحماية</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- قسم خريطة الطرق الجاهزة -->
        <div id="roadmaps-tab" class="tab-section">
            <div class="section-box">
                <div class="section-title"> خرائط طريق تعليمية مقترحة</div>
                <div style="font-size: 13px; color: #cbd5e1; line-height: 1.8;">
                    يمكنك كتابة اسم أي مجال في مربع البحث الرئيسي بالصفحة الرئيسية لتوليد خريطة طريق مخصصة بالذكاء الاصطناعي فوراً.
                </div>
            </div>
        </div>

        <!-- قسم المكتبة -->
        <div id="library-tab" class="tab-section">
            <div class="section-box">
                <div class="section-title"> أفضل المنصات والمصادر العالمية</div>
                <div class="courses-grid">
                    <div class="course-card"><div class="course-platform">منصة عالمية</div><div class="course-title">Coursera</div><a href="https://www.coursera.org" target="_blank" class="course-link">زيارة المنصة ↗</a></div>
                    <div class="course-card"><div class="course-platform">منصة عربية</div><div class="course-title">إدراك (Edraak)</div><a href="https://www.edraak.org" target="_blank" class="course-link">زيارة المنصة ↗</a></div>
                    <div class="course-card"><div class="course-platform">منصة مجانية</div><div class="course-title">Alison</div><a href="https://alison.com" target="_blank" class="course-link">زيارة المنصة ↗</a></div>
                </div>
            </div>
        </div>

    </div>

    <script>
        function switchTab(tabName) {
            document.querySelectorAll('.tab-section').forEach(el => el.classList.remove('active-tab'));
            document.querySelectorAll('.nav-link').forEach(el => el.classList.remove('active'));
            
            document.getElementById(tabName + '-tab').classList.add('active-tab');
            event.currentTarget.classList.add('active');
        }

        function quickSearch(topic) {
            switchTab('home');
            const input = document.querySelector('input[name="topic"]');
            input.value = topic;
            document.getElementById('searchForm').submit();
        }

        function downloadRoadmapAsImage() {
            const roadmapElement = document.getElementById('roadmapContainer');
            const btn = event.target;
            const originalText = btn.innerHTML;
            btn.innerText = 'جاري الإنشاء...';
            
            html2canvas(roadmapElement, {
                backgroundColor: '#12131a',
                scale: 2
            }).then(canvas => {
                const link = document.createElement('a');
                link.download = 'Acadix-Roadmap.png';
                link.href = canvas.toDataURL('image/png');
                link.click();
                btn.innerHTML = originalText;
            }).catch(err => {
                console.error('Error generating image:', err);
                btn.innerHTML = originalText;
                alert('حدث خطأ أثناء تحميل الصورة، يرجى المحاولة مرة أخرى.');
            });
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
            if topic:
                roadmap = get_detailed_ai_roadmap(topic)
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