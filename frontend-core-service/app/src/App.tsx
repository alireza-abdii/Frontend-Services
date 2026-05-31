import { useMemo, useState } from "react";
import { Button } from "@/components/ui/button";

type TabKey = "compress" | "component";

export default function App() {
  const [activeTab, setActiveTab] = useState<TabKey>("compress");
  const serviceUrls = useMemo(() => {
    const protocol = window.location.protocol;
    const host = window.location.hostname;
    return {
      compress: `${protocol}//${host}:8000`,
      component: `${protocol}//${host}:8100`
    };
  }, []);
  const tabConfig: Record<TabKey, { title: string; description: string; url: string }> = {
    compress: {
      title: "Compress Assets",
      description: "Optimize images with high visual quality retention.",
      url: serviceUrls.compress
    },
    component: {
      title: "Image To Component",
      description: "Convert icon images into reusable TSX/JSX components.",
      url: serviceUrls.component
    }
  };
  const active = useMemo(() => tabConfig[activeTab], [activeTab, tabConfig]);

  return (
    <main className="mx-auto h-screen w-full max-w-6xl overflow-hidden px-4 py-4 sm:px-6 sm:py-6">
      <div className="flex h-full min-h-0 flex-col">
        <header className="mb-4 flex items-center gap-3 sm:mb-5 sm:gap-4">
          <img src="/logo.svg" alt="Core Landing Logo" className="h-10 w-10 rounded-lg border border-border bg-card p-1 sm:h-12 sm:w-12" />
          <div>
            <h1 className="text-2xl font-semibold sm:text-3xl">Frontend Core Service</h1>
            <p className="mt-1 text-sm text-muted-foreground">Microfrontend landing for internal optimization tools.</p>
          </div>
        </header>

        <nav className="mb-3 flex flex-wrap gap-2" aria-label="Service tabs">
          {(Object.keys(tabConfig) as TabKey[]).map((tab) => (
            <Button
              key={tab}
              variant={tab === activeTab ? "default" : "outline"}
              onClick={() => setActiveTab(tab)}
              className="px-4 py-2 text-xs sm:text-sm"
            >
              {tabConfig[tab].title}
            </Button>
          ))}
        </nav>

        <section className="min-h-0 flex-1 overflow-hidden rounded-xl border border-border bg-card" aria-label={active.title}>
          <iframe src={active.url} title={active.title} className="h-full w-full border-0 bg-background" loading="lazy" />
        </section>
        <p className="mt-2 text-xs text-muted-foreground sm:text-sm">{active.description}</p>
      </div>
    </main>
  );
}
