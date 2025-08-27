import pdfplumber
import pandas as pd
import os

def extract_tables_with_keyword(pdf_path, keyword):
    """
    ดึงข้อมูลตารางจากไฟล์ PDF เฉพาะตารางที่มีคำที่กำหนด และบันทึกเป็นไฟล์ CSV แยกกัน
    
    Args:
        pdf_path (str): Path ของไฟล์ PDF
        keyword (str): คำที่ต้องการค้นหาในตาราง
    """
    output_dir = "output_tables"
    
    # ตรวจสอบและสร้างโฟลเดอร์สำหรับผลลัพธ์
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"สร้างโฟลเดอร์ '{output_dir}' เรียบร้อยแล้ว")
    
    found_tables_count = 0
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"กำลังค้นหาตารางที่มีคำว่า '{keyword}' ในไฟล์...")
            for page_num, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                if not tables:
                    continue  # ข้ามถ้าไม่พบตารางในหน้านั้น
                    
                for table_num, table in enumerate(tables):
                    # แปลงข้อมูลตารางเป็นข้อความเพื่อค้นหาคำ
                    table_text = " ".join(item for sublist in table for item in sublist if item is not None)
                    
                    # ตรวจสอบว่ามีคำที่ต้องการหรือไม่ (ไม่สนใจตัวพิมพ์เล็ก-ใหญ่)
                    if keyword.lower() in table_text.lower():
                        if table and table[0]:
                            try:
                                header = table[0]
                                data = table[1:]
                                df = pd.DataFrame(data, columns=header)
                                
                                # สร้างชื่อไฟล์
                                base_name = os.path.splitext(os.path.basename(pdf_path))[0]
                                csv_filename = os.path.join(output_dir, f"{base_name}_page_{page_num+1}_table_{table_num+1}.csv")
                                
                                # บันทึกเป็นไฟล์ CSV
                                df.to_csv(csv_filename, index=False, encoding='utf-8')
                                print(f"✅ พบและบันทึกตารางที่ {table_num+1} จากหน้า {page_num+1} ที่มีคำว่า '{keyword}' -> {csv_filename}")
                                found_tables_count += 1
                                
                            except Exception as e:
                                print(f"❌ เกิดข้อผิดพลาดในการบันทึกตารางที่ {table_num+1} จากหน้า {page_num+1}: {e}")

    except FileNotFoundError:
        print(f"❌ ไม่พบไฟล์ PDF: {pdf_path}")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดทั่วไป: {e}")
        
    if found_tables_count == 0:
        print(f"\n⚠️ ไม่พบตารางที่มีคำว่า '{keyword}' ในไฟล์นี้")
    else:
        print(f"\n🎉 บันทึกตารางทั้งหมด {found_tables_count} ตารางที่มีคำว่า '{keyword}' เรียบร้อยแล้ว")

# --- ตัวอย่างการใช้งาน ---
pdf_file = "GP26073 Constant Comfort Microfiber Modern Brief (WMI38,43T).pdf" 
search_keyword = "Sewing Operation" # เปลี่ยนเป็นคำที่คุณต้องการค้นหา

extract_tables_with_keyword(pdf_file, search_keyword)
