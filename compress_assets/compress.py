import subprocess
import os

def compress_best_quality(input_path, output_path, target_size_kb=500):
    """
    بالاترین کیفیت ممکن - بدون محدودیت زمانی
    """
    if os.path.exists(output_path):
        os.remove(output_path)
    
    result = subprocess.run([
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1', input_path
    ], capture_output=True, text=True)
    duration = float(result.stdout.strip())
    
    target_bitrate = int((target_size_kb * 8) / duration * 0.90)
    
    print(f"🎬 مدت ویدیو: {duration:.1f} ثانیه")
    print(f"🎯 Bitrate هدف: {target_bitrate} kbps")
    print(f"⏳ این پروسه ممکنه خیلی طول بکشه...")
    print("\n" + "="*50)
    print("پاس اول - آنالیز ویدیو...")
    print("="*50)
    
    # VP9 با بهترین تنظیمات ممکن
    subprocess.run([
        'ffmpeg', '-y', '-i', input_path,
        '-c:v', 'libvpx-vp9',
        '-b:v', f'{target_bitrate}k',
        '-quality', 'best',      # بهترین کیفیت
        '-speed', '0',           # کندترین = بهترین
        '-tile-columns', '0',    # بدون tile برای کیفیت بهتر
        '-frame-parallel', '0',  # بدون parallel برای کیفیت بهتر
        '-auto-alt-ref', '6',    # بیشترین alt ref frames
        '-arnr-maxframes', '15', # بیشترین فریم برای noise reduction
        '-arnr-strength', '6',   # قوی‌ترین noise reduction
        '-lag-in-frames', '25',  # بیشترین lookahead
        '-enable-tpl', '1',      # temporal layer optimization
        '-row-mt', '1',
        '-threads', '8',
        '-pass', '1',
        '-an',
        '-f', 'null', 'NUL'
    ])
    
    print("\n" + "="*50)
    print("پاس دوم - Encode نهایی...")
    print("="*50)
    
    subprocess.run([
        'ffmpeg', '-y', '-i', input_path,
        '-c:v', 'libvpx-vp9',
        '-b:v', f'{target_bitrate}k',
        '-quality', 'best',
        '-speed', '0',
        '-tile-columns', '0',
        '-frame-parallel', '0',
        '-auto-alt-ref', '6',
        '-arnr-maxframes', '15',
        '-arnr-strength', '6',
        '-lag-in-frames', '25',
        '-enable-tpl', '1',
        '-row-mt', '1',
        '-threads', '8',
        '-pass', '2',
        '-an',
        '-map_metadata', '-1',
        output_path
    ])
    
    for f in ['ffmpeg2pass-0.log']:
        if os.path.exists(f):
            os.remove(f)
    
    orig_size = os.path.getsize(input_path) / 1024
    new_size = os.path.getsize(output_path) / 1024
    
    print("\n" + "="*50)
    print("✅ تموم شد!")
    print("="*50)
    print(f"📁 حجم اصلی: {orig_size:.0f} KB")
    print(f"📁 حجم جدید: {new_size:.0f} KB")
    print(f"📉 کاهش: {(1-new_size/orig_size)*100:.1f}%")

compress_best_quality('zDkEup7O62q0z8HmStbH.mp4', 'output_best.webm', 500)
