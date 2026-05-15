import type { ReactNode } from "react";

const LINKS = {
  pypi: "https://pypi.org/project/camoufox-turnstile/",
  github: "https://github.com/builker-col/turnstile-camoufox-sdk",
  integration:
    "https://github.com/builker-col/turnstile-camoufox-sdk/blob/main/INTEGRACION.md",
  lab: "https://turnstile-lab.builker.com/",
  issues: "https://github.com/builker-col/turnstile-camoufox-sdk/issues",
};

const SECTIONS = [
  { href: "#vision", label: "Visión general" },
  { href: "#instalacion", label: "Instalación" },
  { href: "#inicio-rapido", label: "Inicio rápido" },
  { href: "#arquitectura", label: "Arquitectura" },
  { href: "#pesos", label: "Pesos del modelo" },
  { href: "#api", label: "API" },
  { href: "#enlaces", label: "Enlaces" },
] as const;

function IconExternal({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      width="14"
      height="14"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
    >
      <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
      <polyline points="15 3 21 3 21 9" />
      <line x1="10" y1="14" x2="21" y2="3" />
    </svg>
  );
}

function DocLink({
  href,
  children,
}: {
  href: string;
  children: ReactNode;
}) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="inline-flex items-center gap-1 font-medium text-blue-600 underline decoration-blue-200 underline-offset-[3px] transition hover:text-blue-800 hover:decoration-blue-400"
    >
      {children}
      <IconExternal className="shrink-0 opacity-70" />
    </a>
  );
}

function CodeBlock({ code }: { code: string }) {
  return (
    <pre className="overflow-x-auto rounded-lg border border-slate-200 bg-white px-4 py-3 text-[13px] leading-relaxed text-slate-800 shadow-[0_1px_2px_rgba(15,23,42,0.04)]">
      <code className="font-mono">{code}</code>
    </pre>
  );
}

function SectionHeading({ children }: { children: ReactNode }) {
  return (
    <h2 className="border-b border-slate-200 pb-2 text-xl font-semibold tracking-tight text-slate-900">
      {children}
    </h2>
  );
}

function InlineCode({ children }: { children: ReactNode }) {
  return (
    <code className="rounded border border-slate-200 bg-white px-1.5 py-0.5 font-mono text-[0.875em] text-slate-800 shadow-sm">
      {children}
    </code>
  );
}

export default function Home() {
  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-50 border-b border-slate-200/90 bg-white/90 backdrop-blur-md">
        <div className="mx-auto flex h-14 max-w-6xl items-center justify-between gap-4 px-4 sm:px-6">
          <div className="flex min-w-0 items-center gap-3">
            <span className="truncate font-mono text-sm font-semibold tracking-tight text-slate-900">
              camoufox-turnstile
            </span>
            <span className="hidden shrink-0 rounded-md border border-slate-200 bg-slate-50 px-2 py-0.5 font-mono text-xs text-slate-600 sm:inline">
              v0.2.0
            </span>
          </div>
          <nav className="flex shrink-0 flex-wrap items-center justify-end gap-x-4 gap-y-1 text-sm">
            <DocLink href={LINKS.pypi}>PyPI</DocLink>
            <DocLink href={LINKS.github}>GitHub</DocLink>
            <DocLink href={LINKS.integration}>Integración</DocLink>
            <DocLink href={LINKS.lab}>Lab</DocLink>
          </nav>
        </div>
      </header>

      <div className="mx-auto flex max-w-6xl gap-10 px-4 py-10 sm:px-6 lg:py-14">
        <aside className="hidden w-52 shrink-0 lg:block">
          <nav
            className="sticky top-24 space-y-0.5 text-sm"
            aria-label="En esta página"
          >
            <p className="mb-3 text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500">
              En esta página
            </p>
            {SECTIONS.map((s) => (
              <a
                key={s.href}
                href={s.href}
                className="block rounded-md px-2 py-1.5 text-slate-600 transition hover:bg-white hover:text-slate-900 hover:shadow-sm"
              >
                {s.label}
              </a>
            ))}
          </nav>
        </aside>

        <main className="min-w-0 flex-1">
          <article className="max-w-2xl">
            <p className="text-xs font-semibold uppercase tracking-wider text-blue-600">
              Documentación
            </p>
            <h1 className="mt-2 text-3xl font-semibold tracking-tight text-slate-900 sm:text-[2.125rem] sm:leading-tight">
              Cloudflare Turnstile con Camoufox
            </h1>
            <p className="mt-5 text-lg leading-relaxed text-slate-600">
              SDK en Python para rellenar{" "}
              <InlineCode>cf-turnstile-response</InlineCode> con{" "}
              <strong className="font-semibold text-slate-800">Playwright
              async</strong>{" "}
              y un bucle de visión <strong className="font-semibold text-slate-800">YOLO</strong>{" "}
              (Ultralytics + OpenCV) incluido en el instalable estándar. El
              fallback DOM es opcional dentro del mismo flujo.
            </p>
            <div className="mt-10 flex flex-wrap gap-3">
              <a
                href={LINKS.pypi}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center rounded-lg bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-800"
              >
                Ver en PyPI
              </a>
              <a
                href={LINKS.integration}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center rounded-lg border border-slate-300 bg-white px-5 py-2.5 text-sm font-semibold text-slate-800 shadow-sm transition hover:border-slate-400 hover:bg-slate-50"
              >
                Guía INTEGRACION.md
              </a>
            </div>
          </article>

          <div className="mt-16 max-w-2xl space-y-14">
            <section id="vision" className="scroll-mt-28 space-y-4">
              <SectionHeading>Visión general</SectionHeading>
              <ul className="space-y-3 text-slate-600">
                <li className="flex gap-3">
                  <span
                    className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-blue-500"
                    aria-hidden
                  />
                  <span>
                    <InlineCode>solve_on_page</InlineCode> ejecuta siempre el
                    bucle YOLO (captura + inferencia) hasta token o tiempo
                    agotado.
                  </span>
                </li>
                <li className="flex gap-3">
                  <span
                    className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-blue-500"
                    aria-hidden
                  />
                  <span>
                    El extra <InlineCode>[yolo]</InlineCode> está vacío (solo
                    compatibilidad); Torch suele llegar vía Ultralytics.
                  </span>
                </li>
                <li className="flex gap-3">
                  <span
                    className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-blue-500"
                    aria-hidden
                  />
                  <span>
                    <InlineCode>SolveOptions.use_dom_fallback</InlineCode>: clics
                    heurísticos cuando no hay sugerencia clara desde el modelo.
                  </span>
                </li>
                <li className="flex gap-3">
                  <span
                    className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-blue-500"
                    aria-hidden
                  />
                  <span>
                    Alcance: widget Turn estándar; no otros captchas (reCAPTCHA,
                    hCaptcha, etc.).
                  </span>
                </li>
              </ul>
              <div className="rounded-xl border border-blue-100 bg-gradient-to-br from-blue-50/90 to-white p-5 text-sm leading-relaxed text-slate-700">
                Prueba rápida:{" "}
                <DocLink href={LINKS.lab}>Turnstile Lab</DocLink>. El ejemplo{" "}
                <InlineCode>examples/minimal.py</InlineCode> apunta ahí por
                defecto.
              </div>
            </section>

            <section id="instalacion" className="scroll-mt-28 space-y-5">
              <SectionHeading>Instalación</SectionHeading>
              <p className="text-slate-600 leading-relaxed">
                Dependencia principal <InlineCode>camoufox-turnstile</InlineCode>.
                Extra opcional{" "}
                <InlineCode>[s3]</InlineCode> si descargas pesos desde S3 privado.
              </p>
              <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">
                Terminal
              </p>
              <CodeBlock
                code={`pip install camoufox-turnstile
pip install 'camoufox-turnstile[s3]'  # opcional`}
              />
              <p className="text-sm text-slate-600">
                Binario Camoufox (una vez por máquina o imagen):
              </p>
              <CodeBlock code="camoufox fetch" />
            </section>

            <section id="inicio-rapido" className="scroll-mt-28 space-y-5">
              <SectionHeading>Inicio rápido</SectionHeading>
              <p className="text-slate-600 leading-relaxed">
                <InlineCode>camoufox_context_options</InlineCode> fija{" "}
                <InlineCode>device_scale_factor=1</InlineCode> para alinear vista
                y capturas con el modelo.
              </p>
              <CodeBlock
                code={`import asyncio
from camoufox.async_api import AsyncCamoufox
from camoufox_turnstile import (
    SolveOptions,
    camoufox_context_options,
    solve_on_page,
    DEFAULT_VIEWPORT,
)

async def main():
    async with AsyncCamoufox(headless=True) as browser:
        ctx = await browser.new_context(
            **camoufox_context_options(viewport=DEFAULT_VIEWPORT)
        )
        page = await ctx.new_page()
        await page.goto("https://turnstile-lab.builker.com/", wait_until="load")
        result = await solve_on_page(page, SolveOptions())
        print(result.visual_ok_via, len(result.token))
        await ctx.close()

asyncio.run(main())`}
              />
            </section>

            <section id="arquitectura" className="scroll-mt-28 space-y-5">
              <SectionHeading>Arquitectura</SectionHeading>
              <ol className="list-none space-y-4">
                {[
                  {
                    n: "1",
                    title: "Pesos",
                    body: (
                      <>
                        <InlineCode>ensure_yolo_weights</InlineCode> resuelve
                        ruta local, caché de usuario o descarga (HTTPS / env).
                      </>
                    ),
                  },
                  {
                    n: "2",
                    title: "Detector",
                    body: (
                      <>
                        <InlineCode>load_yolo_detector</InlineCode> carga el{" "}
                        <InlineCode>.pt</InlineCode>.
                      </>
                    ),
                  },
                  {
                    n: "3",
                    title: "Bucle",
                    body: (
                      <>
                        Captura del viewport, inferencia y clics según clases (
                        <InlineCode>success_mark</InlineCode>,{" "}
                        <InlineCode>target_checkbox</InlineCode>, etc.).
                      </>
                    ),
                  },
                  {
                    n: "4",
                    title: "Fallback DOM",
                    body: (
                      <>
                        Si aplica <InlineCode>use_dom_fallback</InlineCode>,
                        intentos heurísticos en el iframe.
                      </>
                    ),
                  },
                ].map((item) => (
                  <li key={item.n} className="flex gap-4">
                    <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-slate-200 bg-white font-mono text-xs font-semibold text-slate-700 shadow-sm">
                      {item.n}
                    </span>
                    <div>
                      <p className="font-semibold text-slate-900">
                        {item.title}
                      </p>
                      <p className="mt-1 text-slate-600 leading-relaxed">
                        {item.body}
                      </p>
                    </div>
                  </li>
                ))}
              </ol>
            </section>

            <section id="pesos" className="scroll-mt-28 space-y-5">
              <SectionHeading>Pesos del modelo</SectionHeading>
              <p className="text-slate-600 leading-relaxed">
                El modelo no va en el wheel; la primera ejecución puede
                descargarlo y guardarlo en caché (
                <InlineCode>platformdirs</InlineCode>, nombre típico{" "}
                <InlineCode>turnstile-yolo-latest.pt</InlineCode>).
              </p>
              <p className="text-sm text-slate-600 leading-relaxed">
                Orden habitual:{" "}
                <InlineCode>yolo_weights</InlineCode> /{" "}
                <InlineCode>TURNSTILE_YOLO_WEIGHTS</InlineCode>; caché; URL (
                <InlineCode>TURNSTILE_YOLO_WEIGHTS_URL</InlineCode>) o S3 (
                <InlineCode>TURNSTILE_YOLO_S3_URI</InlineCode> con{" "}
                <InlineCode>[s3]</InlineCode>). Variables adicionales: SHA256,
                forzar descarga, nombre de archivo en caché (ver README del
                proyecto).
              </p>
            </section>

            <section id="api" className="scroll-mt-28 space-y-5">
              <SectionHeading>Referencia rápida de API</SectionHeading>
              <p className="text-slate-600 leading-relaxed">
                Puntos de entrada habituales; el detalle está en el código fuente
                PyPI / repo.
              </p>
              <ul className="grid gap-2 sm:grid-cols-2">
                {[
                  "solve_on_page",
                  "SolveOptions",
                  "read_turnstile_token",
                  "wait_turnstile_token",
                  "camoufox_context_options",
                  "ensure_yolo_weights",
                  "load_yolo_detector",
                  "assist_turnstile_clicks",
                  "assist_turnstile_vision_clicks",
                ].map((name) => (
                  <li key={name}>
                    <span className="block rounded-lg border border-slate-200 bg-white px-3 py-2 font-mono text-[13px] text-slate-800 shadow-sm">
                      {name}()
                    </span>
                  </li>
                ))}
              </ul>
            </section>

            <section id="enlaces" className="scroll-mt-28 space-y-4">
              <SectionHeading>Enlaces útiles</SectionHeading>
              <ul className="space-y-2 text-slate-600">
                <li>
                  <DocLink href={LINKS.integration}>
                    Integración paso a paso (INTEGRACION.md)
                  </DocLink>
                </li>
                <li>
                  <DocLink href={LINKS.github}>Código fuente</DocLink>
                </li>
                <li>
                  <DocLink href={LINKS.issues}>Issues</DocLink>
                </li>
              </ul>
            </section>
          </div>

          <footer className="mt-16 max-w-2xl border-t border-slate-200 pt-10 pb-16 text-sm text-slate-500">
            <p>
              Licencia{" "}
              <span className="font-semibold text-slate-700">MIT</span>. Uso
              responsable y conforme a términos del sitio y ley aplicable.
            </p>
            <p className="mt-3">
              El paquete canónico:{" "}
              <DocLink href={LINKS.pypi}>PyPI · camoufox-turnstile</DocLink>
            </p>
          </footer>
        </main>
      </div>
    </div>
  );
}
