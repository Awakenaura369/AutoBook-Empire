import streamlit as st
from groq import Groq
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib import colors
import re
import io

# إعداد العميل (Groq)
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def ultra_clean(text):
    """دالة لتعقيم النص من النجمات وتكرار العناوين"""
    if not text: return ""
    # مسح النجمات والرموز
    t = text.replace("**", "").replace("###", "").replace("##", "").replace("#", "").replace("---", "")
    # مسح جمل التقديم بحال "Certainly! Here is..."
    t = re.sub(r"(?i)^(chapter|section|here is|certainly|sure|based on).*?[:\n]", "", t).strip()
    return t

def ai_expert(prompt, system_instruction):
    """اتصال مركز مع AI لضمان جودة المحتوى"""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4 # درجة حرارة منخفضة لتقليل التبرهيش
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

def generate_pdf(title, subtitle, intro, chapters):
    """محرك صناعة الـ PDF بتنسيق نقي"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, rightMargin=70, leftMargin=70, topMargin=70, bottomMargin=70)
    styles = getSampleStyleSheet()
    
    # تعريف الستايلات الاحترافية
    title_s = ParagraphStyle('T', parent=styles['Title'], fontSize=26, textColor=colors.navy, leading=32, spaceAfter=20)
    sub_s = ParagraphStyle('S', parent=styles['Italic'], fontSize=14, textColor=colors.grey, alignment=TA_CENTER, spaceAfter=40)
    chap_s = ParagraphStyle('C', parent=styles['Heading1'], fontSize=20, textColor=colors.darkblue, spaceBefore=30, spaceAfter=20)
    body_s = ParagraphStyle('B', parent=styles['Normal'], fontSize=11, leading=16, alignment=TA_JUSTIFY)
    box_s = ParagraphStyle('Box', parent=styles['Normal'], fontSize=10, backColor=colors.whitesmoke, borderPadding=10, textColor=colors.black)

    story = []
    # 1. صفحة الغلاف
    story.append(Spacer(1, 200))
    story.append(Paragraph(ultra_clean(title), title_s))
    story.append(Paragraph(ultra_clean(subtitle), sub_s))
    story.append(PageBreak())

    # 2. المقدمة
    story.append(Paragraph("Introduction", chap_s))
    for p in ultra_clean(intro).split("\n\n"):
        story.append(Paragraph(p, body_s))
        story.append(Spacer(1, 10))
    story.append(PageBreak())

    # 3. الفصول
    for i, chap in enumerate(chapters):
        story.append(Paragraph(f"Chapter {i+1}: {ultra_clean(chap['title'])}", chap_s))
        for p in ultra_clean(chap['content']).split("\n\n"):
            if p.strip():
                story.append(Paragraph(p, body_s))
                story.append(Spacer(1, 10))
        
        # صندوق الأكشن بلان (القيمة المضافة)
        story.append(Spacer(1, 20))
        story.append(Paragraph("🚀 PRACTICAL ACTION STEPS:", ParagraphStyle('H', parent=body_s, textColor=colors.darkred, fontWeight='bold')))
        story.append(Paragraph(ultra_clean(chap['action']), box_s))
        story.append(PageBreak())

    doc.build(story)
    return buffer.getvalue()

# --- واجهة Streamlit ---
st.set_page_config(page_title="The Clean Sniper", layout="centered")
st.title("🛡️ The Content Sniper V1")
st.info("هذا المحرك يركز 100% على جودة الكتاب وتنسيقه الاحترافي.")

niche = st.text_input("موضوع الكتاب (Niche):", "Advanced Property Management")

if st.button("🚀 إنشاء كتاب احترافي"):
    with st.status("🏗️ جاري هندسة المحتوى الصافي...") as s:
        # تعليمات صارمة للـ AI
        sys_writer = "You are a professional author. Use deep analysis and real-world data. NEVER use asterisks (**) or markdown headers. Start text immediately."
        
        # 1. العناوين
        title = ai_expert(f"Elite bestseller title for {niche}", sys_writer)
        subtitle = ai_expert(f"Deep results-oriented subtitle for {title}", sys_writer)
        intro = ai_expert(f"Write a 500-word deep intro for {title}. No fluff.", sys_writer)
        
        # 2. الفصول (3 فصول للتركيز)
        chapters = []
        for i in range(1, 4):
            st.write(f"✍️ كـتابة الفصل {i}...")
            ch_t = ai_expert(f"Chapter {i} title for {title}", sys_writer)
            ch_c = ai_expert(f"Write deep content for '{ch_t}'. Include a specific Case Study. NO TITLES.", sys_writer)
            ch_a = ai_expert(f"Provide 5 actionable steps for '{ch_t}'", sys_writer)
            chapters.append({"title": ch_t, "content": ch_c, "action": ch_a})
            
        pdf_file = generate_pdf(title, subtitle, intro, chapters)
        s.update(label="✅ تم الإنجاز بنجاح!", state="complete")

    st.success(f"تم إنشاء: {title}")
    st.download_button("📘 تحميل الكتاب (النسخة المنقحة)", pdf_file, "clean_sniper_book.pdf", "application/pdf")
