import streamlit as st
from groq import Groq
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib import colors
import re
import datetime
import io

# ==================== الإعدادات الأولية ====================
# [2026-01-10] AI engine is Groq
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    client = None

# ==================== وظائف التنظيف والذكاء الاصطناعي ====================
def ultra_clean(text):
    """تنظيف النص من النجمات والعبارات الزائدة"""
    if not text: return ""
    t = text.replace("**", "").replace("###", "").replace("##", "").replace("---", "")
    t = re.sub(r"(?i)^(chapter|section|here is|certainly|sure|based on).*?[:\n]", "", t).strip()
    return t

def ai_writer(prompt):
    if not client: return "⚠️ يرجى إضافة مفتاح API"
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a world-class author. Write deep, professional content. NO asterisks, NO 'Chapter X' titles, NO fluff. Start directly."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

# ==================== محرك إنشاء الـ PDF ====================
def create_pdf(title, subtitle, intro, chapters):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()
    
    # ستايلات احترافية
    t_style = ParagraphStyle('T', parent=styles['Title'], fontSize=26, textColor=colors.navy, alignment=TA_CENTER, leading=32, spaceAfter=20)
    c_style = ParagraphStyle('C', parent=styles['Heading1'], fontSize=18, textColor=colors.darkblue, spaceBefore=30, spaceAfter=20)
    b_style = ParagraphStyle('B', parent=styles['Normal'], alignment=TA_JUSTIFY, fontSize=11, leading=15)
    box_style = ParagraphStyle('Box', parent=styles['Normal'], fontSize=10, textColor=colors.whitesmoke, backColor=colors.darkslategray, borderPadding=10)

    story = []
    # الغلاف
    story.append(Spacer(1, 200))
    story.append(Paragraph(ultra_clean(title), t_style))
    story.append(Paragraph(ultra_clean(subtitle), styles['Italic']))
    story.append(PageBreak())

    # المقدمة
    story.append(Paragraph("Introduction", c_style))
    for p in ultra_clean(intro).split("\n\n"):
        story.append(Paragraph(p, b_style))
        story.append(Spacer(1, 10))
    story.append(PageBreak())

    # الفصول
    for i, chap in enumerate(chapters):
        story.append(Paragraph(f"Chapter {i+1}: {ultra_clean(chap['title'])}", c_style))
        for p in ultra_clean(chap['content']).split("\n\n"):
            if p.strip():
                story.append(Paragraph(p, b_style))
                story.append(Spacer(1, 8))
        
        # صندوق الأكشن بلان
        story.append(Spacer(1, 15))
        story.append(Paragraph("🛠 ACTION PLAN:", ParagraphStyle('H', parent=b_style, textColor=colors.gold)))
        story.append(Paragraph(ultra_clean(chap['action']), box_style))
        story.append(PageBreak())

    doc.build(story)
    return buffer.getvalue()

# ==================== واجهة التطبيق ====================
def main():
    st.set_page_config(page_title="Sniper Book Factory", layout="wide")
    st.title("📚 Sniper Book Factory Pro")
    
    with st.sidebar:
        st.header("⚙️ Settings")
        if not client: st.error("API Key Missing in Secrets!")
        niche = st.selectbox("Niche", ["Digital Marketing", "Real Estate", "E-commerce", "Personal Finance"])
        target = st.text_input("Target Audience", "Beginners")

    if st.button("🚀 Generate Professional Book"):
        with st.status("🛠 Building your masterpiece...") as status:
            # 1. التخطيط
            title = ai_writer(f"Premium title for a book about {niche} for {target}")
            subtitle = ai_writer(f"Compelling subtitle for {title}")
            intro = ai_writer(f"Write a deep 500-word intro for {title}")
            
            # 2. الفصول
            chapters = []
            for i in range(1, 5): # 4 Chapters
                st.write(f"✍️ Writing Chapter {i}...")
                ch_t = ai_writer(f"Chapter {i} title for {title}")
                ch_c = ai_writer(f"Write deep content for {ch_t} with a case study. No titles.")
                ch_a = ai_writer(f"5-step action plan for {ch_t}")
                chapters.append({"title": ch_t, "content": ch_c, "action": ch_a})
            
            # 3. إنشاء الملف
            pdf_data = create_pdf(title, subtitle, intro, chapters)
            status.update(label="✅ Ready!", state="complete")

        st.success(f"Generated: {title}")
        st.download_button("📥 Download Ebook (PDF)", pdf_data, "masterpiece.pdf", "application/pdf")
        
        # Preview سريع لهوتمارت
        st.divider()
        st.subheader("🛒 Hotmart Sales Description Idea")
        st.info(f"Book: {title}\nTarget: {target}\nValue: Includes 4 Case Studies and 4 Action Plans.")

if __name__ == "__main__":
    main()
