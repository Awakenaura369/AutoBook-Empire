import os
import streamlit as st
from groq import Groq
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY

# ===============================
# 🔐 API SETUP
# ===============================
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def ai(prompt, model_type="fast"):
    model = "llama-3.1-8b-instant" if model_type == "fast" else "llama-3.3-70b-versatile"
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert author and researcher. Write with depth, examples, and professional insight."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=3500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

# ===============================
# 🧠 PROFESSIONAL BOOK ENGINE
# ===============================
def generate_pro_book(niche):
    # 1. توليد عنوان جذاب وهيكل مفصل (Outline)
    structure_raw = ai(f"""Create a detailed 5-chapter outline for a 50-page ebook about '{niche}'. 
    For each chapter, provide a specific real-world Case Study or Expert Example to include.
    Make it appeal to a high-ticket audience.""", "smart")
    
    title = ai(f"Based on this outline: '{structure_raw}', give me one powerful bestseller book title.", "fast")
    subtitle = ai(f"Give me a catchy emotional subtitle for the book: {title}", "fast")

    full_book_content = []

    # 2. كتابة كل فصل بعمق (الحل لمشكل الاختصار)
    chapters = ["Chapter 1", "Chapter 2", "Chapter 3", "Chapter 4", "Chapter 5"]
    
    progress_bar = st.progress(0)
    for i, chap_name in enumerate(chapters):
        st.write(f"✍️ Writing {chap_name} with Case Studies...")
        content = ai(f"""
        Write the full content for {chap_name} of the book '{title}'.
        Niche: {niche}
        Context: {structure_raw}
        
        STRICT REQUIREMENTS:
        - MINIMUM 1000 words for this chapter.
        - Include a 'Deep Dive Case Study' section with real-world examples and numbers.
        - Add 'Step-by-Step Action Plan' for the reader.
        - Use professional, authoritative, and engaging language.
        - No fluff; focus on high-value information.
        """, "smart")
        
        full_book_content.append(content)
        progress_bar.progress((i + 1) / len(chapters))

    # 3. ملحقات البيزنس
    hotmart = ai(f"Write a 1000-word high-converting sales page for the book '{title}' in the {niche} niche.", "smart")
    cover = ai(f"Create a high-end cinematic AI image prompt for the book cover: {title}", "fast")

    return title, subtitle, full_book_content, hotmart, cover

# ===============================
# 📄 PDF CREATOR (PRO VERSION)
# ===============================
def create_pro_pdf(path, title, subtitle, chapters_list):
    pdf = SimpleDocTemplate(path)
    styles = getSampleStyleSheet()
    
    # ستايل مخصص للفقرات باش تجي مريحة في القراءة
    justified_style = ParagraphStyle(name='Justify', parent=styles['Normal'], alignment=TA_JUSTIFY, fontSize=11, leading=14)
    
    story = []
    # Title Page
    story.append(Spacer(1, 100))
    story.append(Paragraph(title, styles["Title"]))
    story.append(Spacer(1, 20))
    story.append(Paragraph(subtitle, styles["Italic"]))
    story.append(PageBreak())

    # Chapters
    for i, content in enumerate(chapters_list):
        story.append(Paragraph(f"Chapter {i+1}", styles["Heading1"]))
        story.append(Spacer(1, 12))
        for line in content.split("\n"):
            if line.strip():
                story.append(Paragraph(line, justified_style))
                story.append(Spacer(1, 8))
        story.append(PageBreak())

    pdf.build(story)

# ===============================
# 🌐 STREAMLIT UI
# ===============================
st.set_page_config(page_title="PRO BOOK FACTORY", layout="wide")
st.title("🚀 THE PROFESSIONAL EBOOK EMPIRE")
st.sidebar.header("Settings")
niche_input = st.sidebar.text_input("🎯 Target Niche", "Luxury Real Estate Investing")

if st.sidebar.button("GENERATE MASTERPIECE"):
    with st.status("🛠️ Building your professional empire...") as status:
        title, subtitle, content_list, hotmart, cover = generate_pro_book(niche_input)
        
        pdf_path = "final_pro_book.pdf"
        create_pro_pdf(pdf_path, title, subtitle, content_list)
        
        status.update(label="✅ Book Complete!", state="complete")

    st.header(f"📖 {title}")
    st.subheader(subtitle)

    col1, col2, col3 = st.columns(3)
    with col1:
        with open(pdf_path, "rb") as f:
            st.download_button("📘 Download Professional PDF", f, "pro_ebook.pdf")
    with col2:
        st.download_button("🛒 Get Sales Copy", hotmart, "sales_page.txt")
    with col3:
        st.download_button("🎨 Get Cover Prompt", cover, "cover_prompt.txt")

    st.divider()
    st.markdown("### 📝 Sales Copy Preview")
    st.text_area("Hotmart Page", hotmart, height=300)
