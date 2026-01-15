import os
import streamlit as st
from groq import Groq
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ===============================
# 🔐 GROQ API FROM STREAMLIT SECRETS
# ===============================
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ===============================
# 🧠 AI CORE
# ===============================
def ai(prompt):
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.75
    )
    return response.choices[0].message.content.strip()

# ===============================
# 📘 PRODUCT GENERATOR
# ===============================
def generate_product(niche):
    title = ai(f"Generate a powerful ebook title for niche: {niche}")
    subtitle = ai(f"Generate a subtitle for this ebook: {title}")

    ebook = ai(f"""
Write a premium short ebook.

Title: {title}
Subtitle: {subtitle}
Niche: {niche}

Structure:
- Introduction
- 5 Actionable Chapters
- Practical Tips or Exercises
- Conclusion
- Strong Call To Action

Tone: Professional, inspirational
Language: English
""")

    hotmart = ai(f"""
Write a high-converting Hotmart product description.

Title: {title}
Subtitle: {subtitle}
Niche: {niche}

Include:
- Emotional hook
- Benefits (bullet points)
- Who this is for
- Transformation promise
- Strong CTA

Language: English
""")

    cover_prompt = ai(f"""
Create a professional AI image prompt for an ebook cover.

Book title: {title}
Niche: {niche}
Style: Minimal, premium, bestseller, digital product
""")

    return title, subtitle, ebook, hotmart, cover_prompt

# ===============================
# 📄 PDF CREATOR
# ===============================
def create_pdf(path, title, subtitle, content):
    pdf = SimpleDocTemplate(path)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(title, styles["Title"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph(subtitle, styles["Italic"]))
    story.append(Spacer(1, 20))

    for line in content.split("\n"):
        story.append(Paragraph(line, styles["Normal"]))
        story.append(Spacer(1, 6))

    pdf.build(story)

# ===============================
# 📥 FILE READER
# ===============================
def read_file(path):
    with open(path, "rb") as f:
        return f.read()

# ===============================
# 🌐 STREAMLIT UI
# ===============================
st.set_page_config(page_title="AUTO MONEY MODE", layout="centered")

st.title("🔥 AUTO MONEY MODE – AI BOOK FACTORY")
st.markdown("Generate **ready-to-sell ebooks + Hotmart copy + cover prompts** in one click.")

niche = st.text_input("🎯 Enter Niche", "Spiritual Awakening & Energy Vibration")
books = st.number_input("📚 Number of Books", min_value=1, max_value=5, value=1)

if st.button("🚀 GENERATE PRODUCTS"):
    if not niche:
        st.error("Please enter a niche.")
    else:
        with st.spinner("AI is creating your digital products..."):
            for i in range(1, books + 1):
                title, subtitle, ebook, hotmart, cover = generate_product(niche)

                folder = f"PRODUCT_{i}_{title.replace(' ', '_')}"
                os.makedirs(folder, exist_ok=True)

                pdf_path = f"{folder}/{title}.pdf"
                create_pdf(pdf_path, title, subtitle, ebook)

                st.success(f"✅ Product {i} Ready")
                st.subheader(title)

                # 📘 PDF DOWNLOAD
                st.download_button(
                    label="📘 Download Ebook PDF",
                    data=read_file(pdf_path),
                    file_name=f"{title}.pdf",
                    mime="application/pdf"
                )

                # 🛒 HOTMART COPY DOWNLOAD
                st.download_button(
                    label="🛒 Download Hotmart Description",
                    data=hotmart,
                    file_name="hotmart_description.txt",
                    mime="text/plain"
                )

                # 🎨 COVER PROMPT DOWNLOAD
                st.download_button(
                    label="🎨 Download Cover Prompt",
                    data=cover,
                    file_name="cover_prompt.txt",
                    mime="text/plain"
                )

                st.divider()

        st.balloons()
