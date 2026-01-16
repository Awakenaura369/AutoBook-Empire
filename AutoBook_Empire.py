import os
import streamlit as st
from groq import Groq
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
import re

# ===============================
# 🔐 API SETUP (GROQ IS THE ENGINE)
# ===============================
# [2026-01-10] AI engine is Groq
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def ai(prompt, model_type="fast"):
    # استعمال أحدث الموديلات لتفادي أرور Decommissioned
    model = "llama-3.1-8b-instant" if model_type == "fast" else "llama-3.3-70b-versatile"
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a world-class author and marketing strategist. You write deep, actionable content with real-world examples."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=3500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

# ===============================
# 🧹 CLEANING FUNCTION (ANTI-BOT)
# ===============================
def clean_markdown(text):
    """تحويل النجمات لتنسيق Bold للـ PDF أو حذفها لتفادي 'الفرشة'"""
    # نحذف النجمات لضمان مظهر نظيف واحترافية عالية
    text = text.replace("**", "")
    text = text.replace("###", "")
    return text

# ===============================
# 📄 PDF CREATOR (PRO VERSION)
# ===============================
def create_pro_pdf(path, title, subtitle, chapters_list):
    pdf = SimpleDocTemplate(path)
    styles = getSampleStyleSheet()
    
    justified_style = ParagraphStyle(
        name='Justify', 
        parent=styles['Normal'], 
        alignment=TA_JUSTIFY, 
        fontSize=11, 
        leading=14
    )
    
    story = []
    # Title Page
    story.append(Spacer(1, 150))
    story.append(Paragraph(clean_markdown(title), styles["Title"]))
    story.append(Spacer(1, 20))
    story.append(Paragraph(clean_markdown(subtitle), styles["Italic"]))
    story.append(PageBreak())

    # Chapters
    for i, content in enumerate(chapters_list):
        story.append(Paragraph(f"Chapter {i+1}", styles["Heading1"]))
        story.append(Spacer(1, 12))
        clean_content = clean_markdown(content)
        for line in clean_content.split("\n"):
            if line.strip():
                story.append(Paragraph(line, justified_style))
                story.append(Spacer(1, 8))
        story.append(PageBreak())

    pdf.build(story)

# ===============================
# 🌐 STREAMLIT UI WITH TABS
# ===============================
st.set_page_config(page_title="PRO BOOK FACTORY", layout="wide")

tab1, tab2 = st.tabs(["📚 AI Book Factory", "🎯 Facebook Sniper"])

# --- TAB 1: BOOK FACTORY ---
with tab1:
    st.title("🚀 THE PROFESSIONAL EBOOK EMPIRE")
    niche = st.text_input("🎯 Enter Niche", "E-commerce Success Strategies")
    
    if st.button("GENERATE MASTERPIECE"):
        with st.status("🛠️ Building professional content...") as status:
            # 1. Outline & Titles
            structure = ai(f"Create a deep 5-chapter outline for a book about {niche} with case study ideas.", "smart")
            title = ai(f"Bestseller title for niche: {niche}", "fast")
            subtitle = ai(f"Emotional subtitle for: {title}", "fast")
            
            # 2. Chapters (Deep Writing)
            full_book = []
            for i in range(1, 6):
                st.write(f"✍️ Writing Chapter {i} with Deep Dive Case Studies...")
                chap = ai(f"Write Chapter {i} for '{title}'. Min 1000 words. Include real numbers, a case study, and an action plan.", "smart")
                full_book.append(chap)
            
            pdf_path = "pro_book.pdf"
            create_pro_pdf(pdf_path, title, subtitle, full_book)
            status.update(label="✅ Ready!", state="complete")

        st.success(f"Successfully generated: {title}")
        with open(pdf_path, "rb") as f:
            st.download_button("📘 Download Professional PDF", f, "ebook_pro.pdf")

# --- TAB 2: FACEBOOK SNIPER ---
# [2026-01-13] Add Social Media Hook Generator to Facebook Sniper tab
with tab2:
    st.title("🎯 FACEBOOK SNIPER – AD HOOK GENERATOR")
    st.markdown("Generate scroll-stopping hooks for your ebook or service.")
    
    product_desc = st.text_area("What are you selling?", "A book about Real Estate for Students")
    
    if st.button("🔥 GENERATE SNIPER HOOKS"):
        with st.spinner("Targeting psychological triggers..."):
            hooks = ai(f"""
            Generate 5 high-converting Facebook Ad Hooks for: {product_desc}
            Types:
            1. Negative Hook (Fear of missing out)
            2. Result Hook (Pure benefit)
            3. Question Hook (Curiosity)
            4. Transformation (From/To)
            5. 'The Secret' Hook
            Tone: Aggressive, psychological, stop-the-scroll.
            """, "smart")
            
            st.markdown("### 🎯 Your Sniper Hooks:")
            st.write(hooks)
            st.download_button("📥 Save Hooks", hooks, "hooks.txt")
