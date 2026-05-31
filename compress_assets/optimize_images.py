import subprocess
import os

def optimize_image(image_path, output_path, quality=75):
    """
    بهینه‌سازی تصاویر JPG/PNG به WebP
    """
    if not os.path.exists(image_path):
        print(f"❌ {image_path} - فایل پیدا نشد!")
        return False
    
    orig_size = os.path.getsize(image_path) / 1024
    print(f"📁 {image_path} ({orig_size:.0f}KB)")
    
    # تبدیل به WebP
    subprocess.run([
        'ffmpeg', '-y', '-i', image_path,
        '-quality', str(quality),
        '-compression_level', '6',
        '-preset', 'picture',
        '-qmin', '0',
        '-qmax', str(quality + 10),
        output_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    if os.path.exists(output_path):
        new_size = os.path.getsize(output_path) / 1024
        reduction = ((orig_size - new_size) / orig_size) * 100
        print(f"   → {output_path} ({new_size:.0f}KB) ✅ کاهش {reduction:.1f}%\n")
        return True
    else:
        print(f"   ❌ خطا در تبدیل\n")
        return False


# فایل‌های تصویر
files = ['Last-Webinar-Story.jpg', 'Last-Webinar.jpg']

print("شروع بهینه‌سازی تصاویر...\n")
for f in files:
    # تبدیل به WebP
    output = f.replace('.jpg', '.webp').replace('.jpeg', '.webp').replace('.png', '.webp')
    optimize_image(f, output, quality=75)

print("✅ همه تصاویر بهینه شدند!")
