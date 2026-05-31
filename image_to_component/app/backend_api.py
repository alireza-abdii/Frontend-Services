import re
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles

ALLOWED_EXTENSIONS = {".svg"}
BASE_DIR = Path(__file__).resolve().parent
DIST_DIR = BASE_DIR / "dist"

app = FastAPI(title="Image To Component API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/convert", response_class=PlainTextResponse)
async def convert_to_component(file: UploadFile = File(...), output_format: str = Query(default="tsx")):
    extension = Path(file.filename or "").suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Path-based reusable component output requires an SVG file. Please upload SVG.",
        )

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    raw_svg = content.decode("utf-8", errors="ignore").strip()
    svg_match = re.search(r"<svg\b([^>]*)>([\s\S]*?)</svg>", raw_svg, flags=re.IGNORECASE)
    if not svg_match:
        raise HTTPException(status_code=400, detail="Invalid SVG markup.")

    def _to_react_attr(attr_name: str) -> str:
        direct = {
            "class": "className",
            "for": "htmlFor",
            "clip-path": "clipPath",
            "clip-rule": "clipRule",
            "fill-rule": "fillRule",
            "stroke-width": "strokeWidth",
            "stroke-linecap": "strokeLinecap",
            "stroke-linejoin": "strokeLinejoin",
            "stroke-miterlimit": "strokeMiterlimit",
            "stroke-dasharray": "strokeDasharray",
            "stroke-dashoffset": "strokeDashoffset",
            "stop-color": "stopColor",
            "stop-opacity": "stopOpacity",
            "color-interpolation-filters": "colorInterpolationFilters",
            "xlink:href": "xlinkHref",
            "xml:space": "xmlSpace",
        }
        if attr_name in direct:
            return direct[attr_name]
        if "-" in attr_name:
            head, *tail = attr_name.split("-")
            return head + "".join(part[:1].upper() + part[1:] for part in tail)
        return attr_name

    def _convert_attrs(block: str) -> str:
        def repl(match: re.Match[str]) -> str:
            name = match.group(1)
            return f'{_to_react_attr(name)}='

        return re.sub(r'([A-Za-z_:][A-Za-z0-9_:.-]*)\s*=', repl, block)

    svg_attrs = _convert_attrs(svg_match.group(1)).strip()
    inner_markup = _convert_attrs(svg_match.group(2).strip())
    component_name = "".join(part.capitalize() for part in Path(file.filename or "icon").stem.replace("-", "_").split("_")) or "Icon"
    target = output_format.lower().strip()
    if target not in {"tsx", "jsx"}:
        raise HTTPException(status_code=400, detail="output_format must be either 'tsx' or 'jsx'.")

    if target == "tsx":
        code = f"""import {{ SVGProps }} from "react";

export function {component_name}(props: SVGProps<SVGSVGElement>) {{
  return (
    <svg {svg_attrs} {{...props}}>
      {inner_markup}
    </svg>
  );
}}
"""
    else:
        code = f"""export function {component_name}(props) {{
  return (
    <svg {svg_attrs} {{...props}}>
      {inner_markup}
    </svg>
  );
}}
"""

    file_name = f"{component_name}.{target}"
    return PlainTextResponse(content=code, headers={"Content-Disposition": f'attachment; filename="{file_name}"'})


if DIST_DIR.exists():
    app.mount("/", StaticFiles(directory=DIST_DIR, html=True), name="frontend")
