import streamlit as st
from groq import Groq
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import re
import json
import datetime
import zipfile
import io

# ==================== الإعدادات الأولية ====================
# تسجيل خط عربي (اختياري إذا تريد دعم العربية)
# pdfmetrics.registerFont(TTFont('Arabic', 'arial.ttf'))

# إعداد العميل Groq
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.warning("⚠️ يرجى إضافة مفتاح API في secrets.toml")
    client = None

# ==================== هياكتب كتب جاهزة حسب التخصص ====================
BOOK_STRUCTURES = {
    "التسويق الرقمي": [
        "الفصل 1: عقلية البيانات أولاً: كيف يفكر كبار المسوقين",
        "الفصل 2: ثالوث الزيارات: إتقان SEO، الإعلانات المدفوعة، والسوشيال ميديا",
        "الفصل 3: كيمياء التحويل: تحويل الزوار إلى عملاء",
        "الفصل 4: ثورة الاحتفاظ بالعملاء: إبقاء العملاء مدى الحياة",
        "الفصل 5: أنظمة التوسع: أتمتة آلتك التسويقية"
    ],
    "العقارات": [
        "الفصل 1: عقلية المستثمر الطالب",
        "الفصل 2: إيجاد الصفقات في مدينتك الجامعية",
        "الفصل 3: التمويل الإبداعي للصفقات برأس مال صفري",
        "الفصل 4: خطة إطلاق عقار إيجاري في 90 يومًا",
        "الفصل 5: التوسع من 1 إلى 5 عقارات قبل التخرج"
    ],
    "التجارة الإلكترونية": [
        "الفصل 1: إطلاق متجرك الأول في 7 أيام",
        "الفصل 2: استراتيجيات المنتجات الرابحة",
        "الفصل 3: إعلانات فيسبوك التي تبيع فعلاً",
        "الفصل 4: تحسين معدل التحويل إلى 3٪+",
        "الفصل 5: التوسع الدولي والتسليم العالمي"
    ],
    "التمويل الشخصي": [
        "الفصل 1: ميزانية الطالب الذكية",
        "الفصل 2: الاستثمار بمبلغ 100 دولار فقط",
        "الفصل 3: الدخل السلبي للطلاب",
        "الفصل 4: بناء الائتمان أثناء الدراسة",
        "الفصل 5: التخطيط المالي لما بعد التخرج"
    ],
    "مخصص": []  # المستخدم يدخل العناوين بنفسه
}

# ==================== وظائف الذكاء الاصطناعي ====================
def ai_writer(prompt, model="llama-3.3-70b-versatile"):
    """كتابة محتوى متقدم بالذكاء الاصطناعي"""
    if not client:
        return "⚠️ يرجى إعداد مفتاح API أولاً"
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system", 
                    "content": """أنت كاتب غير خيالي من الطراز العالمي بخبرة 20+ سنة.
                    كتابتك يجب أن تكون:
                    1. عملية وتطبيقية: قدم خطوات فعلية يمكن تنفيذها
                    2. غنية بالأمثلة: استخدم دراسات حالة حقيقية بأسماء شركات وأرقام
                    3. هيكلية: استخدم عناوين فرعية، قوائم، وجداول
                    4. محفزة: اكتب بلغة تحفيزية تدعو للعمل
                    5. احترافية: ابتعد عن العبارات الآلية والتكرار
                    
                    تجنب تماماً: "في هذا الفصل"، "سوف نناقش"، "بناءً على طلبك"."""
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=3500,
            top_p=0.9
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ خطأ في الاتصال: {e}"

def clean_text(text):
    """تنظيف النص من العبارات الآلية وتحسين الصياغة"""
    if not text:
        return ""
    
    # إزالة العلامات الزائدة
    t = re.sub(r'\*\*|\#\#\#|```|___|--', '', text)
    
    # استبدال العبارات الآلية
    replacements = {
        r'(?i)in this chapter': '📚 في هذا الفصل ستتعلم',
        r'(?i)we will discuss': '🎯 سنغطي الآن',
        r'(?i)it is important to': '💡 المفتاح هنا هو',
        r'(?i)based on': 'بناءً على',
        r'(?i)as a student': 'كمستثمر مبتدئ',
        r'(?i)however, it is': 'لكن الحقيقة هي',
    }
    
    for pattern, replacement in replacements.items():
        t = re.sub(pattern, replacement, t)
    
    # إضافة فواصل مرئية للعناوين
    t = re.sub(r'Chapter (\d+):', r'\n📖 **الفصل \1:**', t)
    t = re.sub(r'Step (\d+):', r'\n✅ **الخطوة \1:**', t)
    
    return t.strip()

# ==================== توليد المحتوى الاحترافي ====================
def generate_premium_content(niche, target, book_type, addons):
    """توليد كل محتويات الكتاب الاحترافية"""
    
    # 1. عنوان الكتاب (يجب أن يكون مقنعاً للتسويق)
    title_prompt = f"""أنشئ عنوان كتاب من أكثر الكتب مبيعاً حول {niche} للجمهور المستهدف: {target}.
    
    متطلبات العنوان:
    1. استخدم كلمات قوية (إتقان، سر، نظام، نهائي، ثوري)
    2. حدد الفائدة بوضوح (زيادة الإيرادات، توفير الوقت، تحقيق الحرية المالية)
    3. كن محدداً (في 90 يوماً، بـ 100 دولار، بدون خبرة)
    4. الشكل: العنوان الرئيسي: العنوان الفرعي
    
    أمثلة جيدة:
    - "سيادة البيانات: نظام الطالب لتحقيق 10,000 دولار شهرياً من العقارات"
    - "متحكم التحويل: خطة 30 يوماً لتحويل 3٪ من زوار موقعك"
    - "التمويل الذكي: كيف أحقق دخلاً سلبياً وأنا أدرس"
    
    اختر أفضل عنوان واحد فقط:"""
    
    title_response = ai_writer(title_prompt, "llama-3.3-70b-versatile")
    title_lines = title_response.split('\n')
    main_title = title_lines[0].strip()
    subtitle = title_lines[1].strip() if len(title_lines) > 1 else f"دليل {target} لتحقيق النجاح في {niche}"
    
    # 2. المقدمة القوية
    intro_prompt = f"""اكتب مقدمة قوية لكتاب بعنوان: "{main_title}: {subtitle}"
    
    الجمهور المستهدف: {target}
    نوع الكتاب: {book_type}
    
    هيكل المقدمة:
    1. افتتح بقصة أو إحصائية صادمة (مشكلة يواجهها القارئ)
    2. قدم الحل الذي يوفره الكتاب (الوعد الرئيسي)
    3. صف التحول الذي سيحصل عليه القارئ (قبل/بعد)
    4. اذكر الفصول الرئيسية بإيجاز
    5. أنهِ بدعوة للعمل وتحفيزية
    
    الطول: 400-500 كلمة
    النبرة: تحفيزية، مباشرة، وواعدة"""
    
    introduction = ai_writer(intro_prompt)
    
    # 3. الفصول حسب الهيكل المختار
    chapters = []
    chapter_topics = BOOK_STRUCTURES.get(niche, [f"الفصل {i}" for i in range(1, 6)])
    
    for i, topic in enumerate(chapter_topics, 1):
        chapter_prompt = f"""اكتب محتوى كاملاً {topic} لكتاب بعنوان: "{main_title}"
        
        الجمهور: {target}
        
        الهيكل المطلوب بالضبط:
        
        ## 📖 المبدأ الأساسي
        [اشرح الفكرة المركزية باختصار]
        
        ## 📊 دراسة حالة واقعية: [اسم شركة حقيقية]
        - **قبل:** [رقم أو حالة قبل التطبيق]
        - **الإجراء:** [ما فعلوه بالضبط]
        - **بعد:** [النتيجة بأرقام حقيقية]
        - **الدرس المستفاد:** [خلاصة عملية]
        
        ## 🛠️ خطة التنفيذ خطوة بخطوة
        1. [إجراء عملي 1]
        2. [إجراء عملي 2] 
        3. [إجراء عملي 3]
        
        ## 📝 قالب العمل: [اسم القالب]
        [أنشئ قالباً قابلاً للتعبئة]
        
        ## ⚠️ الأخطاء الشائعة التي يجب تجنبها
        - [الخطأ 1 + كيف تتجنبه]
        - [الخطأ 2 + البديل الأفضل]
        
        ## 🚀 خطة عملك لـ 72 ساعة القادمة
        ✓ الساعة 0-24: [مهمة محددة]
        ✓ الساعة 25-48: [مهمة محددة] 
        ✓ الساعة 49-72: [مهمة محددة]
        
        الطول: 800-1200 كلمة"""
        
        content = ai_writer(chapter_prompt)
        
        # إضافة المواد المكافئة إذا طلب المستخدم
        bonuses_text = ""
        if "قوالب" in addons:
            template_prompt = f"""أنشئ قالباً قابلاً للتعبئة لـ {topic}
            القالب يجب أن يكون:
            1. عملياً واستخدامه مباشر
            2. يحتوي على حقول للتعبئة
            3. مصمم لتحقيق نتيجة محددة"""
            template = ai_writer(template_prompt)
            bonuses_text += f"\n\n📝 **قالب العمل:**\n{template}"
        
        if "اختبارات" in addons:
            quiz_prompt = f"""أنشئ اختباراً قصيراً (3 أسئلة) لـ {topic}
            كل سؤال يجب أن يكون:
            1. عملياً وذا صلة مباشرة
            2. متعدد الخيارات
            3. مع شرح للإجابة الصحيحة"""
            quiz = ai_writer(quiz_prompt)
            bonuses_text += f"\n\n🧠 **اختبار الفصل:**\n{quiz}"
        
        chapters.append({
            "number": i,
            "title": topic,
            "content": clean_text(content + bonuses_text)
        })
    
    # 4. المواد المكافئة الإضافية
    bonuses = []
    
    if "خطة التنفيذ" in addons:
        plan_prompt = f"""أنشئ خطة تنفيذ شهرية للكتاب "{main_title}"
        
        الخطة يجب أن تحتوي:
        1. الأسبوع 1: [3 مهام محددة]
        2. الأسبوع 2: [3 مهام محددة]
        3. الأسبوع 3: [3 مهام محددة] 
        4. الأسبوع 4: [3 مهام محددة]
        
        كل مهمة يجب أن تكون:
        - قابلة للتنفيذ
        - محددة الزمن
        - قابلة للقياس"""
        bonus_plan = ai_writer(plan_prompt)
        bonuses.append(("📅 خطة التنفيذ الشهرية", bonus_plan))
    
    if "قائمة المراجعة" in addons:
        checklist_prompt = f"""أنشئ قائمة مراجعة شاملة للتنفيذ للكتاب "{main_title}"
        
        القائمة يجب أن تحتوي 20 نقطة:
        10 نقطة للبداية
        7 نقطة للتوسع
        3 نقطة للاستمرارية
        
        كل نقطة يجب أن تكون إجراءً محدداً"""
        bonus_checklist = ai_writer(checklist_prompt)
        bonuses.append(("✅ قائمة المراجعة الشاملة", bonus_checklist))
    
    # 5. صفحة المبيعات التلقائية
    sales_page = generate_sales_page(main_title, subtitle, chapters, target, niche, addons)
    
    return {
        "title": main_title,
        "subtitle": subtitle,
        "introduction": clean_text(introduction),
        "chapters": chapters,
        "bonuses": bonuses,
        "sales_page": sales_page,
        "metadata": {
            "niche": niche,
            "target": target,
            "type": book_type,
            "addons": addons,
            "generated_date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "word_count": sum(len(ch['content'].split()) for ch in chapters)
        }
    }

# ==================== إنشاء PDF احترافي ====================
def create_professional_pdf(content_data, output_path="premium_ebook.pdf"):
    """إنشاء ملف PDF احترافي بكل الميزات"""
    
    # إعداد مستند PDF
    doc = SimpleDocTemplate(
        output_path,
        pagesize=(595.27, 841.89),  # A4
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # أنماط التنسيق
    styles = getSampleStyleSheet()
    
    # أنماط مخصصة
    title_style = ParagraphStyle(
        'MainTitle',
        parent=styles['Title'],
        fontSize=28,
        textColor=colors.HexColor('#1a237e'),
        alignment=TA_CENTER,
        leading=34,
        spaceAfter=15,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'SubTitle',
        parent=styles['Italic'],
        fontSize=16,
        textColor=colors.HexColor('#455a64'),
        alignment=TA_CENTER,
        leading=20,
        spaceAfter=40
    )
    
    chapter_style = ParagraphStyle(
        'ChapterTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#0d47a1'),
        spaceBefore=30,
        spaceAfter=15,
        fontName='Helvetica-Bold',
        borderPadding=10,
        borderColor=colors.HexColor('#bbdefb'),
        borderWidth=1,
        backColor=colors.HexColor('#e3f2fd')
    )
    
    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        alignment=TA_JUSTIFY,
        spaceAfter=8
    )
    
    box_style = ParagraphStyle(
        'ActionBox',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.white,
        backColor=colors.HexColor('#1565c0'),
        borderPadding=10,
        borderColor=colors.HexColor('#0d47a1'),
        borderWidth=1
    )
    
    # بناء المحتوى
    story = []
    
    # 1. صفحة الغلاف
    story.append(Spacer(1, 180))
    story.append(Paragraph(content_data["title"], title_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph(content_data["subtitle"], subtitle_style))
    story.append(Spacer(1, 100))
    story.append(Paragraph("نُشر بواسطة Content Master Pro", 
                          ParagraphStyle('Publisher', parent=styles['Italic'], fontSize=12, alignment=TA_CENTER)))
    story.append(PageBreak())
    
    # 2. صفحة حقوق النشر
    story.append(Paragraph("إشعار حقوق النشر", chapter_style))
    story.append(Paragraph(f"""
    <b>العنوان:</b> {content_data['title']}<br/>
    <b>الطبعة:</b> الأولى {datetime.datetime.now().year}<br/>
    <b>حقوق النشر © {datetime.datetime.now().year} Content Master Pro</b><br/><br/>
    
    جميع الحقوق محفوظة. لا يجوز إعادة إنتاج أي جزء من هذا الكتاب أو تخزينه في نظام استرجاع أو نقله بأي شكل أو بأي وسيلة، 
    إلكترونية أو ميكانيكية أو تصويرية أو تسجيلية أو غير ذلك، دون الحصول على إذن كتابي مسبق من الناشر.<br/><br/>
    
    هذا الكتاب مقدم لأغراض إعلامية فقط. لا يقدم المؤلف أو الناشر أي ضمانات، صريحة أو ضمنية، ولا يتحملان أي مسؤولية 
    عن أي أخطاء أو سهو، أو عن النتائج التي قد تتحقق من استخدام المعلومات الواردة هنا.<br/><br/>
    
    <i>تم إنشاؤه في {datetime.datetime.now().strftime('%Y-%m-%d')}</i>
    """, body_style))
    story.append(PageBreak())
    
    # 3. المقدمة
    story.append(Paragraph("المقدمة", chapter_style))
    intro_paragraphs = content_data["introduction"].split('\n\n')
    for para in intro_paragraphs:
        if para.strip():
            story.append(Paragraph(para, body_style))
            story.append(Spacer(1, 8))
    story.append(PageBreak())
    
    # 4. الفصول
    for chapter in content_data["chapters"]:
        story.append(Paragraph(f"{chapter['title']}", chapter_style))
        
        # معالجة المحتوى وإضافة تنسيق خاص
        content = chapter['content']
        
        # اكتشاف وتنسيق القوائم
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('✅') or line.startswith('📝') or line.startswith('🧠'):
                # عناوين خاصة
                story.append(Paragraph(f"<b>{line}</b>", 
                                     ParagraphStyle('SpecialHeader', parent=body_style, textColor=colors.HexColor('#d84315'))))
            elif re.match(r'^\d+\.|^-', line):
                # قائمة مرقمة أو نقطية
                story.append(Paragraph(f"• {line}", body_style))
                story.append(Spacer(1, 4))
            elif ':' in line and len(line) < 100:
                # عناوين فرعية
                story.append(Paragraph(f"<b>{line}</b>", 
                                     ParagraphStyle('SubHeader', parent=body_style, textColor=colors.HexColor('#2e7d32'))))
                story.append(Spacer(1, 6))
            else:
                # نص عادي
                story.append(Paragraph(line, body_style))
                story.append(Spacer(1, 8))
        
        story.append(PageBreak())
    
    # 5. الخاتمة
    story.append(Paragraph("الخاتمة: رحلتك التالية", chapter_style))
    conclusion_text = """
    <b>تهانينا! لقد أكملت رحلة التعلم في هذا الكتاب.</b><br/><br/>
    
    تذكر أن المعرفة بدون تنفيذ لا قيمة لها. ابدأ اليوم بتنفيذ خطوة واحدة على الأقل مما تعلمته.<br/><br/>
    
    <b>الخطوات التالية المقترحة:</b><br/>
    1. راجع خطة الـ72 ساعة في كل فصل<br/>
    2. نفذ قالب عمل واحد على الأقل<br/>
    3. شارك نجاحك مع مجتمعنا<br/>
    4. استمر في التعلم والتطوير<br/><br/>
    
    <i>"العمل الجاد يتفوق على الموهبة عندما لا تعمل الموهبة بجد."</i><br/><br/>
    
    إلى الأمام نحو نجاحك!
    """
    story.append(Paragraph(conclusion_text, body_style))
    
    # بناء الملف
    doc.build(story)
    return output_path

# ==================== صفحة المبيعات التلقائية ====================
def generate_sales_page(title, subtitle, chapters, target, niche, addons):
    """توليد صفحة مبيعات جاهزة لـ Hotmart"""
    
    price = calculate_price(len(chapters) * 1200, niche, addons)
    
    sales_html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Hotmart</title>
    <style>
        body {{ font-family: 'Arial', sans-serif; line-height: 1.8; color: #333; max-width: 1000px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #1a237e 0%, #0d47a1 100%); color: white; padding: 40px; border-radius: 10px; text-align: center; }}
        .title {{ font-size: 2.8em; margin-bottom: 10px; }}
        .subtitle {{ font-size: 1.4em; opacity: 0.9; }}
        .benefits {{ background: #e3f2fd; padding: 30px; border-radius: 10px; margin: 30px 0; }}
        .benefit-item {{ display: flex; align-items: center; margin: 15px 0; }}
        .benefit-icon {{ font-size: 24px; margin-left: 15px; }}
        .chapter-list {{ background: #f5f5f5; padding: 25px; border-radius: 10px; }}
        .cta-section {{ background: linear-gradient(135deg, #2e7d32 0%, #4caf50 100%); color: white; padding: 40px; border-radius: 10px; text-align: center; margin: 40px 0; }}
        .price {{ font-size: 3em; font-weight: bold; margin: 20px 0; }}
        .bonus {{ background: #fff8e1; padding: 20px; border-radius: 8px; margin: 15px 0; border-right: 5px solid #ffb300; }}
        .guarantee {{ background: #f3e5f5; padding: 25px; border-radius: 10px; text-align: center; margin: 30px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1 class="title">{title}</h1>
        <h2 class="subtitle">{subtitle}</h2>
        <p>مخصص لـ: {target}</p>
    </div>
    
    <div class="cta-section">
        <h2>🚀 ابدأ رحلتك نحو التميز الآن!</h2>
        <div class="price">${price:.2f}</div>
        <p style="font-size: 1.2em;">دفعة واحدة - وصول مدى الحياة</p>
        <button style="background: #ff9800; color: white; border: none; padding: 18px 50px; font-size: 1.2em; border-radius: 50px; cursor: pointer; margin: 20px;">
            ⚡ اشترِ الآن واحصل على المكافآت
        </button>
        <p><small>ضمان استرداد الأموال لمدة 30 يومًا</small></p>
    </div>
    
    <div class="benefits">
        <h2>🎯 ما الذي ستكسبه من هذا الكتاب؟</h2>
        <div class="benefit-item">
            <span class="benefit-icon">📈</span>
            <span>استراتيجيات مثبتة لتحقيق النتائج في {niche}</span>
        </div>
        <div class="benefit-item">
            <span class="benefit-icon">🛠️</span>
            <span>أدوات وقوالب جاهزة للاستخدام الفوري</span>
        </div>
        <div class="benefit-item">
            <span class="benefit-icon">🎓</span>
            <span>معرفة عملية يمكن تطبيقها من اليوم الأول</span>
        </div>
    </div>
    
    <div class="chapter-list">
        <h2>📖 محتويات الكتاب</h2>
        <ul>
            {"".join([f'<li><strong>{ch["title"]}</strong> - {ch["content"][:100]}...</li>' for ch in chapters])}
        </ul>
    </div>
    
    <div>
        <h2>🎁 المكافآت الحصرية (مجاناً مع الشراء)</h2>
        <div class="bonus">
            <h3>📅 خطة التنفيذ الشهرية</h3>
            <p>دليل أسبوعي خطوة بخطوة لتنفيذ كل فصل</p>
        </div>
        <div class="bonus">
            <h3>✅ قائمة المراجعة الشاملة</h3>
            <p>تأكد من أنك نفذت كل خطوة بنجاح</p>
        </div>
        {"".join([f'<div class="bonus"><h3>{name}</h3><p>مكافأة حصرية تضيف قيمة هائلة</p></div>' for name, _ in []])}
    </div>
    
    <div class="guarantee">
        <h2>🔒 ضماننا لك</h2>
        <p>نحن واثقون جداً من قيمة هذا الكتاب لدرجة أننا نقدم <strong>ضمان استرداد الأموال لمدة 30 يومًا</strong>.</p>
        <p>إذا لم تكن راضياً تماماً، سنرد لك كامل المبلغ.</p>
    </div>
    
    <div class="cta-section">
        <h2>⏰ وقت محدود: العرض الحالي</h2>
        <p>اشترِ الآن واحصل على تحديثات مجانية مدى الحياة + الدخول لمجتمع الدعم الخاص</p>
        <button style="background: #d84315; color: white; border: none; padding: 20px 60px; font-size: 1.3em; border-radius: 50px; cursor: pointer; margin: 20px;">
            🚀 أريد النجاح! اشترِ الآن
        </button>
        <p><small>يتم الدفع بشكل آمن عبر هوتمارت</small></p>
    </div>
</body>
</html>"""
    
    return sales_html

def calculate_price(word_count, niche, addons):
    """حساب السعر الذكي بناءً على القيمة"""
    base_price = 19.99
    
    # إضافة قيمة حسب عدد الكلمات
    if word_count > 10000:
        base_price += 10
    elif word_count > 20000:
        base_price += 20
    
    # إضافة قيمة حسب التخصص
    niche_bonus = {
        "التسويق الرقمي": 7,
        "العقارات": 10,
        "التجارة الإلكترونية": 8,
        "التمويل الشخصي": 5
    }
    base_price += niche_bonus.get(niche, 0)
    
    # إضافة قيمة للمواد الإضافية
    base_price += len(addons) * 3
    
    # تقريب للسعر التسويقي
    if base_price < 27:
        return 27
    elif base_price > 97:
        return 97
    else:
        return round(base_price, 2)

# ==================== واجهة Streamlit ====================
def main():
    st.set_page_config(
        page_title="🚀 Content Master Pro - منشئ الكتب الاحترافية",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS مخصص
    st.markdown("""
    <style>
    .stButton > button {
        background: linear-gradient(135deg, #1a237e 0%, #0d47a1 100%);
        color: white;
        border: none;
        padding: 15px 30px;
        font-size: 1.1em;
        border-radius: 10px;
        width: 100%;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #1a237e 0%, #0d47a1 100%);
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f5f5f5 0%, #e0e0e0 100%);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # الشريط الجانبي
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/book.png", width=80)
        st.title("📚 Content Master Pro")
        st.markdown("---")
        st.markdown("### ⚙️ الإعدادات")
        
        api_key = st.text_input("🔑 مفتاح Groq API", type="password", 
                              help="احصل على المفتاح من: https://console.groq.com")
        if api_key:
            st.session_state.api_key = api_key
        
        st.markdown("---")
        st.markdown("### 📊 الإحصائيات")
        if 'books_generated' not in st.session_state:
            st.session_state.books_generated = 0
        st.metric("📈 الكتب المولدة", st.session_state.books_generated)
        st.markdown("---")
        st.markdown("""
        ### 🎯 نصائح للنجاح:
        1. اختر تخصصاً محدداً
        2. حدد جمهورك بوضوح
        3. أضف مواد مكافئة
        4. استخدم العناوين الجذابة
        5. روج عبر السوشيال ميديا
        """)
    
    # المحتوى الرئيسي
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.title("🚀 Content Master Pro")
        st.markdown("### منشئ الكتب الاحترافية الجاهزة للبيع على **Hotmart** و **Amazon KDP**")
        st.markdown("---")
    
    # خطوات إنشاء الكتاب
    st.header("📝 خطوة 1: إعداد كتابك")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        niche = st.selectbox(
            "🎯 التخصص الرئيسي",
            list(BOOK_STRUCTURES.keys()),
            index=0,
            help="اختر التخصص الذي تريد الكتابة عنه"
        )
        
        if niche == "مخصص":
            custom_chapters = st.text_area(
                "📖 أدخل عناوين الفصول (فصل واحد في كل سطر)",
                "الفصل 1: المقدمة\nالفصل 2: الأساسيات\nالفصل 3: التطبيق\nالفصل 4: التوسع\nالفصل 5: الخاتمة",
                height=150
            )
            if custom_chapters:
                BOOK_STRUCTURES["مخصص"] = [line.strip() for line in custom_chapters.split('\n') if line.strip()]
    
    with col2:
        target = st.selectbox(
            "👥 الجمهور المستهدف",
            ["الطلاب", "المبتدئون", "رواد الأعمال", "أصحاب المشاريع", "الموظفون", "الجميع"],
            index=1,
            help="حدد لمن تكتب هذا الكتاب"
        )
        
        book_type = st.selectbox(
            "📖 نوع الكتاب",
            ["دليل المبتدئين", "إتقان متقدم", "مجموعة دراسات حالة", "نظام خطوة بخطوة", "كتاب عمل + قوالب"],
            index=0
        )
    
    with col3:
        st.markdown("### 🎁 المواد الإضافية")
        addons = st.multiselect(
            "اختر المواد المكافئة لإضافتها:",
            ["قوالب جاهزة", "خطة التنفيذ", "قائمة المراجعة", "اختبارات الفصول", "ملخص صوتي"],
            default=["قوالب جاهزة", "خطة التنفيذ"]
        )
        
        word_count = st.slider(
            "📊 الطول التقريبي (كلمة لكل فصل)",
            min_value=800,
            max_value=2000,
            value=1200,
            step=100
        )
    
    st.markdown("---")
    
    # خطوة 2: معاينة وتوليد
    st.header("⚡ خطوة 2: توليد وعرض النتائج")
    
    if st.button("🚀 إنشاء كتاب احترافي جاهز للبيع", type="primary", use_container_width=True):
        if not st.session_state.get('api_key'):
            st.error("⚠️ يرجى إدخال مفتاح API في الشريط الجانبي أولاً")
            return
        
        with st.spinner("🔄 يجري إنشاء كتابك الاحترافي..."):
            try:
                # توليد المحتوى
                progress_bar = st.progress(0)
                
                progress_bar.progress(10)
                st.write("🔍 يصمم العنوان والمقدمة...")
                
                content_data = generate_premium_content(niche, target, book_type, addons)
                progress_bar.progress(40)
                
                st.write("📖 يكتب الفصول بإتقان...")
                progress_bar.progress(70)
                
                st.write("🎨 يصمم الملف الاحترافي...")
                pdf_path = create_professional_pdf(content_data)
                progress_bar.progress(90)
                
                st.write("🛒 يجهز صفحة المبيعات...")
                progress_bar.progress(100)
                
                # تحديث العداد
                st.session_state.books_generated += 1
                
                # عرض النتائج
                st.success(f"✅ تم إنشاء الكتاب بنجاح: **{content_data['title']}**")
                
                # عرض معاينة
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.download_button(
                        label="📥 تحميل الكتاب (PDF)",
                        data=open(pdf_path, "rb").read(),
                        file_name=f"{content_data['title'].replace(' ', '_')}.pdf",
                        mime="application/pdf"
                    )
                
                with col2:
                    # إنشاء ملف HTML لصفحة المبيعات
                    sales_html = content_data['sales_page']
                    st.download_button(
                        label="🛒 تحميل صفحة المبيعات",
                        data=sales_html,
                        file_name="sales_page.html",
                        mime="text/html"
                    )
                
                with col3:
                    # إنشاء ملف ZIP كامل
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                        zip_file.write(pdf_path, "الكتاب_الاحترافي.pdf")
                        zip_file.writestr("صفحة_المبيعات.html", sales_html)
                        zip_file.writestr("ملف_الوصف.txt", 
                                        f"""وصف المنتج لـ Hotmart:

{content_data['title']}
{content_data['subtitle']}

📚 الوصف:
كتاب متكامل لـ {target} يساعدهم على إتقان {niche} خطوة بخطوة. يحتوي على دراسات حالة حقيقية، قوالب جاهزة، وخطط تنفيذ عملية.

🎯 الجمهور المستهدف:
- {target} الذين يريدون تحقيق نتائج في {niche}
- المبتدئون الذين يبحثون عن دليل شامل
- المحترفون الذين يريدون تحديث معرفتهم

📦 ما سيتعلمه المشتري:
{chr(10).join([f'• {ch["title"]}' for ch in content_data['chapters']])}

🎁 المكافآت:
{chr(10).join([f'• {name}' for name, _ in content_data['bonuses']])}

💰 السعر: ${calculate_price(content_data['metadata']['word_count'], niche, addons):.2f}
""")
                    
                    st.download_button(
                        label="📦 تحميل الحزمة الكاملة",
                        data=zip_buffer.getvalue(),
                        file_name="حزمة_الكتاب_الكاملة.zip",
                        mime="application/zip"
                    )
                
                # عرض تفاصيل الكتاب
                st.markdown("---")
                st.header("📊 تفاصيل الكتاب المولد")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("📖 العنوان", content_data['title'])
                    st.metric("🎯 الجمهور", target)
                    st.metric("💰 السعر المقترح", 
                            f"${calculate_price(content_data['metadata']['word_count'], niche, addons):.2f}")
                
                with col2:
                    st.metric("📊 عدد الفصول", len(content_data['chapters']))
                    st.metric("📝 عدد الكلمات", f"{content_data['metadata']['word_count']:,}")
                    st.metric("🎁 عدد المكافآت", len(content_data['bonuses']))
                
                # معاينة الفصل الأول
                with st.expander("👁️ معاينة الفصل الأول", expanded=True):
                    if content_data['chapters']:
                        first_chapter = content_data['chapters'][0]
                        st.markdown(f"### {first_chapter['title']}")
                        preview_text = first_chapter['content'][:500] + "..." if len(first_chapter['content']) > 500 else first_chapter['content']
                        st.write(preview_text)
                
                # نصائح للتسويق
                st.markdown("---")
                st.header("📣 نصائح لتسويق كتابك على Hotmart")
                
                tips_col1, tips_col2, tips_col3 = st.columns(3)
                
                with tips_col1:
                    st.markdown("""
                    ### 🎯 1. حدد جمهورك
                    - أنشئ شخصية المشتري المثالي
                    - اعرف مشاكله ورغباته
                    - خاطبه بلغته الخاصة
                    """)
                
                with tips_col2:
                    st.markdown("""
                    ### 📱 2. روج على السوشيال ميديا
                    - شارك مقاطع من الكتاب
                    - أنشئ محتوى تعليمي مجاني
                    - استخدم الإعلانات المستهدفة
                    """)
                
                with tips_col3:
                    st.markdown("""
                    ### 💰 3. استخدم استراتيجيات التسعير
                    - عرض ترويجي أولي
                    - خصم للمجموعات
                    - عرض upsell للدورات
                    """)
                
                # دعوة للعمل النهائية
                st.markdown("---")
                st.success("""
                🎉 **مبروك! كتابك جاهز للبيع.** 
                
                **الخطوات التالية:**
                1. قم بتحميل الكتاب على Hotmart
                2. استخدم صفحة المبيعات المولدة
                3. ابدأ الحملات التسويقية
                4. تابع المبيعات واحصل على التقييمات
                5. طور منتجات إضافية
                
                **تذكر:** الجودة والعرض هما مفتاح النجاح. ركز على تقديم قيمة حقيقية.
                """)
                
            except Exception as e:
                st.error(f"⚠️ حدث خطأ أثناء الإنشاء: {str(e)}")
                st.info("💡 تأكد من صحة مفتاح API وأن الخطة تدعم الاستخدام المطلوب")
    
    # قسم التعليمات
    with st.expander("📚 دليل الاستخدام السريع"):
        st.markdown("""
        ## 🚀 كيفية استخدام الأداة
        
        ### 1. **الإعداد الأولي**
        - احصل على مفتاح API من [Groq Console](https://console.groq.com)
        - أدخل المفتاح في الشريط الجانبي
        
        ### 2. **إنشاء الكتاب**
        - اختر التخصص المناسب
        - حدد جمهورك المستهدف
        - اختر نوع الكتاب
        - أضف مواد مكافئة لزيادة القيمة
        
        ### 3. **التوليد والتحميل**
        - اضغط على "إنشاء كتاب احترافي"
        - انتظر حتى يكتمل التوليد
        - حمل الملفات المولدة
        
        ### 4. **النشر على Hotmart**
        - سجل حساب على [Hotmart](https://www.hotmart.com)
        - أنشئ منتج جديد (رقمي)
        - ارفع ملف PDF
        - استخدم صفحة المبيعات المولدة
        - حدد السعر وشروط البيع
        
        ### 💡 نصائح للنجاح
        - اختر عناوين جذابة
        - ركز على حل مشاكل حقيقية
        - أضف صوراً احترافية للغلاف
        - اطلب تقييمات من المشترين الأوليين
        - طور منتجات إضافية مرتبطة
        """)
    
    # تذييل الصفحة
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
    <p>© 2024 Content Master Pro | أداة إنشاء الكتب الاحترافية</p>
    <p>مصممة لرواد الأعمال والكتاب الرقميين</p>
    </div>
    """, unsafe_allow_html=True)

# تشغيل التطبيق
if __name__ == "__main__":
    main()
