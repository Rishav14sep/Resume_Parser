import fitz
import docx
import textract
import tempfile
import os
import json
import re
from dotenv import load_dotenv
from groq import Groq
 
load_dotenv(dotenv_path=".env")


 
def extract_text(file):
    file_type = file.name.split(".")[-1].lower()

    # -------- PDF --------
    if file_type == "pdf":
        document = fitz.open(stream=file.read(), filetype="pdf")
        text = ""
        for page in document:
            text += page.get_text()
        return text

    # -------- DOCX --------
    elif file_type == "docx":
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])

    # -------- DOC --------
    elif file_type == "doc":
        with tempfile.NamedTemporaryFile(delete=False, suffix=".doc") as tmp:
            tmp.write(file.read())
            tmp_path = tmp.name

        text = textract.process(tmp_path).decode("utf-8")
        os.remove(tmp_path)
        return text

    else:
        raise ValueError("Unsupported file format")


 
def parse_resume(text):

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY not found. Check your .env file.")

    client = Groq(api_key=api_key)

    text = text[:5000]

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
            "role": "user",
            "content": f"""
Extract structured data from this resume.

Return ONLY valid JSON. No explanation.

Schema:
{{
  "name": "",
  "email": "",
  "phone": "",
  "skills": [],
  "education": [{{"degree": "", "institution": "", "year": ""}}],
  "experience": [{{"title": "", "company": "", "duration": ""}}],
  "projects": [
    {{"name": "", "description": "", "technologies": []}}
  ],
  "certifications": [
    {{"name": "", "issuer": "", "year": ""}}
  ],
  "summary": ""
}}

Rules:
- Extract projects even if mentioned under experience or portfolio
- Extract certifications even if mentioned under achievements
- If section missing → return empty list
- Keep response strictly JSON

Resume Text:
{text}
"""
        }],
        max_tokens=1500
    )

    content = response.choices[0].message.content.strip()

    
    content = re.sub(r"^```(?:json)?", "", content)
    content = re.sub(r"```$", "", content).strip()

     
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass

        return {"error": "Invalid JSON", "raw": content}