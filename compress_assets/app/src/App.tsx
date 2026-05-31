import { useEffect, useMemo, useState } from "react";
import { Download, FileImage, Loader2, UploadCloud } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";

type CompressionResult = {
  fileName: string;
  originalSize: number;
  compressedSize: number;
  reductionPercentage: number;
  downloadUrl: string;
};

function extractFileName(contentDisposition: string | null, fallbackName: string): string {
  if (!contentDisposition) return fallbackName;
  const match = contentDisposition.match(/filename="([^"]+)"/i);
  return match?.[1] ?? fallbackName;
}

async function compressImage(file: File): Promise<CompressionResult> {
  const formData = new FormData();
  formData.append("file", file);
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim() ?? "";

  const response = await fetch(`${apiBaseUrl}/api/compress`, {
    method: "POST",
    body: formData
  });

  if (!response.ok) {
    let detail = "Compression failed.";
    try {
      const parsed = (await response.json()) as { detail?: string };
      if (parsed?.detail) detail = parsed.detail;
    } catch {
      const text = await response.text();
      if (text) detail = text;
    }
    throw new Error(detail);
  }

  const compressedBlob = await response.blob();
  const compressedSize = compressedBlob.size;
  const originalSize = file.size;
  const reductionPercentage = ((originalSize - compressedSize) / originalSize) * 100;
  const fallbackName = file.name.replace(/\.(png|jpe?g|webp)$/i, ".webp");
  const contentDisposition = response.headers.get("content-disposition");

  return {
    fileName: extractFileName(contentDisposition, fallbackName),
    originalSize,
    compressedSize,
    reductionPercentage,
    downloadUrl: URL.createObjectURL(compressedBlob)
  };
}

function toMb(bytes: number): string {
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

export default function App() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<CompressionResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isDragActive, setIsDragActive] = useState(false);
  const [loadingLabel, setLoadingLabel] = useState("Preparing file...");

  const canCompress = useMemo(() => Boolean(file) && !loading, [file, loading]);

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
    setProgress(0);
  };

  const onFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    applySelectedFile(event.target.files?.[0] ?? null);
  };

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
    const droppedFile = event.dataTransfer.files?.[0] ?? null;
    applySelectedFile(droppedFile);
  };

  const onCompress = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);
    setResult(null);
    setLoadingLabel("Preparing file...");

    // Lightweight progress animation for perceived responsiveness.
    const ticker = window.setInterval(() => {
      setProgress((current) => (current >= 90 ? current : current + 10));
    }, 180);
    const loadingSteps = ["Preparing file...", "Uploading image...", "Optimizing with Python...", "Finalizing output..."];
    let loadingStepIndex = 0;
    const statusTicker = window.setInterval(() => {
      loadingStepIndex = Math.min(loadingStepIndex + 1, loadingSteps.length - 1);
      setLoadingLabel(loadingSteps[loadingStepIndex]);
    }, 850);

    try {
      const compressionResult = await compressImage(file);
      setResult(compressionResult);
      setProgress(100);
      setLoadingLabel("Compression complete.");
    } catch (caughtError) {
      if (caughtError instanceof Error) {
        setError(caughtError.message);
      } else {
        setError("Compression service is unavailable. Make sure your Python API is running.");
      }
      setProgress(0);
    } finally {
      window.clearInterval(ticker);
      window.clearInterval(statusTicker);
      setLoading(false);
    }
  };

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-4xl flex-col justify-center px-4 py-8 sm:px-6 sm:py-14">
      <section className="mb-6 sm:mb-8">
        <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">Compress Assets</h1>
        <p className="text-xs text-muted-foreground sm:text-sm">High-quality image compression with a refined workflow.</p>
      </section>

      <Card>
        <CardHeader>
          <CardTitle>Optimize Your Asset</CardTitle>
          <CardDescription>
            Upload a PNG, JPG, WEBP, or SVG image, then run compression while preserving visual quality.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-5">
          <label
            className={`group flex cursor-pointer flex-col items-center justify-center gap-2 rounded-xl border border-dashed bg-background px-4 py-8 text-center transition sm:px-6 sm:py-10 ${
              isDragActive ? "border-primary bg-muted/40" : "border-border hover:border-primary/60 hover:bg-muted/40"
            }`}
            onDragOver={onDragOver}
            onDragEnter={onDragOver}
            onDragLeave={onDragLeave}
            onDrop={onDrop}
          >
            <UploadCloud className="h-7 w-7 text-primary" />
            <p className="text-sm font-medium">Drop an image or click to browse</p>
            <p className="text-xs text-muted-foreground">PNG, JPG, JPEG, WEBP, SVG</p>
            <Input type="file" accept=".png,.jpg,.jpeg,.webp,.svg,image/svg+xml" className="hidden" onChange={onFileChange} />
          </label>

          {file ? (
            <div className="rounded-xl border border-border bg-background p-4">
              <div className="flex items-center gap-3">
                <FileImage className="h-5 w-5 text-primary" />
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium">{file.name}</p>
                  <p className="text-xs text-muted-foreground">{toMb(file.size)}</p>
                </div>
              </div>
            </div>
          ) : null}

          {loading ? (
            <div className="space-y-2 rounded-xl border border-border/70 bg-background/70 p-3">
              <div className="flex items-center justify-between gap-2">
                <p className="text-xs text-muted-foreground">{loadingLabel}</p>
                <span className="text-xs text-primary">{Math.round(progress)}%</span>
              </div>
              <Progress value={progress} />
            </div>
          ) : null}

          {error ? <p className="text-sm text-red-300">{error}</p> : null}

          {result ? (
            <div className="space-y-4 rounded-xl border border-primary/40 bg-background p-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <p className="text-sm text-muted-foreground">
                  Size: <span className="text-foreground">{toMb(result.originalSize)}</span> to{" "}
                  <span className="text-foreground">{toMb(result.compressedSize)}</span>
                </p>
                <span className="rounded-full border border-primary/40 px-3 py-1 text-xs text-primary">
                  {result.reductionPercentage.toFixed(1)}% smaller
                </span>
              </div>

              <a href={result.downloadUrl} download={result.fileName}>
                <Button className="w-full">
                  <Download className="mr-2 h-4 w-4" />
                  Download Optimized File
                </Button>
              </a>
            </div>
          ) : null}

          <Button onClick={onCompress} disabled={!canCompress} className="w-full" size="lg">
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Compressing...
              </>
            ) : (
              "Compress Asset"
            )}
          </Button>
        </CardContent>
      </Card>
    </main>
  );
}
