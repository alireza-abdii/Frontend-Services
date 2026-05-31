import base64
import re
import subprocess
import os

def optimize_svg_image(svg_path, output_path, quality=90):
    """
    بهینه‌سازی SVG با پشتیبانی از href، xlink:href و Base64
    """
    with open(svg_path, 'r', encoding='utf-8') as f:
        svg_content = f.read()

    img_filename = None
    is_base64 = False
    match_obj = None

    # ۱. بررسی وجود Base64 مستقیم (حالت قبلی)
    base64_pattern = r'data:image/(png|jpg|jpeg);base64,([A-Za-z0-9+/=]+)'
    match = re.search(base64_pattern, svg_content)
    if match:
        print(f"📁 {svg_path} (حالت Base64 مستقیم)")
        is_base64 = True
        match_obj = match
    else:
        # ۲. بررسی لینک معمولی href="..."
        href_pattern = r'href=["\']([^"\']+?\.(png|jpg|jpeg))["\']'
        match = re.search(href_pattern, svg_content, re.IGNORECASE)
        if match:
            img_filename = match.group(1)
            print(f"📁 {svg_path} (حالت لینک href)")
        else:
            # ۳. بررسی لینک xlink:href="..." (بسیار رایج در SVGها)
            xlink_pattern = r'xlink:href=["\']([^"\']+?\.(png|jpg|jpeg))["\']'
            match = re.search(xlink_pattern, svg_content, re.IGNORECASE)
            if match:
                img_filename = match.group(1)
                print(f"📁 {svg_path} (حالت لینک xlink:href)")

    # اگر هیچ کدام پیدا نشد
    if not match and not img_filename:
        print(f"📁 {svg_path} - هیچ تصویری پیدا نشد!")
        # برای دیباگ: محتویات فایل را چاپ کن تا ببینیم ساختارش چطور است
        # print(svg_content[:500]) 
        return False

    # --- پردازش تصویر ---
    
    # مسیر فایل تصویر ورودی برای ffmpeg
    input_img_path = ''
    
    if is_base64:
        # دیکد کردن Base64 و ذخیره موقت
        img_data = base64.b64decode(match_obj.group(2))
        input_img_path = 'temp_input.png'
        with open(input_img_path, 'wb') as f:
            f.write(img_data)
        orig_size = len(img_data) / 1024
    else:
        # خواندن از فایل
        svg_dir = os.path.dirname(svg_path)
        # اگر مسیر خالی بود، یعنی فایل در همان پوشه جاری است
        if not svg_dir:
            svg_dir = '.'
            
        input_img_path = os.path.join(svg_dir, img_filename)
        
        if not os.path.exists(input_img_path):
            print(f"   ❌ فایل تصویر یافت نشد: {input_img_path}")
            return False
            
        orig_size = os.path.getsize(input_img_path) / 1024

    # فشرده‌سازی با WebP
    subprocess.run([
        'ffmpeg', '-y', '-i', input_img_path,
        '-quality', str(quality),
        '-compression_level', '6',
        'temp_img.webp'
    ], capture_output=True)

    # خواندن تصویر فشرده
    with open('temp_img.webp', 'rb') as f:
        new_img_data = f.read()
    
    new_size = len(new_img_data) / 1024
    new_base64 = base64.b64encode(new_img_data).decode('utf-8')

    # جایگزینی در SVG
    if is_base64:
        # جایگزینی رشته کامل Base64 قبلی
        old_str = match_obj.group(0)
        new_str = f'data:image/webp;base64,{new_base64}'
        new_svg = svg_content.replace(old_str, new_str)
    else:
        # جایگزینی href یا xlink:href با داده Base64 جدید
        # ما کل تگ image را پیدا می‌کنیم و ویژگی href را تغییر می‌دهیم
        # روش ساده‌تر: استفاده از replace برای لینک پیدا شده
        
        # نکته: اگر xlink:href بود، آن را به href ساده تبدیل می‌کنیم تا استاندارد باشد
        if 'xlink:href' in svg_content:
            # جایگزینی xlink:href="file.png" با href="data:..."
            # این روش کمی پیچیده است، ساده‌ترین راه این است که کل خاصیت را جایگزین کنیم
            # اما برای اطمینان، ما فقط مقدار را در همان ساختار جایگزین می‌کنیم
            
            # پیدا کردن کل عبارت xlink:href="..."
            full_match = re.search(r'xlink:href=["\'][^"\']+["\']', svg_content)
            if full_match:
                new_svg = svg_content.replace(full_match.group(0), f'href="data:image/webp;base64,{new_base64}"')
            else:
                new_svg = svg_content # فال‌بک
        else:
            # حالت معمولی href
            full_match = re.search(r'href=["\'][^"\']+["\']', svg_content)
            if full_match:
                new_svg = svg_content.replace(full_match.group(0), f'href="data:image/webp;base64,{new_base64}"')
            else:
                new_svg = svg_content

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(new_svg)

    # پاکسازی
    if is_base64 and os.path.exists('temp_input.png'):
        os.remove('temp_input.png')
    if os.path.exists('temp_img.webp'):
        os.remove('temp_img.webp')

    final_size = os.path.getsize(output_path) / 1024
    print(f"   {orig_size:.0f}KB → {final_size:.0f}KB ✅")
    return True

# بهینه‌سازی فایل
files = [r'casual-life-3d-orange-planet-with-disk 1.svg' , 'Rectangle 59 (2).svg' ,'Rectangle 59 (5).svg' ,'Rectangle 59.svg']
print("شروع بهینه‌سازی...\n")
for f in files:
    output = f.replace('.svg', '_optimized.svg')
    optimize_svg_image(f, output, quality=90)
print("\n✅ همه فایل‌ها بهینه شدند!")