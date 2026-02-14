import fitz

def create_sample():
    doc = fitz.open()
    page = doc.new_page()
    
    page.insert_text((100, 150), "Hidden Message", fontsize=40, color=(1, 0, 0))
    
    rect = fitz.Rect(100, 100, 500, 200) 
    page.insert_image(rect, filename="sample/mask.png")
    
    doc.save("sample/target.pdf")


create_sample()