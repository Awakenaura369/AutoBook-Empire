import streamlit as st
from groq import Groq
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib import colors
import re

# ===============================
# 🔐 API & ENGINE (Llama 3.3 70b)
# ===============================
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def ai(prompt, model_type="smart"):
    # استعمال الموديل الأقوى لضمان العمق وعدم السطحية
    model = "llama-3.3-70b-versatile"
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a senior business expert. Use real-world examples, numbers, and actionable strategies. No conversational filler."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=4000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

# ===============================
# 🧹 CLEANER (ANTI-FRCHA)
# ===============================
def clean_pro(text):
    t = text.replace("**", "").replace("###", "").replace("---", "")
    t = re.sub(r"(?i)^(here is|certainly|sure|based on|i will|i suggest).*?[:\n]", "", t).strip()
    return t

# ===============================
# 📄 MASTERPIECE PDF CREATOR
# ===============================
def create_masterpiece_pdf(path, title, subtitle, intro, chapters_data):
    pdf = SimpleDocTemplate(path)
    styles = getSampleStyleSheet()
    
    # ستايلات الألوان والاحترافية
    title_style = ParagraphStyle('T', parent=styles['Title'], fontSize=30, textColor=colors.navy, alignment=TA_CENTER)
    chap_style = ParagraphStyle('C', parent=styles['Heading1'], fontSize=20, textColor=colors.darkblue)
    body_style = ParagraphStyle('B', parent=styles['Normal'], alignment=TA_JUSTIFY, fontSize=11, leading=15)
    box_style = ParagraphStyle('Box', parent=styles['Normal'], fontSize=10, textColor=colors.whitesmoke, backColor=colors.darkslategray, borderPadding=10)

    story = [Spacer(1, 200), Paragraph(clean_pro(title), title_style), Paragraph(clean_pro(subtitle), styles["Italic"]), PageBreak()]

    # Introduction
    story.append(Paragraph("Introduction", chap_style))
    for p in clean_pro(intro).split("\n\n"):
        story.append(Paragraph(p, body_style)); story.append(Spacer(1, 10))
    story.append(PageBreak())

    # Chapters
    for i, chap in enumerate(chapters_data):
        story.append(Paragraph(f"Chapter {i+1}: {chap['title']}", chap_style))
        story.append(Spacer(1, 10))
        for p in clean_pro(chap['content']).split("\n\n"):
            story.append(Paragraph(p, body_style)); story.append(Spacer(1, 8))
        
        # Action Plan Box (القيمة المضافة)
        story.append(Spacer(1, 15))
        story.append(Paragraph("🛠 ACTION STEPS:", ParagraphStyle('H', parent=body_style, textColor=colors.gold)))
        story.append(Paragraph(clean_pro(chap['action']), box_style))
        story.append(PageBreak())
        
    pdf.build(story)

# ===============================
# 🌐 FULL UI (WITH HOTMART PREVIEW)
# ===============================
st.set_page_config(page_title="SNIPER FACTORY PRO", layout="wide")
tab1, tab2 = st.tabs(["🏗️ Build Masterpiece", "🎯 Facebook Sniper"])

with tab1:
    st.title("🏆 HIGH-VALUE BOOK FACTORY")
    niche = st.text_input("🎯 Niche", "Passive Income Strategies")
    
    if st.button("🚀 GENERATE MASTERPIECE"):
        with st.status("🛠️ Building high-value content...") as s:
            # 1. Title & Intro
            title = ai(f"One elite title for {niche}. No meta-talk.", "fast")
            subtitle = ai(f"One professional subtitle for {title}", "fast")
            intro = ai(f"Write a 500-word deep intro for '{title}'. No intro sentences.", "smart")
            
            # 2. Chapters
            chapters_data = []
            for i in range(1, 6):
                st.write(f"✍️ Writing Chapter {i} + Case Study...")
                ch_title = ai(f"Chapter {i} title for '{title}'", "fast")
                content = ai(f"Deep content for '{ch_title}'. Include a detailed Case Study.", "smart")
                action = ai(f"5-step action plan for '{ch_title}'", "fast")
                chapters_data.append({"title": ch_title, "content": content, "action": action})
            
            # 3. Marketing (Hotmart)
            hotmart = ai(f"Write a high-converting Hotmart sales description for {title}. No meta-talk.", "smart")
            cover = ai(f"AI image prompt for {title} cover", "fast")
            
            pdf_p = "masterpiece.pdf"
            create_masterpiece_pdf(pdf_p, title, subtitle, intro, chapters_data)
            s.update(label="✅ Ready!", state="complete")

        # --- الـ Preview والتحميل (الرجوع للساحة!) ---
        st.success(f"Successfully Created: {title}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            with open(pdf_p, "rb") as f: st.download_button("📘 Download Ebook", f, "ebook.pdf")
        with col2:
            st.download_button("🛒 Download Hotmart Copy", hotmart, "hotmart.txt")
        with col3:
            st.download_button("🎨 Download Cover Prompt", cover, "cover.txt")

        # عرض هوتمارت فـ الشاشة
        st.divider()
        st.subheader("🛒 Hotmart Sales Page Preview")
        st.info(hotmart) # هاهو رجع البريفيو!

with tab2:
    st.title("🎯 FACEBOOK SNIPER")
    ad_desc = st.text_input("Product for hooks:", niche)
    if st.button("🔥 Generate Hooks"):
        hooks = ai(f"5 aggressive FB hooks for {ad_desc}", "smart")
        st.markdown(hooks)
