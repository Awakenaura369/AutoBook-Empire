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
# 🧠 AI CORE (UPDATED TO WORKING MODELS)
# ===============================
def ai(prompt, model_type="fast"):
    """
    استعمال أحدث موديلات Groq المتاحة حالياً
    """
    # عزلنا الموديلات اللي خدامين 100% دابا
    model = "llama-3.1-8b-instant" if model_type == "fast" else "llama-3.3-70b-versatile"
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a world-class digital product creator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        # هاد السطر غيوريك الأرور الحقيقي إلا وقعات شي حاجة
        st.error(f"Groq API Error: {e}")
        return f"Error with model {model}"

# ===============================
# 📘 PRODUCT GENERATOR
# ===============================
def generate_product(niche):
    # نستخدم الموديل السريع للعناوين
    title = ai(f"Generate a short, powerful ebook title for niche: {niche}", "fast")
    subtitle = ai(f"Generate a catchy subtitle for this ebook: {title}", "fast")

    # نستخدم الموديل القوي 70b لكتابة الكتاب باش يجي جودة عالية
    ebook = ai(f"""
Write a premium short ebook for niche: {niche}.
Title: {title}
Subtitle: {subtitle}

Structure:
- Introduction
- 3 Actionable Chapters
- Practical Tips
- Conclusion
- Strong CTA
""", "smart")

    hotmart = ai(f"Write a high-converting Hotmart description for: {title}", "fast")
    cover_prompt = ai(f"AI image prompt for ebook cover: {title}", "fast")

    return title, subtitle, ebook, hotmart, cover_prompt

# ===============================
# 📄 PDF CREATOR (STAYS THE SAME)
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

def read_file(path):
    with open(path, "rb") as f:
        return f.read()

# ===============================
# 🌐 STREAMLIT UI
# ===============================
st.set_page_config(page_title="AUTO MONEY MODE", layout="centered")
st.title("🔥 AUTO BOOK FACTORY (v2.0)")

niche = st.text_input("🎯 Enter Niche", "Passive Income Strategies")
books = st.number_input("📚 Number of Books", 1, 5, 1)

if st.button("🚀 GENERATE PRODUCTS"):
    if not niche:
        st.error("Please enter a niche.")
    else:
        with st.spinner("Creating content with Llama 3.3 & 3.1..."):
            for i in range(1, int(books) + 1):
                title, subtitle, ebook, hotmart, cover = generate_product(niche)

                # تأكد أن العنوان ليس فيه خطأ
                if "Error" in title:
                    st.error("Failed to connect to Groq. Check your API Key.")
                    break

                folder = f"PRODUCT_{i}"
                os.makedirs(folder, exist_ok=True)
                pdf_path = f"{folder}/ebook.pdf"
                create_pdf(pdf_path, title, subtitle, ebook)

                st.success(f"✅ Ready: {title}")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.download_button("📘 PDF", read_file(pdf_path), f"book_{i}.pdf")
                with col2:
                    st.download_button("🛒 Copy", hotmart, f"copy_{i}.txt")
                with col3:
                    st.download_button("🎨 Cover", cover, f"prompt_{i}.txt")
                st.divider()
        st.balloons()
