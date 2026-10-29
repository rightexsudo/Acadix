# Acadix 
**محرك البحث التعليمي المبتكر بالذكاء الاصطناعي**

منصة ذكية تساعد الطلاب والمطورين والشغوفين على التخطيط للتعلم وإتقان أي مجال أو مهارة من الصفر وحتى الاحتراف خلال ثوانٍ.

**رابط المنصة :**(https://acadix-bc98.onrender.com)

---

## المميزات الاساسية

* **توليد خرائط طريق ذكية (AI Roadmaps):** إنشاء خطة تعليمية مقسمة إلى 3 مراحل رئيسية (مبتدئ، متوسط، متقدم) لكل تخصص بأسلوب دقيق ومباشر.
* **تجميع المصادر التعليمية:** جلب تلقائي لأفضل الكورسات المقترحة والفيديوهات ذات الصلة من **YouTube**، **Coursera**، **Udemy**، **إدراك**، و**معارف**.
* **تحميل خريطة الطريق كصورة:** إمكانية حفظ خارطة الطريق المولدة بنقرة زر واحدة كصورة عالية الجودة (`PNG`).
* **تصميم مرن ومتوافق:** واجهة شخصية عصرية بوضع داكن (Dark Mode) متوافقة بالكامل مع جميع الشاشات والأجهزة (الهواتف المحمولة والكمبيوتر).

---

##  التقنيات المستخدمة

* **Backend:** Python / Flask
* **AI Provider:** Groq API
* **Search Integration:** `youtube-search-python`
* **Frontend:** HTML5, CSS3 (Flexbox/Grid, Responsive Media Queries), JavaScript (`html2canvas`)
* **Hosting:** Render

---

##  التشغيل المحلي (Local Setup)

1. **استكشاف المشروع:**
   ```bash
   git clone https://github.com/rightexsudo/Acadix.git
   cd Acadix
   ```

2. **تثبيت الاعتماديات:**
   ```bash
   pip install -r requirements.txt
   ```

3. **إعداد متغيرات البيئة:**
   قم بإضافة مفتاح `GROQ_API_KEY` الخاص بك:
   ```bash
   export GROQ_API_KEY="your_groq_api_key_here"
   ```

4. **تشغيل التطبيق:**
   ```bash
   python app.py
   ```
   افتح المتصفح على `http://127.0.0.1:5000`.

---

 **الدعم والتواصل:** `support.acadix@protonmail.com`
