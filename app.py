from flask import Flask, render_template_string, request
import os
import urllib.parse
from youtubesearchpython import VideosSearch
from google import genai

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=GEMINI_API_KEY)

def get_detailed_ai_roadmap(search_topic):
    prompt = f"""
    أنت مستشار أكاديمي وخبير تعليمي رفيع المستوى. بصفتك موجهًا ومستشارًا في مجال '{search_topic}'، قم بإعداد "خارطة طريق شمولية واحترافية" باللغة العربية للراغبين في إتقان هذا المجال من الصفر وحتى الاحتراف.

    يرجى تنظيم الإجابة وفق الهيكل التالي وبشكل مباشر وواضح:

    🎯 **الملخص التنفيذي:**
    - أفكار جوهرية عن أهمية مجال '{search_topic}' في سوق العمل والتطبيق العملي (في سطرين).

    🗺️ **مراحل خارطة الطريق:**
    1. 🟢 **المرحلة الأولى: التأسيس والبناء (المبتدئ):**
       - أهم المفاهيم الأساسية والأدوات التي يجب إتقانها أولاً.
    2. 🟡 **المرحلة الثانية: التوسع والتمكين (المتوسط):**
       - المهارات التطبيقية والأطر التخصصية وطبيعة المشاريع الصغيرة للتدريب.
    3. 🔴 **المرحلة الثالثة: الاحتراف وسوق العمل (المتقدم):**
       - بناء البورتفوليو (المعرض الشخصي)، بناء المشاريع الحقيقية، وأفضل الممارسات المتقدمة.

    💡 **نصيحة ذهبية للنجاح:**
    - نصيحة سريعة ومحفزة للالتزام والاستمرار والاستفادة القصوى من المصادر.
    """

    models_to_try = ['gemini-3.8-flash', 'gemini-1.5-flash', 'gemini-1.5-pro']
    
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            if response and response.text:
                return response.text
        except Exception as e:
            print(f"Failed with {model_name}: {str(e)}")
            continue
            
    return "عذراً، خوادم الذكاء الاصطناعي تشهد ضغطاً مؤقتاً حالياً. يرجى المحاولة بعد قليل أو تصفح الدورات أدناه."

def search_courses(search_topic):
    courses = []
    try:
        videos_search = VideosSearch(search_topic, limit=10)
        search_result = videos_search.result()
        if search_result and 'result' in search_result:
            results = search_result.get('result', [])
            for video in results:
                if video and isinstance(video, dict):
                    title = video.get('title')
                    link = video.get('link')
                    if title and link:
                        courses.append({
                            'platform': 'يوتيوب (YouTube)',
                            'title': str(title),
                            'link': str(link)
                        })
    except Exception as e:
        print("YouTube Search Internal Error Handled:", str(e))

    # 2. توليد روابط بحث للمصادر والمنصات التعليمية الكبرى
    encoded_topic = urllib.parse.quote(search_topic)
    platforms_search = [
        {'platform': 'منصة مَعارف (M3aarf)', 'title': f"مسارات ودورات '{search_topic}' المتوفرة", 'link': f"https://www.m3aarf.com/?search_for={encoded_topic}"},
        {'platform': 'منصة إدراك (Edraak)', 'title': f"مساقات وبرامج '{search_topic}' المجانية", 'link': f"https://www.edraak.org/explore/?query={encoded_topic}"},
        {'platform': 'منصة Alison', 'title': f"دورات وتخصصات مجانية لـ '{search_topic}'", 'link': f"https://alison.com/courses?query={encoded_topic}"},
        {'platform': 'كورسيرا (Coursera)', 'title': f"شهادات وبرامج أكاديمية لـ '{search_topic}'", 'link': f"https://www.coursera.org/search?query={encoded_topic}"},
        {'platform': 'يوديمي (Udemy)', 'title': f"أبرز الدورات التدريبية الشاملة لـ '{search_topic}'", 'link': f"https://www.udemy.com/courses/search/?q={encoded_topic}"},
        {'platform': 'رواق (Rwaq)', 'title': f"مقررات دراسية في '{search_topic}'", 'link': f"https://www.rwaq.org/courses?utf8=✓&query={encoded_topic}"},
        {'platform': 'مايكروسوفت ليرن (Microsoft Learn)', 'title': f"مسارات تعلم تقنية لـ '{search_topic}'", 'link': f"https://learn.microsoft.com/en-us/search/?terms={encoded_topic}"}
    ]
    
    for p in platforms_search:
        courses.append(p)

    return courses

# تصميم واجهة الويب المخصصة للكمبيوتر (Desktop Widescreen UI)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Acadix - AI Educational Search Engine</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Abril+Fatface&display=swap" rel="stylesheet">
    
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body {
            background-color: #0d0e12;
            background-image: repeating-linear-gradient(
                135deg,
                rgba(255, 255, 255, 0.03) 0px,
                rgba(255, 255, 255, 0.03) 2px,
                transparent 2px,
                transparent 10px
            );
            color: #e2e8f0;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            min-height: 100vh;
            padding: 40px 20px;
        }

        .main-wrapper {
            width: 100%;
            max-width: 900px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .brand-header {
            text-align: center;
            margin-bottom: 20px;
        }

        .logo-svg {
            width: 120px;
            height: 95px;
            filter: drop-shadow(0 0 20px rgba(168, 85, 247, 0.4));
        }

        .brand-title {
            font-family: 'Abril Fatface', serif;
            font-size: 48px;
            font-weight: 400;
            letter-spacing: 2px;
            color: #ffffff;
            margin-top: -5px;
            text-shadow: 0 4px 20px rgba(0,0,0,0.9);
        }

        .highlight-a {
            color: #c084fc;
            text-shadow: 0 0 15px rgba(192, 132, 252, 0.6);
        }

        .card-container {
            background: rgba(22, 23, 30, 0.85);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 24px;
            padding: 40px;
            width: 100%;
            box-shadow: 0 30px 60px rgba(0, 0, 0, 0.8), 0 0 30px rgba(138, 64, 187, 0.1);
        }

        .search-box {
            margin-bottom: 20px;
        }

        .search-input {
            width: 100%;
            padding: 16px 20px;
            background: rgba(13, 14, 18, 0.8);
            border: 1.5px solid #8A40BB;
            border-radius: 12px;
            color: #ffffff;
            font-size: 16px;
            outline: none;
            text-align: right;
            box-shadow: inset 0 2px 5px rgba(0,0,0,0.5);
            transition: border-color 0.3s, box-shadow 0.3s;
        }

        .search-input:focus {
            border-color: #c084fc;
            box-shadow: 0 0 15px rgba(192, 132, 252, 0.3), inset 0 2px 5px rgba(0,0,0,0.5);
        }

        .search-input::placeholder {
            color: #64748b;
        }

        .submit-btn {
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #8A40BB 0%, #6b21a8 50%, #3b82f6 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 6px 20px rgba(138, 64, 187, 0.4);
            transition: opacity 0.2s, transform 0.2s;
        }

        .submit-btn:hover {
            opacity: 0.95;
            transform: translateY(-1px);
        }

        .loader {
            display: none;
            text-align: center;
            margin-top: 20px;
            color: #60a5fa;
            font-size: 15px;
            font-weight: 500;
        }

        .ai-roadmap-box {
            background: rgba(138, 64, 187, 0.08);
            border: 1px solid rgba(192, 132, 252, 0.25);
            border-radius: 16px;
            padding: 24px;
            margin-top: 30px;
            text-align: right;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }

        .ai-title {
            font-size: 16px;
            color: #c084fc;
            font-weight: 700;
            margin-bottom: 12px;
            border-bottom: 1px solid rgba(192, 132, 252, 0.15);
            padding-bottom: 8px;
        }

        .ai-content {
            font-size: 14.5px;
            color: #cbd5e1;
            line-height: 1.8;
            white-space: pre-line;
        }

        .results-section {
            margin-top: 30px;
            max-height: 500px;
            overflow-y: auto;
            padding-left: 5px;
            padding-right: 5px;
        }

        .results-section::-webkit-scrollbar {
            width: 6px;
        }

        .results-section::-webkit-scrollbar-track {
            background: rgba(13, 14, 18, 0.5);
            border-radius: 10px;
        }

        .results-section::-webkit-scrollbar-thumb {
            background: #8A40BB;
            border-radius: 10px;
        }

        .section-subtitle {
            font-size: 15px;
            font-weight: 600;
            color: #60a5fa;
            margin-bottom: 15px;
            margin-top: 10px;
            text-align: right;
        }

        .course-card {
            background: rgba(18, 19, 26, 0.9);
            border: 1px solid rgba(138, 64, 187, 0.25);
            border-radius: 14px;
            padding: 16px 20px;
            margin-bottom: 12px;
            text-align: right;
            transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
        }

        .course-card:hover {
            border-color: #3b82f6;
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(59, 130, 246, 0.15);
        }

        .course-platform {
            font-size: 12px;
            color: #3b82f6;
            font-weight: 600;
            margin-bottom: 4px;
        }

        .course-title {
            font-size: 14px;
            color: #ffffff;
            margin-bottom: 10px;
            line-height: 1.5;
        }

        .course-link {
            display: inline-block;
            background: linear-gradient(135deg, #8A40BB 0%, #6b21a8 100%);
            color: white;
            text-decoration: none;
            padding: 6px 14px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 600;
            transition: opacity 0.2s;
        }

        .course-link:hover {
            opacity: 0.9;
        }
    </style>
</head>
<body>

    <div class="main-wrapper">
        <div class="brand-header">
            <svg class="logo-svg" viewBox="0 0 120 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M60 12 L105 32 L60 52 L15 32 Z" stroke="#E2E8F0" stroke-width="4.5" stroke-linejoin="round"/>
                <path d="M28 38 L28 52" stroke="#E2E8F0" stroke-width="3.5" stroke-linecap="round"/>
                <circle cx="28" cy="55" r="3.5" fill="#E2E8F0"/>
                <path d="M35 78 L60 35 L85 78" stroke="#E2E8F0" stroke-width="6.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M42 58 Q62 47 92 51" stroke="#E2E8F0" stroke-width="4.5" stroke-linecap="round"/>
                <path d="M45 67 Q65 56 97 60" stroke="#E2E8F0" stroke-width="3.5" stroke-linecap="round"/>
            </svg>
            <h1 class="brand-title"><span class="highlight-a">A</span>cadix</h1>
        </div>

        <div class="card-container">
            <form id="searchForm" method="POST">
                <div class="search-box">
                    <input type="text" id="topicInput" name="topic" class="search-input" placeholder="ما المجال أو المهارة التي ترغب باحترافه اليوم؟" required>
                </div>
                <button type="submit" id="submitBtn" class="submit-btn">توليد الخريطة الذكية واستعراض المصادر</button>
            </form>

            <div class="loader" id="loaderText">جاري توليد خريطة الطريق الشاملة وجمع الدورات من المصادر العالمية...</div>

            {% if searched %}
                <div class="ai-roadmap-box">
                    <div class="ai-title">✨ خارطة الطريق التعليمية الشاملة من Acadix AI</div>
                    <div class="ai-content">{{ roadmap }}</div>
                </div>

                <div class="results-section">
                    <div class="section-subtitle">📚 أرشيف الدورات ومصادر التعلم المباشرة:</div>
                    {% for course in courses %}
                        <div class="course-card">
                            <div class="course-platform">{{ course.platform }}</div>
                            <div class="course-title">{{ course.title }}</div>
                            <a href="{{ course.link }}" target="_blank" class="course-link">الانتقال للمحتوى ↗</a>
                        </div>
                    {% endfor %}
                </div>
            {% endif %}
        </div>
    </div>

    <script>
        const form = document.getElementById('searchForm');
        const loader = document.getElementById('loaderText');
        const submitBtn = document.getElementById('submitBtn');
        const inputField = document.getElementById('topicInput');

        form.addEventListener('submit', function(e) {
            if(inputField.value.trim() !== "") {
                submitBtn.style.opacity = '0.7';
                submitBtn.disabled = true;
                submitBtn.innerText = 'جاري التحليل والبناء...';
                loader.style.display = 'block';
            }
        });
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
        print(f"CRITICAL ROUTE ERROR: {str(e)}")
        roadmap = "حدث خطأ غير متوقع أثناء معالجة طلبك، يرجى المحاولة مرة أخرى."
        courses = []
        searched = True
        
    return render_template_string(HTML_TEMPLATE, searched=searched, roadmap=roadmap, courses=courses)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)