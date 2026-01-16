import streamlit as st
from groq import Groq
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib import colors
import re

# إعداد المحرك (Groq)
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def ai_writer(prompt):
    # استخدام أقوى موديل للتركيز فقط على جودة الكتابة
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": """You are a world-class non-fiction author. 
                Your writing is:
                1. Deep and Analytical: Avoid surface-level information.
                2. Practical: Include real-world case studies with data.
                3. Structured: Use clear steps and actionable advice.
                4. Professional: No conversational filler or AI self-references."""},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5, # حرارة منخفضة لضمان الدقة والاحترافية
            max_tokens=4000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

def clean_text(text):
    # تنظيف احترافي للنص من أي شوائب
    t = text.replace("**", "").replace("###", "").replace("---", "")
    t = re.sub(r"(?i)^(here is|certainly|sure|based on|in this chapter).*?[:\n]", "", t).strip()
    return t

def create_pro_pdf(path, title, subtitle, intro, chapters):
    pdf = SimpleDocTemplate(path)
    styles = getSampleStyleSheet()
    
    # ستايلات هندسية لمنع التداخل
    title_style = ParagraphStyle('MainTitle', parent=styles['Title'], fontSize=28, textColor=colors.navy, alignment=TA_CENTER, leading=34, spaceAfter=20)
    sub_style = ParagraphStyle('SubTitle', parent=styles['Italic'], fontSize=14, textColor=colors.grey, alignment=TA_CENTER, leading=18)
    chap_style = ParagraphStyle('ChapterTitle', parent=styles['Heading1'], fontSize=22, textColor=colors.darkblue, spaceBefore=40, spaceAfter=20)
    body_style = ParagraphStyle('BodyText', parent=styles['Normal'], alignment=TA_JUSTIFY, fontSize=11, leading=16)
    box_style = ParagraphStyle('ActionBox', parent=styles['Normal'], fontSize=10, textColor=colors.whitesmoke, backColor=colors.darkslategray, borderPadding=12)

    story = []
    
    # 1. صفحة العنوان (نقية ومحترفة)
    story.append(Spacer(1, 200))
    story.append(Paragraph(clean_text(title), title_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph(clean_text(subtitle), sub_style))
    story.append(PageBreak())

    # 2. المقدمة العميقة
    story.append(Paragraph("Introduction", chap_style))
    for p in clean_text(intro).split("\n\n"):
        if p.strip():
            story.append(Paragraph(p, body_style))
            story.append(Spacer(1, 12))
    story.append(PageBreak())

    # 3. الفصول (محتوى + Case Study + Action Plan)
    for i, chap in enumerate(chapters):
        story.append(Paragraph(f"Chapter {i+1}: {chap['title']}", chap_style))
        for p in clean_text(chap['content']).split("\n\n"):
            if p.strip():
                story.append(Paragraph(p, body_style))
                story.append(Spacer(1, 10))
        
        # إضافة صندوق الخطوات العملية (Value Booster)
        story.append(Spacer(1, 20))
        story.append(Paragraph("🛠️ STRATEGIC ACTION PLAN:", ParagraphStyle('H', parent=body_style, textColor=colors.gold, fontWeight='bold')))
        story.append(Paragraph(clean_text(chap['action']), box_style))
        story.append(PageBreak())
        
    pdf.build(story)

# واجهة المستخدم البسيطة والمركزة
st.set_page_config(page_title="THE CONTENT MASTER", layout="centered")
st.title("✍️ THE CONTENT MASTER")
st.write("هذا المحرك مخصص فقط لإنشاء محتوى كتب احترافي وعميق.")

niche = st.text_input("🎯 ما هو موضوع الكتاب؟", "Advanced Digital Growth")

if st.button("🚀 إنشاء الكتاب باحترافية"):
    with st.status("🛠️ يجري الآن هندسة المحتوى...") as status:
        # التركيز على العناوين أولاً
        title = ai_writer(f"Create one premium bestseller title for {niche}.")
        subtitle = ai_writer(f"Create a deep, results-oriented subtitle for '{title}'.")
        
        # إنشاء مقدمة قوية
        intro = ai_writer(f"Write a 600-word introduction for '{title}'. Focus on the pain points and the solution.")
        
        # إنشاء الفصول بعمق (Case Studies included)
        chapters = []
        for i in range(1, 6):
            st.write(f"⌛ جاري كتابة الفصل {i} بعمق...")
            ch_title = ai_writer(f"Provide a strong title for Chapter {i} of '{title}'.")
            # هنا نطلب Case Study صريحة
            ch_content = ai_writer(f"Write the full content for '{ch_title}'. Include a REAL-WORLD CASE STUDY with data and numbers.")
            ch_action = ai_writer(f"Create a 5-step implementation checklist for the reader based on '{ch_title}'.")
            chapters_data = {"title": ch_title, "content": ch_content, "action": ch_action}
            chapters.append(chapters_data)
        
        create_pro_pdf("pro_masterpiece.pdf", title, subtitle, intro, chapters)
        status.update(label="✅ تم إنشاء الكتاب بنجاح!", state="complete")

    st.success(f"تم إنجاز: {title}")
    with open("pro_masterpiece.pdf", "rb") as f:
        st.download_button("📘 تحميل الكتاب (النسخة الاحترافية)", f, "professional_book.pdf")
