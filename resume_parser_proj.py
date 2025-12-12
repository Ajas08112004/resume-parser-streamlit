import streamlit as st
import pdfplumber
import docx
import pandas as pd
import io

# Extract text from PDF
def extract_text_from_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

# Extract text from DOCX
def extract_text_from_docx(uploaded_file):
    doc = docx.Document(uploaded_file)
    return "\n".join([para.text for para in doc.paragraphs])

# Extract basic data from resume text
def extract_resume_data(text):
    text_lower = text.lower()
    data = {}
    data["Name"] = text.split('\n')[0] if text else ""
    data["Email"] = next((word for word in text.split() if "@" in word), "")
    data["Phone"] = next((word for word in text.split() if word.replace("+", "").replace("-", "").isdigit() and len(word) >= 10), "")
    data["Skills"] = ", ".join([skill for skill in ["python", "java", "machine learning", "html", "css", "sql"]
                                 if skill in text_lower])
    return data

# Streamlit App
def main():
    st.set_page_config(page_title="Resume Parser", layout="centered")
    st.title("📄 AJAS RESUME PARSER WEBPAGE")

    uploaded_files = st.file_uploader("Upload one or more resumes (.pdf or .docx):", type=["pdf", "docx"], accept_multiple_files=True)

    if uploaded_files:
        parsed_results = []

        for uploaded_file in uploaded_files:
            st.write(f"🔍 Processing: {uploaded_file.name}")
            try:
                if uploaded_file.name.endswith(".pdf"):
                    text = extract_text_from_pdf(uploaded_file)
                else:
                    text = extract_text_from_docx(uploaded_file)

                data = extract_resume_data(text)
                data["Filename"] = uploaded_file.name
                parsed_results.append(data)
            except Exception as e:
                st.error(f"❌ Failed to parse {uploaded_file.name}: {e}")

        if parsed_results:
            df = pd.DataFrame(parsed_results)
            st.success("✅ Resume data extracted successfully.")
            st.dataframe(df)

            # Create Excel for download
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Parsed Resumes')
            st.download_button("⬇ Download as Excel", data=output.getvalue(), file_name="resume_output.xlsx")

if __name__ == "__main__":
    main()