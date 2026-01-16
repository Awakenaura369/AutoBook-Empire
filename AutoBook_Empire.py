import streamlit as st
from groq import Groq
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib import colors
import re

# [2026-01-10] AI engine is Groq
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def ai(prompt, model_type="smart"):
    model = "llama-3.3-70b-versatile" # الموديل الأقوى لتفادي السطحية
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": "You are an expert author. Write deep, actionable content with case studies. No intro filler."},
                      {"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=4000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

def clean_pro(text):
    t = text.replace("**", "").replace("###", "").replace("---", "")
    t = re.sub(r"(?i)^(here is|certainly|sure|based on|i will|i suggest).*?[:\n]", "", t).strip()
    return t

# ===============================
# 📄 FIXED PDF CREATOR (NO OVERLAP)
# ===============================
def create_masterpiece_pdf(path, title, subtitle, intro, chapters_data):
    pdf = SimpleDocTemplate(path)
    styles = getSampleStyleSheet()
    
    # تحسين الـ Styles لمنع التداخل
    title_style = ParagraphStyle('T', parent=styles['Title'], fontSize=26, textColor=colors.navy, alignment=TA_CENTER, leading=32)
    sub_style = ParagraphStyle('S', parent=styles['Italic'], fontSize=12, textColor=colors.grey, alignment=TA_CENTER, leading=16)
    chap_style = ParagraphStyle('C', parent=styles['Heading1'], fontSize=20, textColor=colors.darkblue, spaceBefore=30, spaceAfter=20)
    body_style = ParagraphStyle('B', parent=styles['Normal'], alignment=TA_JUSTIFY, fontSize=11, leading=16)
    box_style = ParagraphStyle('Box', parent=styles['Normal'], fontSize=10, textColor=colors.whitesmoke, backColor=colors.darkslategray, borderPadding=10)

    story = []
    
    # 1. صفحة الغلاف مع مساحات كافية
    story.append(Spacer(1, 150))
    story.append(Paragraph(clean_pro(title), title_style))
    story.append(Spacer(1, 20)) # مسافة أمان لمنع التداخل
    story.append(Paragraph(clean_pro(subtitle), sub_style))
    story.append(PageBreak())

    # 2. المقدمة + البونص (قائمة الأدوات)
    story.append(Paragraph("Introduction & Success Roadmap", chap_style))
    for p in clean_pro(intro).split("\n\n"):
        story.append(Paragraph(p, body_style))
        story.append(Spacer(1, 10))
    
    # إضافة Bonus: قائمة الأدوات لزيادة القيمة
    story.append(Spacer(1, 20))
    story.append(Paragraph("🎁 BONUS: ESSENTIAL TOOLS LIST", ParagraphStyle('H', parent=body_style, textColor=colors.red)))
    tools_list = "1. Google Analytics (Data) | 2. Canva (Design) | 3. Meta Ads Manager (Traffic) | 4. ChatGPT/Groq (Content)"
    story.append(Paragraph(tools_list, box_style))
    story.append(PageBreak())

    # 3. الفصول مع Action Plans
    for i, chap in enumerate(chapters_data):
        story.append(Paragraph(f"Chapter {i+1}: {chap['title']}", chap_style))
        for p in clean_pro(chap['content']).split("\n\n"):
            story.append(Paragraph(p, body_style))
            story.append(Spacer(1, 8))
        
        # Action Plan
        story.append(Spacer(1, 15))
        story.append(Paragraph("✅ YOUR ACTION PLAN:", ParagraphStyle('H', parent=body_style, textColor=colors.gold)))
        story.append(Paragraph(clean_pro(chap['action']), box_style))
        story.append(PageBreak())
        
    pdf.build(story)

# ===============================
# 🌐 UI SETUP
# ===============================
st.set_page_config(page_title="SNIPER FACTORY", layout="wide")
t1, t2 = st.tabs(["📚 Book Factory", "🎯 Facebook Sniper"])

with t1:
    st.title("🏆 HIGH-VALUE BOOK FACTORY")
    niche = st.text_input("🎯 Niche", "E-commerce Growth")
    if st.button("🚀 GENERATE MASTERPIECE"):
        with st.status("🛠️ Engineering...") as s:
            title = ai(f"One elite title for {niche}", "fast")
            subtitle = ai(f"One subtitle for {title}", "fast")
            intro = ai(f"Deep intro for '{title}'", "smart")
            chapters_data = []
            for i in range(1, 6):
                ch_t = ai(f"Chapter {i} title for '{title}'", "fast")
                cont = ai(f"Deep content for '{ch_t}' with a Case Study.", "smart")
                act = ai(f"5-step action checklist for '{ch_t}'", "fast")
                chapters_data.append({"title": ch_t, "content": cont, "action": act})
            hotmart = ai(f"Sales copy for {title}", "smart")
            cover = ai(f"AI image prompt for {title}", "fast")
            pdf_p = "masterpiece.pdf"
            create_masterpiece_pdf(pdf_p, title, subtitle, intro, chapters_data)
            s.update(label="✅ Ready!", state="complete")

        st.success(f"Created: {title}")
        c1, c2, c3 = st.columns(3)
        with c1: 
            with open(pdf_p, "rb") as f: st.download_button("📘 Download Ebook", f, "ebook.pdf")
        with c2: st.download_button("🛒 Hotmart Copy", hotmart, "hotmart.txt")
        with c3: st.download_button("🎨 Cover Prompt", cover, "cover.txt")
        st.divider()
        st.subheader("🛒 Hotmart Preview")
        st.info(hotmart)

with t2:
    # [2026-01-13] Facebook Sniper tab
    st.title("🎯 FACEBOOK SNIPER")
    if st.button("🔥 Generate Hooks"):
        st.write(ai(f"5 aggressive FB hooks for {niche}", "smart"))
