import os
import streamlit as st
from groq import Groq
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ===============================
# 🔐 GROQ API FROM STREAMLIT SECRETS
# ===============================
# تأكد أنك حاط GROQ_API_KEY في Streamlit Secrets
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ===============================
# 🧠 AI CORE (FIXED FOR BAD REQUEST)
# ===============================
def ai(prompt):
    """
    نسخة محسنة لتفادي أخطاء BadRequest و NotFound
    """
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",  # الموديل المستقر والسريع
            messages=[
                {"role": "system", "content": "You are a professional digital product creator and copywriter."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2500  # كافية لإنشاء فصول الكتاب
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Groq API Error: {e}")
        return "Error generating content."

# ===============================
# 📘 PRODUCT GENERATOR
# ===============================
def generate_product(niche):
    # إنشاء العنوان والعنوان الفرعي
    title = ai(f"Generate a short, powerful ebook title for niche: {niche}")
    subtitle = ai(f"Generate a catchy subtitle for this ebook: {title}")

    # إنشاء محتوى الكتاب
    ebook = ai(f"""
Write a premium short ebook for niche: {niche}.
Title: {title}
Subtitle: {subtitle}

Structure:
- Introduction
- 3 Actionable Chapters
- Practical Tips or Exercises
- Conclusion
- Strong Call To Action

Tone: Professional, inspirational, concise
Language: English
""")

    # وصف المنتج لـ Hotmart
    hotmart = ai(f"""
Write a high-converting Hotmart product description for:
Title: {title}
Niche: {niche}

Include: Benefits, target audience, and a strong CTA.
Language: English
""")

    # أمر الذكاء الاصطناعي للغلاف
    cover_prompt = ai(f"Create a professional AI image prompt for an ebook cover titled '{title}' in the {niche} niche. Minimalist and premium style.")

    return title, subtitle, ebook, hotmart, cover_prompt

# ===============================
# 📄 PDF CREATOR
# ===============================
def create_pdf(path, title, subtitle, content):
    pdf = SimpleDocTemplate(path)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(title, styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(subtitle, styles["Italic"]))
    story.append(Spacer(1, 24))

    for line in content.split("\n"):
        if line.strip():
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
        with st.spinner("AI is crafting your digital empire..."):
            for i in range(1, int(books) + 1):
                title, subtitle, ebook, hotmart, cover = generate_product(niche)

                # تنظيف اسم الملف من الرموز غير المسموح بها
                clean_title = "".join(x for x in title if x.isalnum() or x in "._- ")
                folder = f"PRODUCT_{i}"
                os.makedirs(folder, exist_ok=True)

                pdf_path = f"{folder}/ebook.pdf"
                create_pdf(pdf_path, title, subtitle, ebook)

                st.success(f"✅ Product {i}: {title} Ready!")
                
                # أزرار التحميل
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.download_button("📘 Download PDF", read_file(pdf_path), f"{clean_title}.pdf", "application/pdf")
                with col2:
                    st.download_button("🛒 Hotmart Copy", hotmart, f"hotmart_{i}.txt", "text/plain")
                with col3:
                    st.download_button("🎨 Cover Prompt", cover, f"cover_{i}.txt", "text/plain")
                
                st.divider()

        st.balloons()
