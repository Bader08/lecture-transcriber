import streamlit as st
import google.generativeai as genai
import os
from fpdf import FPDF

# إعداد الصفحة لتكون مريحة وواسعة لملفات الـ Plant Design
st.set_page_config(page_title="Plant Design Transcription Engine", layout="wide")

st.title("🔬 PLANT DESIGN | STREAMLIT TRANSCRIPTION ENGINE")
st.caption("Automated Academic System for Chemical Engineering & Unit Operations")
st.markdown("---")

# تقسيم الشاشة بشكل مريح
col_input, col_output = st.columns([1, 2])

with col_input:
    st.subheader("📁 1. Source Audio File")
    uploaded_file = st.file_uploader("Upload Lecture Audio (M4A / MP3 / WAV / OGG / AAC)", type=["m4a", "mp3", "wav", "ogg", "aac"])
    
    st.markdown("---")
    st.subheader("⚙️ 2. Execution Center")
    api_key = st.text_input("Enter Google API Key:", type="password", help="ضع مفتاح الـ API الخاص بك هنا لتفعيل الاتصال الحقيقي بسيرفرات جوجل وتفريغ المحاضرة كاملة")

if api_key and uploaded_file is not None:
    genai.configure(api_key=api_key)
    audio_file_name = uploaded_file.name
    
    if col_input.button("🚀 Start Full Processing", use_container_width=True):
        with st.spinner("Analyzing full audio with Plant Design context... Please wait. This may take 1-3 minutes for long lectures."):
            try:
                # حفظ الملف مؤقتاً لرفعه
                with open("temp_audio.mp3", "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # رفع الملف السحابي لضمان معالجة المحاضرة كاملة دون انقطاع
                audio_file = genai.upload_file(path="temp_audio.mp3")
                
                # تم التعديل إلى gemini-1.5-flash لتجاوز خطأ الحصة اليومية (Quota) وضمان تفريغ المحاضرة كاملة مجاناً
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction=(
                        "You are an elite academic engine specialized in Chemical Engineering and Plant Design. "
                        "Process the entire audio file completely from start to finish without missing or cutting any section. "
                        "Strictly write all engineering formulas, variables, and notations in plain clear text or bold formatting (e.g., write 'alpha', 'q-value', 'Reflux Ratio R_D', 'PFR Kinetics') and NEVER use LaTeX or dollar signs ($) to prevent formatting errors. "
                        "The engine must automatically understand and master all terms related to: Distillation columns & reflux control, Reactor Design (Batch, PFR, CSTR, kinetics), Heat Exchangers, Piping systems, and Plant Safety (Rupture disks, corrosion, SACP/ICCP cathodic protection). "
                        "Structure the output with exact timestamps: '[00:01:15] Speaker 1 (Professor): ...'. "
                        "At the very end, you must generate a separate, comprehensive academic section titled 'EXAM PREP & STUDY TARGETS SUMMARY' showcasing exam-expected questions and core takeaways linked to their timestamps."
                    )
                )
                
                # إطلاق عملية المعالجة الحقيقية
                response = model.generate_content([audio_file, f"Strictly transcribe the entire audio file named '{audio_file_name}' word-for-word with speakers and timestamps, and provide the detailed exam-focused summary at the end."])
                full_text = response.text
                os.remove("temp_audio.mp3")
                
                # فصل السكريبت عن الملخص برمجياً لإتاحة تحميل كل جزئية لوحدها
                if "EXAM PREP" in full_text:
                    parts = full_text.split("EXAM PREP")
                    transcript_part = parts[0]
                    summary_part = "EXAM PREP" + parts[1]
                else:
                    transcript_part = full_text
                    summary_part = "Summary section could not be parsed automatically, please check the main transcript tab."

                with col_output:
                    st.success(f"✨ Successfully Processed Full Lecture: {audio_file_name}")
                    
                    tab1, tab2 = st.tabs([f"📝 Transcript for: {audio_file_name}", "🎯 Exam Study Targets & Summary"])
                    
                    with tab1:
                        st.text_area("Transcript Content", value=transcript_part, height=450)
                        
                        st.markdown("### 📥 Download Transcript As:")
                        c1, c2, c3 = st.columns(3)
                        c1.download_button("Plain Text (.txt)", data=transcript_part, file_name=f"Transcript_{audio_file_name}.txt", mime="text/plain", use_container_width=True)
                        
                        pdf1 = FPDF()
                        pdf1.add_page()
                        pdf1.set_font("Arial", size=12)
                        clean_text1 = transcript_part.encode('latin-1', 'ignore').decode('latin-1')
                        pdf1.multi_cell(0, 10, txt=clean_text1)
                        pdf1_bytes = pdf1.output(dest='S').encode('latin-1')
                        c2.download_button("PDF Document (.pdf)", data=pdf1_bytes, file_name=f"Transcript_{audio_file_name}.pdf", mime="application/pdf", use_container_width=True)
                        
                        c3.download_button("Subtitle File (.srt)", data=transcript_part, file_name=f"Transcript_{audio_file_name}.srt", mime="text/srt", use_container_width=True)

                    with tab2:
                        st.text_area("Summary Content", value=summary_part, height=450)
                        
                        st.markdown("### 📥 Download Study Summary As:")
                        cc1, cc2 = st.columns(2)
                        cc1.download_button("Plain Text (.txt)", data=summary_part, file_name=f"Study_Targets_{audio_file_name}.txt", mime="text/plain", use_container_width=True)
                        
                        pdf2 = FPDF()
                        pdf2.add_page()
                        pdf2.set_font("Arial", size=12)
                        clean_text2 = summary_part.encode('latin-1', 'ignore').decode('latin-1')
                        pdf2.multi_cell(0, 10, txt=clean_text2)
                        pdf2_bytes = pdf2.output(dest='S').encode('latin-1')
                        cc2.download_button("PDF Document (.pdf)", data=pdf2_bytes, file_name=f"Study_Targets_{audio_file_name}.pdf", mime="application/pdf", use_container_width=True)

            except Exception as e:
                st.error(f"Error processing audio file: {e}")
else:
    with col_output:
        st.info("ℹ️ Awaiting Audio Upload and Google API Key Setup to activate the transcription pipeline.")
