import streamlit as st
from groq import Groq
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib import colors
import re
import io

# إعداد العميل
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def clean_and_format(text):
    """تنظيف وحشي للنص من النجمات والتكرار"""
    # مسح النجمات والهاشتاغات
    t = text.replace("**", "").replace("###", "").replace("##", "").replace("#", "")
    # مسح جمل التقديم المملة
    t = re.sub(r"(?i)^(chapter|here is|certainly|sure|based on).*?[:\n]", "", t).strip()
    return t

def ai_call(prompt, system_prompt):
    """اتصال ذكي مع Groq"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5
    )
    return response.choices[0].message.content.strip()

def create_ebook(title, subtitle, intro, chapters):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, rightMargin=70, leftMargin=70, topMargin=70, bottomMargin=70)
    styles = getSampleStyleSheet()
    
    # تنسيق احترافي "سنايبر"
    title_s = ParagraphStyle('T', parent=styles['Title'], fontSize=28, textColor=colors.navy, spaceAfter=20)
    sub_s = ParagraphStyle('S', parent=styles['Italic'], fontSize=14, textColor=colors.grey, alignment=TA_CENTER, spaceAfter=50)
    chap_s = ParagraphStyle('C', parent=styles['Heading1'], fontSize=20, textColor=colors.darkblue, spaceBefore=30, spaceAfter=20)
    body_s = ParagraphStyle('B', parent=styles['Normal'], fontSize=11, leading=16, alignment=TA_JUSTIFY)
    box_s = ParagraphStyle('Box', parent=styles['Normal'], fontSize=10, backColor=colors.whitesmoke, borderPadding=10)

    story = []
    # صفحة الغلاف
    story.append(Spacer(1, 200))
    story.append(Paragraph(clean_and_format(title), title_s))
    story.append(Paragraph(clean_and_format(subtitle), sub_s))
    story.append(PageBreak())

    # المقدمة
    story.append(Paragraph("Introduction", chap_s))
    story.append(Paragraph(clean_and_format(intro), body_s))
    story.append(PageBreak())

    # الفصول
    for i, chap in enumerate(chapters):
        story.append(Paragraph(f"Chapter {i+1}: {clean_and_format(chap['title'])}", chap_s))
        story.append(Paragraph(clean_and_format(chap['content']), body_s))
        story.append(Spacer(1, 20))
        # إضافة Action Plan لزيادة القيمة
        story.append(Paragraph("✅ KEY TAKEAWAYS & ACTION:", ParagraphStyle('H', parent=body_s, textColor=colors.darkred)))
        story.append(Paragraph(clean_and_format(chap['action']), box_s))
        story.append(PageBreak())

    doc.build(story)
    return buffer.getvalue()

# --- واجهة المستخدم ---
st.title("🎯 The Content Sniper V1")
st.write("ركز فقط على المحتوى.. التنسيق علينا!")

niche = st.text_input("موضوع الكتاب (Niche):", "E-commerce for Beginners")

if st.button("🚀 إنشاء الكتاب باحترافية"):
    with st.status("🛠 جاري الهندسة...") as s:
        # 1. العناوين
        title = ai_call(f"Create a bestseller title for {niche}", "You are a marketing genius.")
        subtitle = ai_call(f"Create a deep subtitle for {title}", "Expert author.")
        
        # 2. المقدمة والفصول
        intro = ai_call(f"Write a deep intro for {title}", "World-class writer. No fluff.")
        
        chapters = []
        for i in range(1, 4): # 3 فصول للتجربة
            st.write(f"✍️ كـتابة الفصل {i}...")
            ch_t = ai_call(f"Chapter {i} title for {title}", "Expert author.")
            ch_c = ai_call(f"Write full content for {ch_t}. Include a Case Study.", "Professional analyst.")
            ch_a = ai_call(f"3 action steps for {ch_t}", "Practical coach.")
            chapters.append({"title": ch_t, "content": ch_c, "action": ch_a})
            
        pdf_file = create_ebook(title, subtitle, intro, chapters)
        s.update(label="✅ الكتاب جاهز!", state="complete")

    st.success(f"تم إنشاء: {title}")
    st.download_button("📘 تحميل النسخة الاحترافية", pdf_file, "pro_sniper_book.pdf", "application/pdf")
