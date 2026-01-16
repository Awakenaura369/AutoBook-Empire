import streamlit as st
from groq import Groq
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib import colors
import re

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 1. دالة تنظيف "وحشية" كتحيد كاع الرموز الزايدة
def ultra_clean(text):
    # حيد النجمات، الهاشتاج، الشرطات، وأي رموز غريبة
    text = text.replace("**", "").replace("###", "").replace("---", "").replace("##", "")
    # حيد الجمل اللي كيبدا بها AI ديما
    text = re.sub(r"(?i)^(chapter|here is|certainly|sure|based on).*?[:\n]", "", text).strip()
    return text

def ai_call(prompt):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": "You are a professional author. Write ONLY the body text. NEVER include titles, chapter numbers, or meta-comments like 'Here is the content'."},
                  {"role": "user", "content": prompt}],
        temperature=0.4
    )
    return response.choices[0].message.content.strip()

# 2. محرك الـ PDF المضبوط
def create_final_pdf(path, title, subtitle, chapters):
    pdf = SimpleDocTemplate(path)
    styles = getSampleStyleSheet()
    
    # ستايلات بمسافات مضبوطة
    t_style = ParagraphStyle('T', parent=styles['Title'], fontSize=26, textColor=colors.navy, leading=32, spaceAfter=30)
    c_style = ParagraphStyle('C', parent=styles['Heading1'], fontSize=20, textColor=colors.darkblue, spaceBefore=30, spaceAfter=20)
    b_style = ParagraphStyle('B', parent=styles['Normal'], alignment=TA_JUSTIFY, fontSize=11, leading=16)

    story = [Spacer(1, 200), Paragraph(ultra_clean(title), t_style), Paragraph(ultra_clean(subtitle), styles['Italic']), PageBreak()]

    for i, chap in enumerate(chapters):
        # العنوان كنحطوه حنا بيدينا مرة وحدة
        story.append(Paragraph(f"Chapter {i+1}: {ultra_clean(chap['title'])}", c_style))
        # المحتوى كيجي "صافي" من AI
        for p in ultra_clean(chap['content']).split("\n\n"):
            if p.strip():
                story.append(Paragraph(p, b_style))
                story.append(Spacer(1, 10))
        story.append(PageBreak())
    pdf.build(story)

# --- الواجهة ---
st.title("✍️ THE CLEAN WRITER")
niche = st.text_input("Niche", "Property Management")

if st.button("🚀 Generate Clean Book"):
    with st.status("Writing...") as s:
        title = ai_call(f"Elite book title for {niche}")
        subtitle = ai_call(f"One subtitle for {title}")
        
        chaps = []
        for i in range(1, 4): # جرب غير بـ 3 فصول دابا باش تشوف النظافة
            ch_t = ai_call(f"Title for Chapter {i} of {title}")
            # كنأكد عليه ما يكتبش كلمة Chapter فـ الداخل
            ch_c = ai_call(f"Write the content for {ch_t}. Start directly with the first sentence. No titles.")
            chaps.append({"title": ch_t, "content": ch_c})
            
        create_final_pdf("clean_book.pdf", title, subtitle, chaps)
        s.update(label="Done!", state="complete")
        
    with open("clean_book.pdf", "rb") as f:
        st.download_button("📘 Download Clean PDF", f, "book.pdf")
