import base64
import re
import subprocess
import os


def optimize_svg_image(svg_path, output_path, quality=90):
    """
    بهینه‌سازی SVG با فشرده‌سازی تصویر embed شده
    """
    with open(svg_path, 'r', encoding='utf-8') as f:
        svg_content = f.read()

    # پیدا کردن تصویر base64 (PNG یا JPEG)
    pattern = r'data:image/(png|jpg|jpeg);base64,([A-Za-z0-9+/=]+)'
    match = re.search(pattern, svg_content)

    if match:
        print(f"📁 {svg_path}")
        
        img_format = match.group(1)  # png, jpg, or jpeg
        
        # decode کردن base64
        img_data = base64.b64decode(match.group(2))

        # ذخیره موقت
        temp_ext = 'png' if img_format == 'png' else 'jpg'
        temp_input = f'temp_img.{temp_ext}'
        with open(temp_input, 'wb') as f:
            f.write(img_data)

        orig_size = len(img_data) / 1024

        # فشرده‌سازی با WebP
        subprocess.run([
            'ffmpeg', '-y', '-i', temp_input,
            '-quality', str(quality),
            '-compression_level', '6',
            'temp_img.webp'
        ], capture_output=True)

        # خواندن تصویر فشرده
        with open('temp_img.webp', 'rb') as f:
            new_img_data = f.read()

        new_size = len(new_img_data) / 1024

        # تبدیل به base64
        new_base64 = base64.b64encode(new_img_data).decode('utf-8')

        # جایگزینی در SVG
        new_svg = svg_content.replace(
            f'data:image/{img_format};base64,{match.group(2)}',
            f'data:image/webp;base64,{new_base64}'
        )

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(new_svg)

        # پاکسازی
        os.remove(temp_input)
        os.remove('temp_img.webp')

        final_size = os.path.getsize(output_path) / 1024
        print(f"   {orig_size:.0f}KB → {final_size:.0f}KB ✅")
        return True
    else:
        print(f"📁 {svg_path} - تصویر base64 پیدا نشد!")
        return False


# بهینه‌سازی 3 فایل
files = [r'casual-life-3d-orange-planet-with-disk 1.svg' , 'Rectangle 59 (2).svg' ,'Rectangle 59 (5).svg' ,'Rectangle 59.svg']

print("شروع بهینه‌سازی...\n")
for f in files:
    output = f.replace('.svg', '_optimized.svg')
    optimize_svg_image(f, output, quality=90)

print("\n✅ همه فایل‌ها بهینه شدند!")
