from PIL import Image

src_path = r"C:\Users\MSi\.gemini\antigravity\brain\d617e4a4-ecbe-447b-bb80-886f9dfacef4\.user_uploaded\media_1791380077693.png"
dst_path = "images/card_back.jpg"

img = Image.open(src_path)
img = img.resize((859, 1200), Image.Resampling.LANCZOS)
if img.mode != 'RGB':
    img = img.convert('RGB')
img.save(dst_path, "JPEG", quality=95)
print(f"Updated {dst_path} to 859x1200.")
