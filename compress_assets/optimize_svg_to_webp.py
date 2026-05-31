import base64
import os
import re
import subprocess


def convert_to_webp(input_img_path, output_webp_path, quality=90):
    """Convert image file to WebP with fallback."""
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                input_img_path,
                "-quality",
                str(quality),
                "-compression_level",
                "6",
                output_webp_path,
            ],
            capture_output=True,
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        try:
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-i",
                    input_img_path,
                    output_webp_path,
                ],
                capture_output=True,
                check=True,
            )
            return True
        except subprocess.CalledProcessError as error:
            print(f"Conversion failed for {input_img_path}: {error.stderr.decode(errors='ignore')}")
            return False


def optimize_svg_embedded_images(svg_path, output_path, quality=90):
    """Compress embedded base64 PNG/JPEG images in SVG and replace them with WebP."""
    try:
        with open(svg_path, "r", encoding="utf-8") as file:
            content = file.read()
    except UnicodeDecodeError:
        print(f"Invalid SVG text file: {svg_path}")
        return False

    pattern = r"data:image/(png|jpe?g);base64,([A-Za-z0-9+/=]+)"
    converted_count = [0]

    def replacer(match):
        image_format = match.group(1)
        image_bytes = base64.b64decode(match.group(2))
        temp_input = f"temp_in_{os.getpid()}_{converted_count[0]}.{image_format}"
        temp_output = f"temp_out_{os.getpid()}_{converted_count[0]}.webp"

        with open(temp_input, "wb") as file:
            file.write(image_bytes)

        try:
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-i",
                    temp_input,
                    "-quality",
                    str(quality),
                    "-compression_level",
                    "6",
                    temp_output,
                ],
                capture_output=True,
                check=True,
            )
            with open(temp_output, "rb") as file:
                webp_bytes = file.read()
            webp_b64 = base64.b64encode(webp_bytes).decode("utf-8")
            converted_count[0] += 1
            replacement = f"data:image/webp;base64,{webp_b64}"
        except Exception:
            replacement = match.group(0)
        finally:
            if os.path.exists(temp_input):
                os.remove(temp_input)
            if os.path.exists(temp_output):
                os.remove(temp_output)

        return replacement

    updated_content = re.sub(pattern, replacer, content)
    if converted_count[0] > 0:
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(updated_content)
        return True
    return False


def process_file(input_path, output_webp_path, quality=90):
    """Process SVG/PNG/JPG/JPEG input and produce optimized output."""
    if not os.path.exists(input_path):
        print(f"File does not exist: {input_path}")
        return False

    extension = os.path.splitext(input_path)[1].lower()
    if extension == ".svg":
        output_svg_path = input_path.replace(".svg", "_optimized.svg")
        if optimize_svg_embedded_images(input_path, output_svg_path, quality):
            print(f"Optimized SVG saved: {output_svg_path}")
            return True
        print(f"No embedded raster image found in SVG: {input_path}")
        return True

    if convert_to_webp(input_path, output_webp_path, quality):
        print(f"Converted to WebP: {output_webp_path}")
        return True
    return False


if __name__ == "__main__":
    files = [
        "add-asset-banner.svg",
        "auth-login-hero.svg",
        "earth (2).svg",
        "final_logo.svg",
        "no-scenario.svg",
        "optimize-banner.svg",
        "story-placeholder.jpg",
    ]
    quality = 90

    print("Starting SVG/image optimization...")
    for file_name in files:
        output_file = os.path.splitext(file_name)[0] + ".webp"
        process_file(file_name, output_file, quality)
    print("Done.")
