import streamlit as st
import google.generativeai as genai
import os
from fpdf import FPDF
import io

# إعداد الصفحة لتكون مريحة، واسعة، وغير محشورة وتناسب ملفات الـ Plant Design
st.set_page_config(page_title="Plant Design Transcription Engine", layout="wide")

# تخصيص واجهة مريحة وموزعة بشكل ممتاز بدون مربعات جانية معقدة
st.title("🔬 PLANT DESIGN | LECTURE TRANSCRIPTION ENGINE")
st.caption("Automated Academic System for Chemical Engineering & Unit Operations")
st.markdown("---")

# تقسيم الشاشة إلى مساحات واسعة ومريحة للعين (رفع الملف على اليسار والمخرجات على اليمين)
col_input, col_output = st.columns([1, 2])

with col_input:
    st.subheader("📁 1. Source Audio File")
    uploaded_file = st.file_uploader("Upload Lecture Audio (MP3 / WAV)", type=["mp3", "wav"])
    
    st.markdown("---")
    st.subheader("⚙️ 2. Execution Center")
    api_key = st.text_input("Enter Google API Key:", type="password", help="ضع مفتاح الـ API الخاص بك هنا لتفعيل الاتصال بسيرفرات جوجل")

if api_key and uploaded_file is not None:
    genai.configure(api_key=api_key)
    
    # الحصول على اسم ملف الأوديو الحقيقي لاستخدامه في العناوين تلقائياً
    audio_file_name = uploaded_file.name
    
    if col_input.button("🚀 Start Full Processing", use_container_width=True):
        with st.spinner("Analyzing full audio with Plant Design context... Please wait."):
            try:
                # حفظ الملف مؤقتاً لرفعه
                with open("temp_audio.mp3", "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # رفع الملف السحابي لضمان معالجة الملفات الطويلة جداً (ساعتين وأكثر) دون انقطاع
                audio_file = genai.upload_file(path="temp_audio.mp3")
                
                # تخزين سياق الهندسة الكيميائية بالكامل في الخلفية (مخ النظام) لكي يفهم كل شيء تلقائياً
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-pro",
                    system_instruction=(
                        "You are an elite academic engine specialized in Chemical Engineering and Plant Design. "
                        "Process the entire audio file completely without missing or cutting any section. "
                        "Strictly write all engineering formulas, variables, and notations in plain clear text or bold formatting (e.g., write 'alpha', 'q-value', 'Reflux Ratio R_D', 'PFR Kinetics') and NEVER use LaTeX or dollar signs ($) to prevent formatting errors. "
                        "The engine must automatically understand and master all terms related to: Distillation columns & reflux control, Reactor Design (Batch, PFR, CSTR, kinetics), Heat Exchangers, Piping systems, and Plant Safety (Rupture disks, corrosion, SACP/ICCP cathodic protection). "
                        "Structure the output with exact timestamps: '[00:01:15] Speaker 1 (Professor): ...'. "
                        "At the very end, you must generate a separate, comprehensive academic section titled 'EXAM PREP & STUDY TARGETS SUMMARY' showcasing exam-expected questions and core takeaways linked to their timestamps."
                    )
                )
                
                # إطلاق عملية المعالجة
                response = model.generate_content([audio_file, f"Strictly transcribe the audio file named '{audio_file_name}' with speakers and timestamps, and provide the detailed exam-focused summary at the end."])
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

                # عرض النتائج في العمود المخصص الواسع بشكل منسق وجذاب وباسم الملف الحقيقي
                with col_output:
                    st.success(f"✨ Successfully Processed: {audio_file_name}")
                    
                    # إنشاء التبويبات المنفصلة والواسعة
                    tab1, tab2 = st.tabs([f"📝 Transcript for: {audio_file_name}", "🎯 Exam Study Targets & Summary"])
                    
                    with tab1:
                        st.text_area("Transcript Content", value=transcript_part, height=450)
                        
                        # أزرار تحميل منفصلة للتفريغ فقط وبصيغ متعددة
                        st.markdown("### 📥 Download Transcript As:")
                        c1, c2, c3 = st.columns(3)
                        c1.download_button("Plain Text (.txt)", data=transcript_part, file_name=f"Transcript_{audio_file_name}.txt", mime="text/plain", use_container_width=True)
                        
                        # توليد PDF للسكريبت
                        pdf1 = FPDF()
                        pdf1.add_page()
                        pdf1.set_font("Arial", size=12)
                        pdf1.multi_cell(0, 10, txt=transcript_part.encode('latin-1', 'ignore').decode('latin-1'))
                        buf1 = io.BytesIO()
                        pdf1.output(buf1, 'F')
                        c2.download_button("PDF Document (.pdf)", data=buf1.getvalue(), file_name=f"Transcript_{audio_file_name}.pdf", mime="application/pdf", use_container_width=True)
                        
                        c3.download_button("Subtitle File (.srt)", data=transcript_part, file_name=f"Transcript_{audio_file_name}.srt", mime="text/srt", use_container_width=True)

                    with tab2:
                        st.text_area("Summary Content", value=summary_part, height=450)
                        
                        # أزرار تحميل منفصلة للملخص فقط
                        st.markdown("### 📥 Download Study Summary As:")
                        cc1, cc2 = st.columns(2)
                        cc1.download_button("Plain Text (.txt)", data=summary_part, file_name=f"Study_Targets_{audio_file_name}.txt", mime="text/plain", use_container_width=True)
                        
                        # توليد PDF للملخص
                        pdf2 = FPDF()
                        pdf2.add_page()
                        pdf2.set_font("Arial", size=12)
                        pdf2.multi_cell(0, 10, txt=summary_part.encode('latin-1', 'ignore').decode('latin-1'))
                        buf2 = io.BytesIO()
                        pdf2.output(buf2, 'F')
                        cc2.download_button("PDF Document (.pdf)", data=buf2.getvalue(), file_name=f"Study_Targets_{audio_file_name}.pdf", mime="application/pdf", use_container_width=True)

            except Exception as e:
                st.error(f"Error processing audio file: {e}")
else:
    with col_output:
        st.info("ℹ️ Awaiting Audio Upload and Google API Key Setup to activate the pipeline.")
