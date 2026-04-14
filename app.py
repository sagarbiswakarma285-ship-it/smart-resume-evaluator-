import streamlit as st
import string
import re 
import PyPDF2 

# ==========================================
# 1. APP SETUP & SIDEBAR
# ==========================================
st.set_page_config(page_title="Smart Resume Evaluator", page_icon="🎯", layout="wide", initial_sidebar_state="collapsed")

if 'user_profile' not in st.session_state:
    st.session_state['user_profile'] = None

# FIXED CSS VARIABLES (Dark Theme Only, No Toggle)
sidebar_bg = "#1E212B" 
dynamic_text = "#FFFFFF" 
box_bg = "#1A1C23"
border_col = "#475569" 
bg_image = "linear-gradient(rgba(15, 23, 42, 0.75), rgba(15, 23, 42, 0.95)), url('https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1600&q=80')"

st.markdown(f"""
    <style>
        .stDeployButton, .stAppDeployButton {{display:none !important;}}
        #MainMenu {{visibility: hidden;}}
        header[data-testid="stHeader"] {{height: 2.5rem !important; background: transparent !important;}} 
        
        /* Layout Full Screen Fit */
        .block-container {{ padding-top: 0.5rem !important; padding-bottom: 0.5rem !important; max-width: 100% !important; }}
        [data-testid="stAppViewContainer"] {{ background-color: #0E1117 !important; }}

        /* Sidebar Visibility */
        [data-testid="stSidebarHeader"] button {{ opacity: 1 !important; visibility: visible !important; }}
        [data-testid="stSidebarHeader"] svg {{ fill: {dynamic_text} !important; color: {dynamic_text} !important; }}
        [data-testid="stSidebar"] {{ background-color: {sidebar_bg} !important; border-right: 1px solid {border_col} !important; }}
        [data-testid="stSidebar"] > div:first-child {{ background-color: {sidebar_bg} !important; }}
        [data-testid="stSidebarHeader"] {{ background-color: {sidebar_bg} !important; }}

        /* Dividers & Borders */
        hr {{ border-top: 1px solid {border_col} !important; border-bottom: none !important; }}
        [data-testid="stExpander"] {{ border: 1px solid {border_col} !important; border-radius: 8px !important; background-color: {box_bg} !important; }}
        [data-testid="stSidebar"] svg, [data-testid="stExpander"] svg {{ fill: {dynamic_text} !important; color: {dynamic_text} !important; }}

        /* ==========================================
           FIXED & BEAUTIFUL MODERN BUTTON STYLING
           ========================================== */
           
        /* Secondary Action Buttons (Login, Logout, Browse Files) */
        button[kind="secondary"] {{ 
            background-color: transparent !important; 
            color: #60A5FA !important; 
            border: 1.5px solid #3B82F6 !important; 
            border-radius: 8px !important; 
            font-weight: 600 !important; 
            transition: all 0.3s ease !important;
            padding: 8px 16px !important;
            white-space: nowrap !important; /* FIXED: Text kabhi tootega nahi */
            height: 42px !important; /* Perfect Symmetry */
        }}
        button[kind="secondary"]:hover {{ 
            background-color: rgba(59, 130, 246, 0.1) !important; 
            border-color: #93C5FD !important; 
            color: #93C5FD !important;
            transform: translateY(-2px) !important;
        }}

        /* Primary Action Buttons (Sign Up, Evaluate) */
        button[kind="primary"] {{ 
            background: linear-gradient(135deg, #2563EB, #3B82F6) !important; 
            color: white !important; 
            border: none !important; 
            border-radius: 8px !important; 
            font-weight: 600 !important; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.2) !important; 
            transition: all 0.3s ease !important;
            letter-spacing: 0.5px !important;
            padding: 8px 16px !important;
            white-space: nowrap !important; /* FIXED: Text kabhi tootega nahi */
            height: 42px !important; /* Perfect Symmetry */
        }}
        button[kind="primary"]:hover {{ 
            background: linear-gradient(135deg, #1D4ED8, #2563EB) !important; 
            box-shadow: 0 6px 12px rgba(37, 99, 235, 0.4) !important; 
            transform: translateY(-2px) !important; 
        }}

        /* Text Colors */
        .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown label, .stMarkdown li, .stMarkdown span {{ color: {dynamic_text} !important; }}
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p {{ color: {dynamic_text} !important; }}
        
        /* Input Boxes */
        .stTextArea textarea, .stTextInput input {{ background-color: {box_bg} !important; color: {dynamic_text} !important; border: 1px solid {border_col} !important; caret-color: {dynamic_text} !important; }}
        
        /* THE RESTORED STARRY BANNER */
        .corporate-header {{ position: relative; background-image: {bg_image}; background-size: cover; background-position: center; border-radius: 16px; padding: 25px 40px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 15px 35px -10px rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.1); margin-bottom: 10px; overflow: hidden; }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. TOP RIGHT NAV BAR
# ==========================================
nav_col1, nav_col2, nav_col3 = st.columns([8.2, 0.9, 0.9])
with nav_col2:
    if st.button("Login", use_container_width=True, key="login_btn"):
        st.toast("Login system will be connected soon!", icon="🛠️")
with nav_col3:
    if st.button("Sign Up", type="primary", use_container_width=True, key="signup_btn"):
        st.toast("Sign Up system will be connected soon!", icon="🛠️")

# ==========================================
# 3. HIDDEN SIDEBAR & FULL PROFILE FORM
# ==========================================
with st.sidebar:
    st.title("⚙️ App Settings")
    st.markdown("---")
    
    with st.expander("👤 My Profile"):
        st.write("Fill your details. I will use this to auto-fill missing info in your resume.")
        with st.form("profile_form"):
            st.markdown("**Basic Details**")
            p_name = st.text_input("Full Name (e.g., Sagar Biswakarma)")
            p_email = st.text_input("Email ID")
            p_phone = st.text_input("Phone Number")
            p_dob = st.date_input("Date of Birth")
            p_fname = st.text_input("Father's Name")
            p_address = st.text_area("Address")
            
            st.markdown("**Education Details**")
            col1, col2 = st.columns(2)
            p_10th = col1.text_input("10th Passing Year & %")
            p_12th = col2.text_input("12th Passing Year & %")
            p_college = st.text_input("College Degree & Passing Year")
            p_other_edu = st.text_input("Other Courses/Certifications")
            
            st.markdown("**Extra Details**")
            p_aim = st.text_input("Career Aim / Objective")
            p_hobbies = st.text_input("Hobbies")
            p_extra = st.text_area("Extra Curricular Activities")
            
            saved = st.form_submit_button("💾 Save My Profile", type="primary")
            if saved:
                if p_name and p_email:
                    st.session_state['user_profile'] = {
                        "name": p_name, "email": p_email, "phone": p_phone, "dob": str(p_dob),
                        "fname": p_fname, "address": p_address, "10th": p_10th, "12th": p_12th,
                        "college": p_college, "other_edu": p_other_edu, "aim": p_aim, "hobbies": p_hobbies, "extra": p_extra
                    }
                    st.success("✅ Profile Saved! I will now remember you.")
                else:
                    st.error("⚠️ Please fill at least Name and Email to save.")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
        st.toast("Logout feature will be live in Phase 2!", icon="🔒")

# ==========================================
# 4. MASSIVE UNIVERSAL KNOWLEDGE BASE 
# ==========================================
CATEGORIES = {
    "💻 Software Development": ["python", "c++", "java", "javascript", "react", "node.js", "angular", "html", "css", "django", "spring boot", "ruby", "php", "rest api", "graphql"],
    "📊 Data Science & AI": ["machine learning", "deep learning", "nlp", "artificial intelligence", "data science", "algorithms", "sas programming", "sas", "data analytics", "tensorflow", "pytorch", "computer vision", "statistics", "matplotlib", "scikit-learn"],
    "☁️ Cloud & DevOps": ["aws", "azure", "gcp", "cloud computing", "docker", "kubernetes", "jenkins", "ci/cd", "linux", "bash", "terraform", "ansible"],
    "🛡️ Cybersecurity & Networks": ["cybersecurity", "blockchain", "ethical hacking", "penetration testing", "firewalls", "cryptography", "ccna", "networking", "tcp/ip"],
    "⚙️ Core Engineering": ["autocad", "solidworks", "thermodynamics", "manufacturing", "matlab", "cad", "cam", "structural engineering", "power systems", "robotics", "circuit design", "vlsi", "embedded systems"],
    "📈 Business & Finance": ["business analysis", "business analytics", "accounting", "tally", "taxation", "marketing", "sales", "finance", "economics", "hr", "digital marketing", "supply chain", "seo", "clinical trial analysis", "b2b", "b2c", "agile", "scrum", "data entry"],
    "⚕️ Medical & Pharma": ["pharmacology", "clinical research", "pharmacovigilance", "drug safety", "anatomy", "biochemistry", "microbiology", "nursing", "pathology", "physiology", "healthcare"],
    "🎨 UI/UX & Design": ["graphic design", "fashion design", "animation", "fine arts", "video editing", "photography", "ui/ux", "figma", "adobe xd", "wireframing", "prototyping", "copywriting", "creative writing"],
    "🛠️ Universal Tools & DB": ["sql", "mysql", "mongodb", "postgresql", "git", "github", "excel", "powerbi", "tableau", "word", "powerpoint", "photoshop", "canva", "jira", "confluence"],
    "🤝 Professional Soft Skills": ["english proficiency", "english", "communication", "business communication", "teamwork", "leadership", "management", "problem solving", "analytical", "motivated", "presentation", "time management", "adaptability", "critical thinking"]
}

SOFT_SKILLS_CATEGORY = "🤝 Professional Soft Skills"

# ==========================================
# 5. SMART ENGINES & PDF HELPER
# ==========================================
def extract_text_from_file(uploaded_file):
    text = ""
    if uploaded_file.name.endswith('.pdf'):
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        except Exception as e:
            pass
    else:
        text = uploaded_file.getvalue().decode("utf-8")
    return text

def clean_job_description(text):
    lines = text.lower().split('\n')
    extracted_text = []
    is_target_section = False
    found_any_target = False
    
    target_keywords = ["skill(s) required", "skills required", "key responsibilities", "responsibilit", "qualifications", "must have", "what we are looking for", "what you will do", "role requirements"]
    stop_keywords = ["earn certification", "earn certifications", "certifications in these", "what you will learn", "perks", "benefits", "salary", "ctc", "probation", "about deepthought", "about the company", "about us", "who can apply", "how to apply", "number of openings", "about the job"]
    
    for line in lines:
        line_clean = line.strip()
        if not line_clean: continue
        
        hit_stop = False
        for kw in stop_keywords:
            if kw in line_clean:
                is_target_section = False 
                hit_stop = True
                break
                
        if hit_stop:
            continue 
            
        for kw in target_keywords:
            if kw in line_clean and len(line_clean) < 60:
                is_target_section = True 
                found_any_target = True
                break
                
        if is_target_section:
            extracted_text.append(line_clean)
            
    if not found_any_target: 
        fallback_text = []
        for line in lines:
            line_clean = line.strip()
            if any(kw in line_clean for kw in stop_keywords) or line_clean.startswith("learn "):
                continue 
            fallback_text.append(line_clean) 
        return " ".join(fallback_text)
        
    return " ".join(extracted_text)

def extract_only_skills(text):
    text = text.lower()
    found_skills = {cat: set() for cat in CATEGORIES.keys()}
    for category_name, keyword_list in CATEGORIES.items():
        for kw in keyword_list:
            if "+" in kw or "#" in kw:
                if kw in text:
                    found_skills[category_name].add(kw.title())
            else:
                pattern = r'\b' + kw + r'\b'
                if re.search(pattern, text):
                    found_skills[category_name].add(kw.title())
    return found_skills

# ==========================================
# 7. RESPONSIVE USER INPUTS
# ==========================================
top_dashboard = st.empty() 

st.markdown("### 📝 Enter Your Details")
col_input1, col_input2 = st.columns(2)

resume_text, job_description = "", ""

with col_input1:
    st.markdown("**Your Resume:**")
    tab1, tab2 = st.tabs(["📝 Paste Text", "📂 Upload File"])
    with tab1: res_text_input = st.text_area("Or Paste Resume Text:", height=80, key="res_text")
    with tab2: res_file = st.file_uploader("Upload PDF/TXT (Max 5MB)", type=["pdf", "txt"], key="res_upload")
    if res_file is not None:
        resume_text = extract_text_from_file(res_file)
    elif res_text_input:
        resume_text = res_text_input

with col_input2:
    st.markdown("**Job Description:**")
    tab3, tab4 = st.tabs(["📝 Paste Text", "📂 Upload File"])
    with tab3: jd_text_input = st.text_area("Or Paste Job Description Text:", height=80, key="jd_text")
    with tab4: jd_file = st.file_uploader("Upload PDF/TXT (Max 5MB)", type=["pdf", "txt"], key="jd_upload")
    if jd_file is not None:
        job_description = extract_text_from_file(jd_file)
    elif jd_text_input:
        job_description = jd_text_input

st.markdown("<p style='text-align: center; color: gray; margin-top: 0px; margin-bottom: 2px;'><i>Click below to check your score 👇</i></p>", unsafe_allow_html=True)

evaluate_clicked = st.button("🚀 Evaluate Resume", type="primary", use_container_width=True)

# ==========================================
# 8. CORE LOGIC & SMART FIELD DETECTION
# ==========================================
score, tech_score = None, 0
matched_skills, missing_skills = {}, {}
dominant_job_field = "General / Unspecified"

if evaluate_clicked and resume_text and job_description:
    cleaned_jd = clean_job_description(job_description)
    resume_skills = extract_only_skills(resume_text)
    job_skills = extract_only_skills(cleaned_jd)

    total_job_skill_count = 0
    total_matched_skill_count = 0
    tech_job_skill_count = 0
    tech_matched_skill_count = 0
    
    category_weights = {}

    for cat in CATEGORIES:
        matched_skills[cat] = resume_skills[cat].intersection(job_skills[cat])
        missing_skills[cat] = job_skills[cat].difference(resume_skills[cat])
        
        cat_total = len(job_skills[cat])
        cat_matched = len(matched_skills[cat])
        
        total_job_skill_count += cat_total
        total_matched_skill_count += cat_matched
        
        if cat not in [SOFT_SKILLS_CATEGORY, "🛠️ Universal Tools & DB"]:
            category_weights[cat] = cat_total
            
        if cat != SOFT_SKILLS_CATEGORY:
            tech_job_skill_count += cat_total
            tech_matched_skill_count += cat_matched

    if category_weights and max(category_weights.values()) > 0:
        dominant_job_field = max(category_weights, key=category_weights.get)

    if total_job_skill_count > 0:
        score = int((total_matched_skill_count / total_job_skill_count) * 100)
    else:
        st.warning("⚠️ I couldn't find core skills. Make sure requirements are clear.")
        score = 0
        
    if tech_job_skill_count > 0:
        tech_score = int((tech_matched_skill_count / tech_job_skill_count) * 100)

# ==========================================
# 9. DYNAMIC CORPORATE HEADER
# ==========================================
if score is None:
    status, color, icon = "Match Scoreboard", dynamic_text, "--" 
    subtext = "Paste your details and click Evaluate to see your score."
    score_bg = "rgba(248, 250, 252, 0.05)"
    score_border = "rgba(226, 232, 240, 0.2)"
elif score == 100:
    status, color, icon = "Perfect Match!", "#34D399", f"{score}"
    subtext = "Your resume is perfect! You can go ahead with this."
    score_bg = "rgba(16, 185, 129, 0.15)"
    score_border = "#34D399"
elif score >= 80:
    status, color, icon = "Great Score!", "#FBBF24", f"{score}"
    subtext = "Score generated! Scroll down for a 100% perfect resume 👇"
    score_bg = "rgba(251, 191, 36, 0.15)"
    score_border = "#FBBF24"
else:
    status, color, icon = "Your Match Score", "#60A5FA", f"{score}"
    subtext = "Score generated! Scroll down for AI suggestions to match requirements 👇"
    score_bg = "rgba(37, 99, 235, 0.15)"
    score_border = "#60A5FA"

banner_html = f"""<div class="corporate-header">
<div style="z-index: 1;">
<h1 style="color: {dynamic_text} !important; margin:0; font-family: sans-serif; font-size: 38px; font-weight: 800; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">
Smart Resume <span style="color: #3B82F6 !important;">Evaluator</span>
</h1>
<p style="color: {dynamic_text} !important; margin: 8px 0 0 0; font-size: 16px; font-weight: 500; text-shadow: 0 1px 2px rgba(0,0,0,0.2); opacity: 0.8;">
Instantly compare your resume with any Job Description to find missing skills.
</p>
</div>
<div style="display: flex; align-items: center; z-index: 1;">
<div style="text-align: right; margin-right: 25px;">
<h3 style="color: {color} !important; margin:0; font-family: sans-serif; font-size: 22px; font-weight: 700; text-shadow: 0 1px 2px rgba(0,0,0,0.2);">{status}</h3>
<p style="color: {dynamic_text} !important; margin:0; font-size: 14px; font-weight: 600; text-shadow: 0 1px 2px rgba(0,0,0,0.2); opacity: 0.8;">{subtext}</p>
</div>
<div style="width: 100px; height: 100px; min-width: 100px; min-height: 100px; flex-shrink: 0; border-radius: 50%; background: {score_bg}; display: flex; justify-content: center; align-items: baseline; color: {dynamic_text} !important; font-weight: 800; border: 3px solid {score_border}; padding-top: 28px; box-sizing: border-box; backdrop-filter: blur(8px); box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
<span style="color: {dynamic_text} !important; font-size: 32px;">{icon}</span><span style="color: {dynamic_text} !important; font-size: 16px; opacity: 0.8; margin-left: 2px;">/100</span>
</div>
</div>
</div>"""

top_dashboard.markdown(banner_html, unsafe_allow_html=True)

# ==========================================
# 10. RESULTS DISPLAY & SMART AI STRATEGY
# ==========================================
if score is not None:
    st.markdown("---")
    # SHORTENED: 1
    st.info(f"🧠 **AI Job Field Analysis:** This job perfectly matches the **{dominant_job_field}** field.")
    
    st.markdown("### 🎯 Hiring Probability & Strategic Advice")
    if tech_score == 100:
        # SHORTENED: 2
        st.success(f"🏆 **Technical Score: {tech_score}% | Status: PERFECT MATCH!**\nYou have all required technical skills. Prepare for the interview!")
    elif tech_score >= 60:
        # SHORTENED: 3
        st.success(f"🔥 **Technical Score: {tech_score}% | Status: HIGH CHANCES!**\nYou have a solid foundation. Add the missing skills below and apply.")
    elif tech_score >= 50:
        # SHORTENED: 4
        st.warning(f"⚖️ **Technical Score: {tech_score}% | Status: MODERATE CHANCES.**\nYou meet basic requirements. Learn the missing technical skills before interviewing.")
    else:
        # SHORTENED: 5
        st.error(f"⚠️ **Technical Score: {tech_score}% | Status: LOW CHANCES.**\nYou are missing key technical skills. Upskill before applying to avoid rejection.")

    st.markdown("---")
    st.markdown("### 📊 Skill Analysis by Category")
    col1, col2 = st.columns(2)
    with col1:
        st.success("**Perfect Matches (You have these skills):**")
        for cat, words in matched_skills.items():
            if words:
                st.markdown(f"**{cat}**")
                st.markdown(" ".join([f"`{w}`" for w in words]))
    with col2:
        st.error("**MUST-HAVE Missing Skills (You need to add/learn these):**")
        for cat, words in missing_skills.items():
            if words:
                st.markdown(f"**{cat}**")
                st.markdown(" ".join([f"`{w}`" for w in words]))

    if score < 100:
        st.markdown("---")
        st.markdown("### 💡 Suggestions & Auto-Updated Resume")
        
        all_missing_skills = [w for words in missing_skills.values() for w in words]
        
        profile = st.session_state.get('user_profile')
        is_my_resume = False
        missing_personal_injection = ""
        
        if profile and profile['name']:
            if profile['name'].lower() in resume_text.lower() or profile['email'].lower() in resume_text.lower():
                is_my_resume = True
        
        if is_my_resume:
            st.success(f"🕵️‍♂️ **AI Detective Match!** I recognize this is your resume ({profile['name']}).")
            missing_from_resume = []
            missing_data_to_inject = []
            
            if profile.get('phone') and str(profile['phone']) not in resume_text:
                missing_from_resume.append("Phone Number")
                missing_data_to_inject.append(f"Phone: {profile['phone']}")
            if profile.get('hobbies') and profile['hobbies'].lower() not in resume_text.lower():
                missing_from_resume.append("Hobbies")
                missing_data_to_inject.append(f"Hobbies: {profile['hobbies']}")
            if profile.get('college') and "college" not in resume_text.lower() and "university" not in resume_text.lower():
                missing_from_resume.append("College Details")
                missing_data_to_inject.append(f"College/Degree: {profile['college']}")
            if profile.get('extra') and len(profile['extra']) > 2 and profile['extra'][:10].lower() not in resume_text.lower():
                missing_from_resume.append("Extra Curricular Activities")
                missing_data_to_inject.append(f"Extra Curricular: {profile['extra']}")
            
            if missing_from_resume:
                # SHORTENED: 6
                st.warning(f"⚠️ **Profile Auto-Fill:** Adding missing details from your profile: **{', '.join(missing_from_resume)}**. You can remove them later if needed.")
                missing_personal_injection = "\n[ AI-ADDED MISSING PERSONAL DETAILS ]\n"
                for item in missing_data_to_inject:
                    missing_personal_injection += f"• {item}\n"
                missing_personal_injection += "\n"
            else:
                st.info("✅ Your uploaded resume contains all major personal details from your saved profile.")
        else:
            if all_missing_skills:
                # SHORTENED: 7
                st.info(f"ℹ️ **Guest Resume:** Missing skills detected: **{', '.join(all_missing_skills[:5])}**. I've added them below to match the job.")
            
        st.markdown("---")
        
        if tech_score == 0:
            # SHORTENED: 8
            st.warning("**⚠️ Honest Advice:** With a 0% technical match, consider learning these skills first.\n\n*I generated an updated resume below just in case you forgot to list them. Copy to MS Word.*")
        else:
            # SHORTENED: 9
            st.write("**Note:** Your original text is safe. I just added the missing skills. Copy this to MS Word!")
        
        ms_word_friendly_skills = f"\n[ AI-OPTIMIZED SKILLS FOR THIS JOB ]\n• Technical/Domain: {', '.join(all_missing_skills[:10])}\n• Tools/Cloud: {', '.join(list(matched_skills['🛠️ Universal Tools & DB'].intersection(job_skills['🛠️ Universal Tools & DB'])) + list(missing_skills['🛠️ Universal Tools & DB']))}\n• Soft Skills: {', '.join(list(matched_skills[SOFT_SKILLS_CATEGORY].intersection(job_skills[SOFT_SKILLS_CATEGORY])) + list(missing_skills[SOFT_SKILLS_CATEGORY]))}\n"
        
        if missing_personal_injection:
            ms_word_friendly_skills = missing_personal_injection + ms_word_friendly_skills
            
        if all_missing_skills or missing_personal_injection:
            if re.search(r'\bTECHNICAL SKILLS\b', resume_text, re.IGNORECASE):
                updated_resume = re.sub(r'(\bTECHNICAL SKILLS\b)', r'\1' + ms_word_friendly_skills, resume_text, count=1, flags=re.IGNORECASE)
            elif re.search(r'\bSKILLS\b', resume_text, re.IGNORECASE):
                updated_resume = re.sub(r'(\bSKILLS\b)', r'\1' + ms_word_friendly_skills, resume_text, count=1, flags=re.IGNORECASE)
            else:
                updated_resume = f"PROFESSIONAL UPDATES (AI-Optimized):\n{ms_word_friendly_skills}\n\n------------------------------\n" + resume_text
        else:
            updated_resume = resume_text

        st.code(updated_resume, language="text")