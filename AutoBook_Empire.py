import os
import streamlit as st
from groq import Groq
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY

# ===============================
# 🔐 API SETUP (ENGINE IS GROQ)
# ===============================
# [2026-01-10] The AI engine is Groq
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def ai(prompt, model_type="fast"):
    # استعمال الموديلات الجديدة لتفادي decommissioning error
    model = "llama-3.1-8b-instant" if model_type == "fast" else "llama-3.3-70b-versatile"
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert digital product creator. You write deep, clean, and professional content."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=3500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

# ===============================
# 🧹 CLEANING (NO MORE ASTERISKS)
# ===============================
def clean_txt(text):
    """تحويل النجمات لتنسيق نظيف لمنع 'الفرشة'"""
    return text.replace("**", "").replace("###", "").strip()

# ===============================
# 📄 PDF CREATOR
# ===============================
def create_pdf(path, title, subtitle, chapters):
    pdf = SimpleDocTemplate(path)
    styles = getSampleStyleSheet()
    justified = ParagraphStyle(name='J', parent=styles['Normal'], alignment=TA_JUSTIFY, fontSize=11)
    
    story = [Spacer(1, 150), Paragraph(clean_txt(title), styles["Title"]), 
             Spacer(1, 20), Paragraph(clean_txt(subtitle), styles["Italic"]), PageBreak()]

    for i, content in enumerate(chapters):
        story.append(Paragraph(f"Chapter {i+1}", styles["Heading1"]))
        story.append(Spacer(1, 12))
        for line in clean_txt(content).split("\n"):
            if line.strip():
                story.append(Paragraph(line, justified))
                story.append(Spacer(1, 8))
        story.append(PageBreak())
    pdf.build(story)

# ===============================
# 🌐 UI WITH ALL FEATURES
# ===============================
st.set_page_config(page_title="PRO FACTORY", layout="wide")
tab1, tab2 = st.tabs(["📚 AI Book Factory", "🎯 Facebook Sniper"])

with tab1:
    st.title("🚀 PROFESSIONAL BOOK FACTORY")
    niche = st.text_input("🎯 Niche", "Passive Income for Beginners")
    
    if st.button("🚀 GENERATE FULL PACKAGE"):
        with st.status("🛠️ Working...") as s:
            # 1. العناوين والهيكل
            title = ai(f"Bestseller title for {niche}", "fast")
            subtitle = ai(f"Subtitle for {title}", "fast")
            
            # 2. الفصول (كتابة عميقة لكل فصل بوحدو)
            full_book = []
            for i in range(1, 6):
                st.write(f"✍️ Writing Chapter {i}...")
                full_book.append(ai(f"Write Chapter {i} for '{title}'. Min 1000 words with case studies.", "smart"))
            
            # 3. هوتمارت (اللي كنتي خايف عليه!)
            st.write("🛒 Generating Hotmart Sales Copy...")
            hotmart = ai(f"Write a high-converting Hotmart description for {title}. Include benefits and CTA.", "smart")
            
            # 4. غلاف
            cover = ai(f"AI cover prompt for {title}", "fast")
            
            pdf_path = "pro_book.pdf"
            create_pdf(pdf_path, title, subtitle, full_book)
            s.update(label="✅ Everything Ready!", state="complete")

        # عرض النتائج
        st.header(f"📖 {title}")
        col1, col2, col3 = st.columns(3)
        with col1:
            with open(pdf_path, "rb") as f:
                st.download_button("📘 Download Ebook", f, "ebook.pdf")
        with col2:
            st.download_button("🛒 Download Hotmart Copy", hotmart, "hotmart.txt")
        with col3:
            st.download_button("🎨 Download Cover Prompt", cover, "cover.txt")
            
        st.subheader("📝 Hotmart Preview")
        st.info(hotmart) # هاهو هوتمارت باين قدامك دبا!

with tab2:
    # [2026-01-13] Social Media Hook Generator in Facebook Sniper tab
    st.title("🎯 FACEBOOK SNIPER")
    desc = st.text_input("Product to promote:", niche if niche else "My New Ebook")
    if st.button("🔥 Generate Hooks"):
        hooks = ai(f"Generate 5 aggressive Facebook ad hooks for: {desc}", "smart")
        st.write(hooks)
