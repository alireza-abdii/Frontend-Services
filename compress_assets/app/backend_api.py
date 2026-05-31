import re
import shutil
import subprocess
import tempfile
from base64 import b64decode, b64encode
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".svg"}
BASE_DIR = Path(__file__).resolve().parent
DIST_DIR = BASE_DIR / "dist"

app = FastAPI(title="Compress Assets API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)


def _compress_to_webp(input_file: Path, output_file: Path, quality: int = 75) -> None:
    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_file),
        "-quality",
        str(quality),
        "-compression_level",
        "6",
        "-preset",
        "picture",
        "-qmin",
        "0",
        "-qmax",
        str(min(100, quality + 10)),
        "-an",
        str(output_file),
    ]
    subprocess.run(command, check=True, capture_output=True)


def _optimize_svg(input_file: Path, output_file: Path, temp_dir: Path, quality: int = 80) -> None:
    svg_content = input_file.read_text(encoding="utf-8", errors="ignore")
    converted_count = 0
    temp_index = 0

    # Optimize all embedded base64 PNG/JPEG images in SVG by converting to WebP.
    pattern = r"data:image/(png|jpg|jpeg);base64,([A-Za-z0-9+/=]+)"

    def replacer(match: re.Match[str]) -> str:
        nonlocal converted_count, temp_index
        image_format = match.group(1).lower()
        raw_data = b64decode(match.group(2))
        temp_input = temp_dir / f"svg_embedded_input_{temp_index}.{image_format}"
        temp_webp = temp_dir / f"svg_embedded_optimized_{temp_index}.webp"
        temp_index += 1
        temp_input.write_bytes(raw_data)
        try:
            _compress_to_webp(temp_input, temp_webp, quality=quality)
            optimized_data = temp_webp.read_bytes()
            optimized_b64 = b64encode(optimized_data).decode("utf-8")
            converted_count += 1
            return f"data:image/webp;base64,{optimized_b64}"
        except Exception:
            return match.group(0)
        finally:
            if temp_input.exists():
                temp_input.unlink(missing_ok=True)
            if temp_webp.exists():
                temp_webp.unlink(missing_ok=True)

    optimized_svg = re.sub(pattern, replacer, svg_content, flags=re.IGNORECASE)

    no_comments = re.sub(r"<!--.*?-->", "", optimized_svg, flags=re.DOTALL)
    no_tag_whitespace = re.sub(r">\s+<", "><", no_comments)
    trimmed_line_spaces = re.sub(r"\n\s+", "\n", no_tag_whitespace)
    output_file.write_text(trimmed_line_spaces.strip(), encoding="utf-8")


@app.post("/api/compress")
async def compress_asset(file: UploadFile = File(...)):
    extension = Path(file.filename or "").suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PNG, JPG, JPEG, WEBP, and SVG files are supported.")

    temp_dir = Path(tempfile.mkdtemp(prefix="compress-assets-"))
    input_path = temp_dir / f"input{extension}"
    output_path = temp_dir / ("optimized.svg" if extension == ".svg" else "optimized.webp")

    try:
        with input_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        if extension == ".svg":
            _optimize_svg(input_path, output_path, temp_dir=temp_dir, quality=80)
        else:
            _compress_to_webp(input_path, output_path, quality=75)

        if not output_path.exists():
            raise HTTPException(status_code=500, detail="Compression output not generated.")

        optimized_bytes = output_path.read_bytes()
        output_name = Path(file.filename or "asset").stem + (".svg" if extension == ".svg" else ".webp")
        return Response(
            content=optimized_bytes,
            media_type="image/svg+xml" if extension == ".svg" else "image/webp",
            headers={"Content-Disposition": f'attachment; filename="{output_name}"'},
        )
    except subprocess.CalledProcessError as error:
        raise HTTPException(status_code=500, detail=error.stderr.decode("utf-8", errors="ignore")) from error
    except FileNotFoundError as error:
        if str(error.filename) == "ffmpeg":
            raise HTTPException(
                status_code=500,
                detail="ffmpeg is not installed on the server. Install ffmpeg, then retry compression.",
            ) from error
        raise HTTPException(status_code=500, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Compression failed: {error}") from error
    finally:
        # Keep no temporary files around after each request.
        shutil.rmtree(temp_dir, ignore_errors=True)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


if DIST_DIR.exists():
    app.mount("/", StaticFiles(directory=DIST_DIR, html=True), name="frontend")
