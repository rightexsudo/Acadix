from flask import Flask, render_template_string, request, send_file
import os
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from youtubesearchpython import VideosSearch
app = Flask(__name__)


def scrape_single_platform(platform_name, search_topic, formatted_topic):
    generated_file = None
    try:
        if platform_name == "youtube":
            videos_search = VideosSearch(search_topic, limit=10)
            results = videos_search.result().get('result', [])
            for video in results:
                title = video.get('title')
                link = video.get('link')
                if title and link:
                    entry = f"{title}\n{link}"
                    if entry not in courses_data:
                        courses_data.append(entry)
        if platform_name == "edraak":
            url = f"https://www.edraak.org/explore/?query={search_topic}"
        elif platform_name == "m3aarif":
            url = f"https://www.m3aarf.com/?search_for={search_topic}"
        elif platform_name == "greatlearning":
            url = f"https://www.mygreatlearning.com/{formatted_topic}/free-courses"
        elif platform_name == "w3schools":
            url = f"https://www.w3schools.com/{search_topic}/index.php"
        elif platform_name == "netacad":
            url = f"https://www.netacad.com/catalogs/learn?search={search_topic}"
        else:
            return None
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        courses_data = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            title = a_tag.get_text(strip=True)
            if len(title) > 3 and search_topic.lower() in title.lower():
                if href.startswith('/'):
                    if platform_name == "edraak":
                        full_url = f"https://www.edraak.org{href}"
                    elif platform_name == "m3aarif":
                        full_url = f"https://www.m3aarf.com{href}"
                    elif platform_name == "w3schools":
                        full_url = f"https://www.w3schools.com{href}"
                    elif platform_name == "netacad":
                        full_url = f"https://www.netacad.com{href}"
                    elif platform_name == "youtube":
                        full_url = f"https://www.youtube.com{href}"
                    else:
                        full_url = f"https://www.mygreatlearning.com{href}"
                else:
                    full_url = href
                
                entry = f"{title}\n{full_url}"
                if entry not in courses_data:
                    courses_data.append(entry)

        if courses_data:
            file_name = f"courses_{platform_name}_{formatted_topic}.txt"
            with open(file_name, "w", encoding="utf-8") as f:
                for c in courses_data:
                    f.write(f"{c}\n\n")
            generated_file = file_name
    except Exception as e:
        pass
        
    return generated_file

def run_scraper(search_topic):
    platforms = ["greatlearning", "edraak", "m3aarif", "w3schools", "youtube"]
    formatted_topic = search_topic.strip().lower().replace(" ", "-")
    
    generated_files = []
    with ThreadPoolExecutor(max_workers=len(platforms)) as executor:
        futures = {executor.submit(scrape_single_platform, p, search_topic, formatted_topic): p for p in platforms}
        for future in as_completed(futures):
            res = future.result()
            if res:
                generated_files.append(res)
                
    return generated_files


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Abril+Fatface&display=swap" rel="stylesheet">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Acadix</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Abril Fatface', cursive;
        }

        body {
            /* الخلفية */
            background-color: #121212;
            background-image: repeating-linear-gradient(
                135deg,
                rgba(255, 255, 255, 0.08) 0px,
                rgba(255, 255, 255, 0.08) 2px,
                transparent 2px, /*حجم تدريخ الخط الرمادي*/
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
            max-width: 520px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        /* حاوية الشعار والأيقونة في الأعلى */
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
            font-size: 38px;
            font-weight: 800;
            letter-spacing: 1.5px;
            color: #ffffff;
            margin-top: -5px;
            text-shadow: 0 4px 15px rgba(0,0,0,0.9);
        }

        .highlight-a {
            color: #c084fc;
            text-shadow: 0 0 12px rgba(192, 132, 252, 0.6);
        }

        /* البطاقة الرئيسية */
        .card-container {
            background: rgba(30, 31, 38, 0.85);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 24px;
            padding: 50px 30px 30px 30px;
            width: 100%;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.7);
            position: relative;
        }

        .theme-btn:hover {
            border-color: #a855f7;
            color: #ffffff;
        }

        /* حقل البحث */
        .search-box {
            margin-top: 15px;
            margin-bottom: 15px;
        }

        .search-input {
            width: 100%;
            padding: 14px 18px;
            background: rgba(18, 18, 22, 0.6);
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

        /* زر البحث والتأكيد المتدرج */
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

        /* صندوق النتائج */
        .results-box {
            margin-top: 25px;
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 14px;
            padding: 18px;
            background: rgba(20, 20, 25, 0.5);
            text-align: right;
        }

        .results-title {
            font-size: 14px;
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 4px;
            text-align: left;
        }

        .results-desc {
            font-size: 12.5px;
            color: #9ca3af;
            margin-bottom: 12px;
        }

        .download-link {
            display: block;
            background: linear-gradient(90deg, #8A40BB 0%, #374151 100%);
            color: #ffffff;
            text-decoration: none;
            padding: 11px 15px;
            border-radius: 8px;
            font-size: 13.5px;
            margin-top: 8px;
            text-align: center;
            border: 1px solid rgba(138, 64, 187, 0.4);
            font-weight: 500;
        }

        .download-link:hover {
            background: linear-gradient(90deg, #9333ea 0%, #4b5563 100%);
        }
    </style>
</head>
<body>

    <div class="main-wrapper">
        <!-- الشعار في الأعلى -->
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

        <!-- البطاقة الأساسية  -->
        <div class="card-container">

            
            <form id="searchForm" method="POST">
                <div class="search-box">
                    <input type="text" id="topicInput" name="topic" class="search-input" placeholder="أبحث عن دورة" required>
                </div>
                <button type="submit" id="submitBtn" class="submit-btn">بحث وتأكيد</button>
            </form>

            <div class="loader" id="loaderText">جاري البحث واستخراج الدورات...</div>

            {% if done %}
                <div class="results-box">
                    <div class="results-title">Acadix Course Search</div>
                    <div class="results-desc">تمت عملية البحث بنجاح!<br>تم استخراج وحفظ الدورات في الملفات التالية:</div>
                    {% for file in files %}
                        <a class="download-link" href="/download/{{ file }}">تحميل الملف: {{ file }}</a>
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
                submitBtn.innerText = 'جاري المعالجة...';
                loader.style.display = 'block';
            }
        });
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    done = False
    files = []
    if request.method == "POST":
        topic = request.form.get("topic")
        files = run_scraper(topic)
        done = True
    return render_template_string(HTML_TEMPLATE, done=done, files=files)

@app.route("/download/<path:filename>")
def download_file(filename):
    file_path = os.path.join(os.getcwd(), filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "الملف غير موجود", 404

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)