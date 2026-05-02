import streamlit as st
import json
from resume_parser import extract_text, parse_resume    

st.set_page_config(page_title="Resume Parser", page_icon="📄")

st.markdown("""
    <style>
        body, .stApp { background-color: #ddeeff; }
        h1 { color: #3b0764 !important; font-weight: 800; }
        .stCaptionContainer p, .stMarkdown p { color: #2d1b4e; }

        .section-heading {
            color: #3b0764;
            font-size: 1.1rem;
            font-weight: 700;
            margin: 18px 0 8px 0;
        }

        .card {
            background-color: #c8e0f8;
            border-left: 5px solid #5b21b6;
            border-radius: 10px;
            padding: 12px 16px;
            margin-bottom: 12px;
            color: #1a0533;
        }

        .pill {
            display: inline-block;
            background-color: #7c3aed;
            color: #ffffff;
            border-radius: 20px;
            padding: 4px 12px;
            margin: 3px;
            font-size: 0.82rem;
        }
    </style>
""", unsafe_allow_html=True)

st.title("📄 Resume Parser")
st.caption("Upload PDF or DOCX resume")

 
uploaded_file = st.file_uploader(
    "Upload your resume",
    type=["pdf", "docx"]
)

if uploaded_file:
    with st.spinner("Reading file..."):
        try:
            text = extract_text(uploaded_file)   
        except Exception as e:
            st.error(str(e))
            st.stop()

    if not text.strip():
        st.warning("Could not extract text.")
    else:
        with st.spinner("Parsing with AI..."):
            result = parse_resume(text)

        try:
            data = result if isinstance(result, dict) else json.loads(result)

            if "error" in data:
                st.error(data["error"])
                st.text(data.get("raw", ""))
            else:
                # Basic Info
                col1, col2, col3 = st.columns(3)
                col1.markdown(f'<div class="card"><b>👤 Name</b><br>{data.get("name","—")}</div>', unsafe_allow_html=True)
                col2.markdown(f'<div class="card"><b>📧 Email</b><br>{data.get("email","—")}</div>', unsafe_allow_html=True)
                col3.markdown(f'<div class="card"><b>📞 Phone</b><br>{data.get("phone","—")}</div>', unsafe_allow_html=True)

                # Skills
                st.markdown('<div class="section-heading">🛠 Skills</div>', unsafe_allow_html=True)
                skills = data.get("skills", [])
                if skills:
                    pills = "".join([f'<span class="pill">{s}</span>' for s in skills])
                    st.markdown(f'<div class="card">{pills}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="card">—</div>', unsafe_allow_html=True)

                # Education
                st.markdown('<div class="section-heading">🎓 Education</div>', unsafe_allow_html=True)
                for edu in data.get("education", []):
                    st.markdown(
                        f'<div class="card"><b>{edu.get("degree","—")}</b><br>'
                        f'{edu.get("institution","—")} · {edu.get("year","—")}</div>',
                        unsafe_allow_html=True
                    )

                # Experience
                st.markdown('<div class="section-heading">💼 Experience</div>', unsafe_allow_html=True)
                for exp in data.get("experience", []):
                    st.markdown(
                        f'<div class="card"><b>{exp.get("title","—")}</b> at {exp.get("company","—")}<br>'
                        f'⏱ {exp.get("duration","—")}</div>',
                        unsafe_allow_html=True
                    )

                # Projects
                st.markdown('<div class="section-heading">🚀 Projects</div>', unsafe_allow_html=True)
                projects = data.get("projects", [])
                if projects:
                    for proj in projects:
                        st.markdown(
                            f'<div class="card"><b>{proj.get("name","—")}</b><br>'
                            f'{proj.get("description","")}<br>'
                            f'🛠 {", ".join(proj.get("technologies", []))}</div>',
                            unsafe_allow_html=True
                        )
                else:
                    st.markdown('<div class="card">—</div>', unsafe_allow_html=True)

                # Certifications
                st.markdown('<div class="section-heading">📜 Certifications</div>', unsafe_allow_html=True)
                certs = data.get("certifications", [])
                if certs:
                    for cert in certs:
                        st.markdown(
                            f'<div class="card"><b>{cert.get("name","—")}</b><br>'
                            f'{cert.get("issuer","")} · {cert.get("year","")}</div>',
                            unsafe_allow_html=True
                        )
                else:
                    st.markdown('<div class="card">—</div>', unsafe_allow_html=True)

                # Summary
                st.markdown('<div class="section-heading">📝 Summary</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="card">{data.get("summary","—")}</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error: {e}")
            st.write(result)