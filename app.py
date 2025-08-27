import streamlit as st
import pdfplumber
import pandas as pd
import os
import zipfile
from io import BytesIO

def extract_tables_with_keyword(pdf_file, keyword):
    """
    ดึงข้อมูลตารางจากไฟล์ PDF เฉพาะตารางที่มีคำที่กำหนด และบันทึกเป็นไฟล์ CSV แยกกัน
    
    Args:
        pdf_file: ไฟล์ PDF ที่อัปโหลดโดยผู้ใช้
        keyword (str): คำที่ต้องการค้นหาในตาราง
    """
    output_dir = "output_tables"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    found_tables_count = 0
    file_list = []
    
    try:
        with pdfplumber.open(pdf_file) as pdf:
            st.info(f"กำลังค้นหาตารางที่มีคำว่า '{keyword}' ในไฟล์...")
            for page_num, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                if not tables:
                    continue  
                    
                for table_num, table in enumerate(tables):
                    table_text = " ".join(item for sublist in table for item in sublist if item is not None)
                    
                    if keyword.lower() in table_text.lower():
                        if table and table[0]:
                            try:
                                header = table[0]
                                data = table[1:]
                                df = pd.DataFrame(data, columns=header)
                                
                                base_name = os.path.splitext(os.path.basename(pdf_file.name))[0]
                                csv_filename = f"{base_name}_page_{page_num+1}_table_{table_num+1}.csv"
                                file_path = os.path.join(output_dir, csv_filename)
                                
                                df.to_csv(file_path, index=False, encoding='utf-8')
                                st.success(f"✅ พบและบันทึกตารางที่ {table_num+1} จากหน้า {page_num+1} ที่มีคำว่า '{keyword}'")
                                found_tables_count += 1
                                file_list.append(file_path)
                                
                            except Exception as e:
                                st.error(f"❌ เกิดข้อผิดพลาดในการบันทึกตารางที่ {table_num+1} จากหน้า {page_num+1}: {e}")

    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาดทั่วไป: {e}")
        
    return file_list

def create_zip_archive(files):
    """
    สร้างไฟล์ ZIP จากรายการไฟล์ CSV
    """
    if not files:
        return None
        
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file in files:
            zip_file.write(file, os.path.basename(file))
            
    return zip_buffer.getvalue()

def main():
    st.title("เครื่องมือดึงข้อมูลตารางจาก PDF")
    st.markdown("โปรดอัปโหลดไฟล์ PDF ของคุณและใส่คำที่ต้องการค้นหาในตาราง")
    
    # ส่วนอัปโหลดไฟล์ที่รองรับหลายไฟล์
    uploaded_files = st.file_uploader("อัปโหลดไฟล์ PDF", type="pdf", accept_multiple_files=True)
    
    # ส่วนกรอกคำค้นหา
    search_keyword = st.text_input("ป้อนคำที่ต้องการค้นหาในตาราง", "Summary")

    if uploaded_files and search_keyword:
        if st.button("เริ่มประมวลผล"):
            st.spinner("กำลังประมวลผล...")
            
            all_extracted_files = []
            
            for file in uploaded_files:
                st.info(f"--- กำลังประมวลผลไฟล์: {file.name} ---")
                extracted_files = extract_tables_with_keyword(file, search_keyword)
                all_extracted_files.extend(extracted_files)
                
            if all_extracted_files:
                st.subheader("ผลลัพธ์")
                st.success(f"🎉 ประมวลผลเสร็จสิ้น! พบตารางทั้งหมด {len(all_extracted_files)} ตาราง")
                
                # สร้างและแสดงปุ่มดาวน์โหลดไฟล์ ZIP
                zip_data = create_zip_archive(all_extracted_files)
                st.download_button(
                    label="ดาวน์โหลดตารางทั้งหมด (ไฟล์ ZIP)",
                    data=zip_data,
                    file_name="extracted_tables.zip",
                    mime="application/zip"
                )
                
                # ลบไฟล์ชั่วคราวหลังจากสร้าง ZIP แล้ว
                for file_path in all_extracted_files:
                    os.remove(file_path)
                
            else:
                st.warning(f"⚠️ ไม่พบตารางที่มีคำว่า '{search_keyword}' ในไฟล์ที่อัปโหลดทั้งหมด")

if __name__ == "__main__":
    main()
