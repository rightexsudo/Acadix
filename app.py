from flask import Flask, render_template_string, request
import os
import urllib.parse
from youtubesearchpython import VideosSearch
from google import genai

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=GEMINI_API_KEY)

def get_detailed_ai_roadmap(search_topic):
    try:
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

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        print("CRITICAL AI ERROR:", str(e))
        return f"عذراً، تعذر جلب خريطة الطريق حالياً: {str(e)}"

def search_courses(search_topic):
    courses = []
    
    try:
        videos_search = VideosSearch(search_topic, limit=10)
        results = videos_search.result().get('result', [])
        for video in results:
            title = video.get('title')
            link = video.get('link')
            if title and link:
                courses.append({
                    'platform': 'يوتيوب (YouTube)',
                    'title': title,
                    'link': link
                })
    except Exception as e:
        print("YouTube Search Error:", e)

    encoded_topic = urllib.parse.quote(search_topic)
    platforms_search = [
        {'platform': 'منصة مَعارف (M3aarf)', 'title': f"مسارات ودورات '{search_topic}' المتوفرة", 'link': f"https://www.m3aarf.com/?search_for={encoded_topic}"},
        {'platform': 'منصة إدراك (Edraak)', 'title': f"مساقات وبرامج '{search_topic}' المجانية", 'link': f"https://www.edraak.org/explore/?query={encoded_topic}"},
        {'platform': 'منصة Alison', 'title': f"دورات وتخصصات مجانية لـ '{search_topic}'", 'link': f"https://alison.com/courses?query={encoded_topic}"},
        {'platform': 'كورسيرا (Coursera)', 'title': f"شهادات وبرامج أكاديمية لـ '{search_topic}'", 'link': f"https://www.coursera.org/search?query={encoded_topic}"},
        {'platform': 'يوديمي (Udemy)', 'title': f"أبرز الدورات التدريبية الشاملة لـ '{search_topic}'", 'link': f"https://www.udemy.com/courses/search/?q={encoded_topic}"},
        {'platform': 'رواق (Rwaq)', 'title': f"مقررات دراسية في '{search_topic}'", 'link': f"https://www.rwaq.org/courses?utf8=✓&query={encoded_topic}"},
        {'platform': 'مايكروسوفت ليرن (Microsoft Learn)', 'title': f"مسارات تعلم مسارات تقنية لـ '{search_topic}'", 'link': f"https://learn.microsoft.com/en-us/search/?terms={encoded_topic}"}
    ]
    
    for p in platforms_search:
        courses.append(p)

    return courses

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Acadix</title>
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
            background-color: #121212;
            background-image: repeating-linear-gradient(
                135deg,
                rgba(255, 255, 255, 0.08) 0px,
                rgba(255, 255, 255, 0.08) 2px,
                transparent 2px,
                transparent 10px
            );
            color: #ffffff;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }

        .main-wrapper {
            position: relative;
            width: 100%;
            max-width: 720px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .brand-header {
            text-align: center;
            margin-bottom: -22px;
            z-index: 10;
        }

        .logo-svg {
            width: 110px;
            height: 90px;
            filter: drop-shadow(0 0 15px rgba(168, 85, 247, 0.4));
        }

        .brand-title {
            font-family: 'Abril Fatface', serif;
            font-size: 42px;
            font-weight: 400;
            letter-spacing: 1.5px;
            color: #ffffff;
            margin-top: -5px;
            text-shadow: 0 4px 15px rgba(0,0,0,0.9);
        }

        .highlight-a {
            color: #c084fc;
            text-shadow: 0 0 12px rgba(192, 132, 252, 0.6);
        }

        .card-container {
            background: rgba(30, 31, 38, 0.9);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 24px;
            padding: 50px 30px 30px 30px;
            width: 100%;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.8);
        }

        .search-box {
            margin-top: 15px;
            margin-bottom: 15px;
        }

        .search-input {
            width: 100%;
            padding: 14px 18px;
            background: rgba(18, 18, 22, 0.7);
            border: 1.5px solid #8A40BB;
            border-radius: 10px;
            color: #ffffff;
            font-size: 15px;
            outline: none;
            text-align: right;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.3);
        }

        .search-input::placeholder {
            color: #9ca3af;
        }

        .submit-btn {
            width: 100%;
            padding: 14px;
            background: linear-gradient(90deg, #8A40BB 0%, #6b21a8 50%, #4b5563 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(138, 64, 187, 0.3);
            transition: opacity 0.2s;
        }

        .submit-btn:hover {
            opacity: 0.9;
        }

        .loader {
            display: none;
            text-align: center;
            margin-top: 15px;
            color: #c084fc;
            font-size: 14px;
        }

        .ai-roadmap-box {
            background: rgba(138, 64, 187, 0.12);
            border: 1px solid rgba(192, 132, 252, 0.4);
            border-radius: 14px;
            padding: 20px;
            margin-top: 25px;
            text-align: right;
        }

        .ai-title {
            font-size: 15px;
            color: #c084fc;
            font-weight: 700;
            margin-bottom: 10px;
            border-bottom: 1px solid rgba(192, 132, 252, 0.2);
            padding-bottom: 6px;
        }

        .ai-content {
            font-size: 13.5px;
            color: #e2e8f0;
            line-height: 1.7;
            white-space: pre-line;
        }

        .results-section {
            margin-top: 20px;
            max-height: 400px;
            overflow-y: auto;
            padding-right: 5px;
        }

        .section-subtitle {
            font-size: 14px;
            font-weight: 600;
            color: #c084fc;
            margin-bottom: 12px;
            margin-top: 20px;
            text-align: right;
        }

        .course-card {
            background: rgba(20, 20, 25, 0.8);
            border: 1px solid rgba(138, 64, 187, 0.3);
            border-radius: 12px;
            padding: 12px 14px;
            margin-bottom: 10px;
            text-align: right;
            transition: transform 0.2s;
        }

        .course-card:hover {
            border-color: #a855f7;
            transform: translateY(-2px);
        }

        .course-platform {
            font-size: 11px;
            color: #c084fc;
            font-weight: 600;
            margin-bottom: 3px;
        }

        .course-title {
            font-size: 13px;
            color: #ffffff;
            margin-bottom: 6px;
            line-height: 1.4;
        }

        .course-link {
            display: inline-block;
            background: #8A40BB;
            color: white;
            text-decoration: none;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 11.5px;
            font-weight: 500;
        }

        .course-link:hover {
            background: #9333ea;
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
                    <input type="text" id="topicInput" name="topic" class="search-input" placeholder="ما المجال الذي ترغب باحترافه اليوم؟" required>
                </div>
                <button type="submit" id="submitBtn" class="submit-btn">توليد الخريطة الذكية واستعراض المصادر</button>
            </form>

            <div class="loader" id="loaderText">الذكاء الاصطناعي يبني خارطة طريق شمولية ويجمع المصادر...</div>

            {% if searched %}
                <div class="ai-roadmap-box">
                    <div class="ai-title"> خارطة الطريق التعليمية الشاملة من Acadix </div>
                    <div class="ai-content">{{ roadmap }}</div>
                </div>

                <div class="results-section">
                    <div class="section-subtitle"> أرشيف الدورات ومصادر التعلم المباشرة:</div>
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
                submitBtn.innerText = 'جاري التوليد والتحليل...';
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
    if request.method == "POST":
        topic = request.form.get("topic")
        roadmap = get_detailed_ai_roadmap(topic)
        courses = search_courses(topic)
        searched = True
    return render_template_string(HTML_TEMPLATE, searched=searched, roadmap=roadmap, courses=courses)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)