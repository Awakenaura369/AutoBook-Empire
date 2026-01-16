import streamlit as st
from groq import Groq
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib import colors
import re

# ===============================
# 🔐 API & ENGINE
# ===============================
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def ai(prompt, model_type="smart"):
    # كنستعملو أقوى موديل (llama-3.3-70b) باش يعطينا العمق اللي بغا ديبسيك
    model = "llama-3.3-70b-versatile"
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a senior business consultant and expert author. Avoid fluff. Use real data, case studies, and actionable steps. Tone: Professional and high-value."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6, # هبطنا الحرارة باش يكون الكلام رزين ومنطقي
            max_tokens=4000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

# ===============================
# 🧹 PRO CLEANER
# ===============================
def clean_pro(text):
    t = text.replace("**", "").replace("###", "").replace("---", "")
    t = re.sub(r"(?i)^(here is|certainly|sure|based on|i will).*?[:\n]", "", t).strip()
    return t

# ===============================
# 📄 THE MASTERPIECE PDF CREATOR
# ===============================
def create_masterpiece_pdf(path, title, subtitle, intro, chapters_data):
    pdf = SimpleDocTemplate(path)
    styles = getSampleStyleSheet()
    
    # ستايلات "بريميوم"
    title_style = ParagraphStyle('T', parent=styles['Title'], fontSize=32, textColor=colors.navy, spaceAfter=50, alignment=TA_CENTER)
    chap_style = ParagraphStyle('C', parent=styles['Heading1'], fontSize=22, textColor=colors.darkblue, spaceBefore=30, spaceAfter=20)
    sub_style = ParagraphStyle('S', parent=styles['Italic'], fontSize=16, textColor=colors.grey, alignment=TA_CENTER)
    body_style = ParagraphStyle('B', parent=styles['Normal'], alignment=TA_JUSTIFY, fontSize=11, leading=16)
    box_style = ParagraphStyle('Box', parent=styles['Normal'], fontSize=10, textColor=colors.whitesmoke, backColor=colors.darkslategray, borderPadding=10)

    story = []
    # 1. Cover Page
    story.append(Spacer(1, 250))
    story.append(Paragraph(clean_pro(title), title_style))
    story.append(Paragraph(clean_pro(subtitle), sub_style))
    story.append(PageBreak())

    # 2. Introduction
    story.append(Paragraph("Introduction: The Roadmap to Success", chap_style))
    for p in clean_pro(intro).split("\n\n"):
        story.append(Paragraph(p, body_style)); story.append(Spacer(1, 10))
    story.append(PageBreak())

    # 3. Chapters with Case Studies & Action Plans
    for i, chap in enumerate(chapters_data):
        story.append(Paragraph(f"Chapter {i+1}: {chap['title']}", chap_style))
        
        # Main content
        for p in clean_pro(chap['content']).split("\n\n"):
            story.append(Paragraph(p, body_style)); story.append(Spacer(1, 10))
        
        # Action Plan Box (هادي اللي كتعطي القيمة العملية)
        story.append(Spacer(1, 15))
        story.append(Paragraph("🛠 ACTION PLAN:", ParagraphStyle('H', parent=body_style, textColor=colors.gold, fontWeight='bold')))
        story.append(Paragraph(clean_pro(chap['action_plan']), box_style))
        
        story.append(PageBreak())
        
    pdf.build(story)

# ===============================
# 🌐 THE INTERFACE
# ===============================
st.set_page_config(page_title="THE SNIPER FACTORY", layout="wide")
tab1, tab2 = st.tabs(["🏗️ Build Empire", "🎯 Sniper Hooks"])

with tab1:
    st.title("🏆 THE HIGH-VALUE BOOK FACTORY")
    niche = st.text_input("🎯 Book Niche", "Digital Marketing for Small Businesses")
    
    if st.button("🚀 GENERATE MASTERPIECE"):
        with st.status("🛠️ Engineering high-value content...") as s:
            # 1. Title & Intro
            title = ai(f"One elite title for {niche}. No fluff.", "fast")
            subtitle = ai(f"One psychological subtitle for {title}", "fast")
            intro = ai(f"Write a deep intro for '{title}'. Why this matters NOW and the transformation promised.", "smart")
            
            # 2. Deep Chapters
            chapters_data = []
            for i in range(1, 6):
                st.write(f"✍️ Crafting Chapter {i} + Case Study...")
                ch_title = ai(f"Give me a strong title for Chapter {i} of '{title}'", "fast")
                content = ai(f"Write deep content for '{ch_title}'. Include a REAL-WORLD CASE STUDY with numbers.", "smart")
                action = ai(f"Create a 5-step checklist/action plan for the reader based on '{ch_title}'", "fast")
                chapters_data.append({"title": ch_title, "content": content, "action_plan": action})
            
            # 3. Marketing
            hotmart = ai(f"Sales page for {title}. Focus on pain points and ROI.", "smart")
            cover = ai(f"Cinematic AI prompt for {title} cover", "fast")
            
            pdf_p = "masterpiece.pdf"
            create_masterpiece_pdf(pdf_p, title, subtitle, intro, chapters_data)
            s.update(label="✅ Masterpiece Finished!", state="complete")

        st.success(f"Final Product: {title}")
        c1, c2, c3 = st.columns(3)
        with c1:
            with open(pdf_p, "rb") as f: st.download_button("📘 Download PDF", f, "pro_book.pdf")
        with c2: st.download_button("🛒 Hotmart Copy", hotmart, "hotmart.txt")
        with c3: st.download_button("🎨 Cover Prompt", cover, "cover.txt")

with tab2:
    st.title("🎯 FACEBOOK SNIPER")
    if st.button("🔥 Generate High-ROI Hooks"):
        hooks = ai(f"5 aggressive FB hooks for {niche}", "smart")
        st.write(hooks)
