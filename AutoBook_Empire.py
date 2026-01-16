import os
import streamlit as st
from groq import Groq
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib import colors # مكتبة الألوان
import re

# ===============================
# 🔐 API SETUP (GROQ ENGINE)
# ===============================
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def ai(prompt, model_type="fast"):
    model = "llama-3.1-8b-instant" if model_type == "fast" else "llama-3.3-70b-versatile"
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a professional author. Write clean, deep content without conversational filler or suggestions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=3500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

# ===============================
# 🧹 CLEANING (ANTI-BOT & NO ASTERISKS)
# ===============================
def clean_txt(text):
    """حذف النجمات وأي نصوص تقديمية من الـ AI"""
    # حذف النجمات
    t = text.replace("**", "").replace("###", "")
    # حذف الجمل التقديمية المشهورة ديال الـ AI
    t = re.sub(r"Here is a short.*:", "", t, flags=re.IGNORECASE)
    t = re.sub(r"Here are some.*:", "", t, flags=re.IGNORECASE)
    return t.strip()

# ===============================
# 📄 PDF CREATOR (COLOR & PRO FORMAT)
# ===============================
def create_pro_pdf(path, title, subtitle, chapters):
    pdf = SimpleDocTemplate(path)
    styles = getSampleStyleSheet()
    
    # ستايلات ملونة واحترافية
    title_style = ParagraphStyle('T', parent=styles['Title'], fontSize=26, textColor=colors.dodgerblue, spaceAfter=30)
    chap_style = ParagraphStyle('C', parent=styles['Heading1'], fontSize=18, textColor=colors.dodgerblue, spaceBefore=20)
    body_style = ParagraphStyle('B', parent=styles['Normal'], alignment=TA_JUSTIFY, fontSize=11, leading=14)

    story = [Spacer(1, 200), Paragraph(clean_txt(title), title_style), 
             Paragraph(clean_txt(subtitle), styles["Italic"]), PageBreak()]

    for i, content in enumerate(chapters):
        story.append(Paragraph(f"Chapter {i+1}", chap_style))
        story.append(Spacer(1, 12))
        for line in clean_txt(content).split("\n"):
            if line.strip():
                story.append(Paragraph(line, body_style))
                story.append(Spacer(1, 8))
        story.append(PageBreak())
    pdf.build(story)

# ===============================
# 🌐 THE FULL EMPIRE UI
# ===============================
st.set_page_config(page_title="PRO BOOK EMPIRE", layout="wide")
tab1, tab2 = st.tabs(["📚 AI Book Factory", "🎯 Facebook Sniper"])

with tab1:
    st.title("🚀 PROFESSIONAL BOOK FACTORY")
    niche = st.text_input("🎯 Enter Niche", "Digital Marketing Secrets")
    
    if st.button("🚀 GENERATE MASTERPIECE"):
        with st.status("🛠️ Building your professional empire...") as s:
            # 1. العناوين
            title = ai(f"Give me only ONE bestseller title for {niche}", "fast")
            subtitle = ai(f"Give me only ONE emotional subtitle for {title}", "fast")
            
            # 2. الفصول
            full_book = []
            for i in range(1, 6):
                st.write(f"✍️ Writing Chapter {i} with Case Studies...")
                full_book.append(ai(f"Write the full content for Chapter {i} of '{title}'. NO intro text, just the chapter.", "smart"))
            
            # 3. هوتمارت (باقي معانا!)
            hotmart = ai(f"Write a high-converting Hotmart sales page for {title}", "smart")
            
            # 4. برومبت الغلاف (باقي معانا!)
            cover = ai(f"Cinematic AI cover prompt for {title}", "fast")
            
            pdf_path = "final_pro_book.pdf"
            create_pro_pdf(pdf_path, title, subtitle, full_book)
            s.update(label="✅ Success!", state="complete")

        st.header(f"📖 {title}")
        c1, c2, c3 = st.columns(3)
        with c1:
            with open(pdf_path, "rb") as f:
                st.download_button("📘 Download Ebook (PDF)", f, "ebook.pdf")
        with c2:
            st.download_button("🛒 Hotmart Sales Copy", hotmart, "hotmart.txt")
        with c3:
            st.download_button("🎨 Cover Image Prompt", cover, "cover_prompt.txt")
            
        st.subheader("🛒 Hotmart Preview")
        st.info(hotmart)

with tab2:
    # [2026-01-13] Facebook Sniper is still here!
    st.title("🎯 FACEBOOK SNIPER")
    ad_desc = st.text_input("What are you promoting?", niche)
    if st.button("🔥 Generate Sniper Hooks"):
        hooks = ai(f"Generate 5 aggressive FB hooks for: {ad_desc}", "smart")
        st.write(hooks)
