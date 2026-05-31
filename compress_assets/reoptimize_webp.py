import base64
import re
import subprocess
import os
from PIL import Image
from io import BytesIO

def reoptimize_svg_webp(svg_path, output_path, quality=75):
    """
    بهینه‌سازی مجدد SVG که WebP دارد با کیفیت و فشرده‌سازی بهتر
    """
    with open(svg_path, 'r', encoding='utf-8') as f:
        svg_content = f.read()

    # پیدا کردن WebP موجود
    pattern = r'data:image/webp;base64,([A-Za-z0-9+/=]+)'
    match = re.search(pattern, svg_content)

    if not match:
        print(f"📁 {svg_path} - WebP پیدا نشد!")
        return False

    print(f"📁 {svg_path}")
    
    # decode کردن WebP موجود
    webp_base64 = match.group(1)
    webp_data = base64.b64decode(webp_base64)
    orig_size = len(webp_data) / 1024

    # ذخیره موقت
    with open('temp_webp.webp', 'wb') as f:
        f.write(webp_data)

    # فشرده‌سازی مجدد با تنظیمات بهتر
    subprocess.run([
        'ffmpeg', '-y', '-i', 'temp_webp.webp',
        '-quality', str(quality),
        '-compression_level', '6',
        '-preset', 'picture',  # بهترین preset برای عکس
        '-qmin', '0',
        '-qmax', str(quality + 10),
        'temp_optimized.webp'
    ], capture_output=True)

    # خواندن تصویر بهینه شده
    with open('temp_optimized.webp', 'rb') as f:
        new_webp_data = f.read()
    
    new_size = len(new_webp_data) / 1024
    
    # اگر حجم کمتر شد، استفاده کن
    if new_size < orig_size:
        new_base64 = base64.b64encode(new_webp_data).decode('utf-8')
        
        # جایگزینی در SVG
        new_svg = svg_content.replace(
            f'data:image/webp;base64,{webp_base64}',
            f'data:image/webp;base64,{new_base64}'
        )

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(new_svg)

        # پاکسازی
        os.remove('temp_webp.webp')
        os.remove('temp_optimized.webp')

        final_size = os.path.getsize(output_path) / 1024
        reduction = ((orig_size - new_size) / orig_size) * 100
        print(f"   {orig_size:.0f}KB → {final_size:.0f}KB ✅ (کاهش {reduction:.1f}%)")
        return True
    else:
        print(f"   {orig_size:.0f}KB - بهینه‌سازی بیشتر ممکن نیست ⚠️")
        os.remove('temp_webp.webp')
        os.remove('temp_optimized.webp')
        return False


# فایل‌های SVG با WebP
files = ['banner-mobile (2)_optimized.svg']

print("شروع بهینه‌سازی مجدد WebP...\n")
for f in files:
    output = f.replace('.svg', '_reoptimized.svg')
    reoptimize_svg_webp(f, output, quality=70)

print("\n✅ بهینه‌سازی مجدد تمام شد!")
عال