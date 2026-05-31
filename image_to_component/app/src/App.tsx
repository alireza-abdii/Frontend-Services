import { useEffect, useState } from "react";
import { Download, FileImage, Loader2, UploadCloud } from "lucide-react";

type ConversionResult = {
  fileName: string;
  code: string;
};

async function convertImage(file: File, outputFormat: "tsx" | "jsx"): Promise<ConversionResult> {
  const formData = new FormData();
  formData.append("file", file);
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim() ?? "";

  const response = await fetch(`${apiBaseUrl}/api/convert?output_format=${outputFormat}`, {
    method: "POST",
    body: formData
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || "Conversion failed.");
  }

  const code = await response.text();
  const fallbackName = `${file.name.replace(/\.[^/.]+$/, "")}.${outputFormat}`;
  const contentDisposition = response.headers.get("content-disposition");
  const match = contentDisposition?.match(/filename="([^"]+)"/i);
  return { fileName: match?.[1] ?? fallbackName, code };
}

export default function App() {
  const [file, setFile] = useState<File | null>(null);
  const [outputFormat, setOutputFormat] = useState<"tsx" | "jsx">("tsx");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ConversionResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isDragActive, setIsDragActive] = useState(false);

  useEffect(() => {
    const preventBrowserFileOpen = (event: DragEvent) => {
      event.preventDefault();
    };

    window.addEventListener("dragover", preventBrowserFileOpen);
    window.addEventListener("drop", preventBrowserFileOpen);

    return () => {
      window.removeEventListener("dragover", preventBrowserFileOpen);
      window.removeEventListener("drop", preventBrowserFileOpen);
    };
  }, []);

  const applySelectedFile = (nextFile: File | null) => {
    setFile(nextFile);
    setResult(null);
    setError(null);
  };

  const isSvgSelected = file ? /\.svg$/i.test(file.name) || file.type === "image/svg+xml" : false;

  const onDragOver = (event: React.DragEvent<HTMLLabelElement>) => {
    event.preventDefault();
    setIsDragActive(true);
  };

  const onDragLeave = (event: React.DragEvent<HTMLLabelElement>) => {
    event.preventDefault();
    setIsDragActive(false);
  };

  const onDrop = (event: React.DragEvent<HTMLLabelElement>) => {
    event.preventDefault();
    setIsDragActive(false);
    const droppedFile = event.dataTransfer?.files && event.dataTransfer.files.length > 0 ? event.dataTransfer.files[0] : null;
    applySelectedFile(droppedFile);
  };

  const downloadCode = () => {
    if (!result) return;
    const blob = new Blob([result.code], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = result.fileName;
    a.click();
    URL.revokeObjectURL(url);
  };

  const onConvert = async () => {
    if (!file) return;
    if (!isSvgSelected) {
      setError("For path-based reusable component output, please upload an SVG file.");
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const converted = await convertImage(file, outputFormat);
      setResult(converted);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Conversion failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-4xl flex-col justify-center px-4 py-8 sm:px-6 sm:py-14">
      <section className="mb-6 sm:mb-8">
        <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">Image To TSX/JSX Component</h1>
        <p className="text-xs text-muted-foreground sm:text-sm">Upload icon images and get a ready-to-use component output.</p>
      </section>

      <div className="rounded-xl border border-border bg-card p-4 shadow-luxe sm:p-6">
        <label
          className={`flex cursor-pointer flex-col items-center gap-2 rounded-xl border border-dashed bg-background px-4 py-8 text-center transition ${
            isDragActive ? "border-primary bg-muted/40" : "border-border"
          }`}
          onDragOver={onDragOver}
          onDragEnter={onDragOver}
          onDragLeave={onDragLeave}
          onDrop={onDrop}
        >
          <UploadCloud className="h-7 w-7 text-primary" />
          <p className="text-sm font-medium">Drop image or click to browse</p>
          <p className="text-xs text-muted-foreground">Best result: SVG (path/defs/groups preserved)</p>
          <input
            type="file"
            className="hidden"
            accept=".png,.jpg,.jpeg,.webp,.svg,image/svg+xml"
            onChange={(event) => {
              const selected = event.currentTarget.files && event.currentTarget.files.length > 0 ? event.currentTarget.files[0] : null;
              applySelectedFile(selected);
            }}
          />
        </label>

        {file ? (
          <div className="mt-3 rounded-xl border border-border bg-background p-3">
            <div className="flex items-center gap-2">
              <FileImage className="h-4 w-4 text-primary" />
              <p className="truncate text-sm">{file.name}</p>
            </div>
            <p className="mt-1 text-xs text-muted-foreground">
              {(file.size / 1024).toFixed(1)} KB {isSvgSelected ? "• SVG detected" : "• Non-SVG selected"}
            </p>
          </div>
        ) : null}

        {file && !isSvgSelected ? (
          <p className="mt-3 text-xs text-amber-300">Selected file is not SVG. Choose SVG to generate path-based component code.</p>
        ) : null}

        <div className="mt-4 flex flex-wrap items-center gap-2">
          <p className="text-xs text-muted-foreground">Output format:</p>
          <button
            type="button"
            onClick={() => setOutputFormat("tsx")}
            className={`rounded-lg border px-3 py-1 text-xs ${outputFormat === "tsx" ? "border-primary text-primary" : "border-border"}`}
          >
            TSX
          </button>
          <button
            type="button"
            onClick={() => setOutputFormat("jsx")}
            className={`rounded-lg border px-3 py-1 text-xs ${outputFormat === "jsx" ? "border-primary text-primary" : "border-border"}`}
          >
            JSX
          </button>
        </div>

        <button
          type="button"
          onClick={onConvert}
          disabled={!file || loading}
          className="mt-4 inline-flex w-full items-center justify-center rounded-xl bg-primary px-4 py-2 font-medium text-black disabled:opacity-60"
        >
          {loading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Converting...
            </>
          ) : (
            "Convert to Component"
          )}
        </button>

        {error ? <p className="mt-4 text-sm text-red-300">{error}</p> : null}

        {result ? (
          <div className="mt-4 space-y-3 rounded-xl border border-border bg-background p-3">
            <div className="flex items-center justify-between gap-2">
              <p className="truncate text-sm">{result.fileName}</p>
              <button
                type="button"
                onClick={downloadCode}
                className="inline-flex items-center rounded-lg border border-border px-3 py-1.5 text-xs"
              >
                <Download className="mr-1 h-3 w-3" />
                Download
              </button>
            </div>
            <pre className="max-h-72 overflow-auto rounded-lg bg-muted p-3 text-xs text-foreground">{result.code}</pre>
          </div>
        ) : null}
      </div>
    </main>
  );
}
