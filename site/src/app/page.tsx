import Image from "next/image";
import type { ReactNode } from "react";

const LINKS = {
  pypi: "https://pypi.org/project/camoufox-turnstile/",
  github: "https://github.com/builker-col/turnstile-camoufox-sdk",
  integration:
    "https://github.com/builker-col/turnstile-camoufox-sdk/blob/main/INTEGRACION.md",
  lab: "https://turnstile-lab.builker.com/",
  issues:
    "https://github.com/builker-col/turnstile-camoufox-sdk/issues",
};

function CodeBlock({
  label,
  code,
}: {
  label?: string;
  code: string;
}) {
  return (
    <div className="group relative">
      {label ? (
        <p className="mb-2 text-xs font-medium uppercase tracking-wide text-zinc-500 dark:text-zinc-400">
          {label}
        </p>
      ) : null}
      <pre className="overflow-x-auto rounded-xl border border-zinc-200 bg-zinc-950 px-4 py-3 text-sm leading-relaxed text-zinc-100 shadow-inner dark:border-zinc-800">
        <code className="font-mono">{code}</code>
      </pre>
    </div>
  );
}

function NavLink({
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
      className="text-sm font-medium text-sky-700 underline-offset-4 transition hover:text-sky-900 hover:underline dark:text-sky-400 dark:hover:text-sky-300"
    >
      {children}
    </a>
  );
}

export default function Home() {
  return (
    <>
      <header className="border-b border-zinc-200/80 bg-white/90 backdrop-blur dark:border-zinc-800 dark:bg-zinc-950/90">
        <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-3 px-4 py-4 sm:px-6">
          <p className="font-mono text-sm font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
            camoufox-turnstile
          </p>
          <nav className="flex flex-wrap items-center gap-x-5 gap-y-2">
            <NavLink href={LINKS.pypi}>PyPI</NavLink>
            <NavLink href={LINKS.github}>Código</NavLink>
            <NavLink href={LINKS.integration}>Integración</NavLink>
            <NavLink href={LINKS.lab}>Turnstile Lab</NavLink>
          </nav>
        </div>
      </header>

      <main className="flex-1">
        <section className="border-b border-zinc-200 bg-gradient-to-b from-zinc-50 to-white dark:border-zinc-800 dark:from-zinc-950 dark:to-zinc-900">
          <div className="mx-auto grid max-w-5xl gap-10 px-4 py-16 sm:px-6 lg:grid-cols-[1fr_1.05fr] lg:items-center lg:gap-12 lg:py-20">
            <div>
              <p className="mb-3 text-sm font-medium text-sky-700 dark:text-sky-400">
                SDK en Python · PyPI
              </p>
              <h1 className="text-balance text-3xl font-semibold tracking-tight text-zinc-900 sm:text-4xl dark:text-zinc-50">
                Turnstile con{" "}
                <span className="text-sky-700 dark:text-sky-400">Camoufox</span>{" "}
                y Playwright async
              </h1>
              <p className="mt-4 max-w-xl text-lg leading-relaxed text-zinc-600 dark:text-zinc-400">
                Automatiza el campo oculto{" "}
                <code className="rounded bg-zinc-200 px-1.5 py-0.5 font-mono text-sm dark:bg-zinc-800 dark:text-zinc-200">
                  cf-turnstile-response
                </code>
                . Elige modo visión con YOLO (extra opcional) o heurística solo
                DOM, sin cargar otros captchas.
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                <a
                  href={LINKS.pypi}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center justify-center rounded-full bg-zinc-900 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-zinc-800 dark:bg-sky-600 dark:hover:bg-sky-500"
                >
                  Instalar desde PyPI
                </a>
                <a
                  href={LINKS.github}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center justify-center rounded-full border border-zinc-300 bg-white px-5 py-2.5 text-sm font-semibold text-zinc-900 transition hover:bg-zinc-50 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100 dark:hover:bg-zinc-800"
                >
                  Ver en GitHub
                </a>
              </div>
            </div>
            <figure className="relative overflow-hidden rounded-2xl border border-zinc-200 bg-white shadow-lg dark:border-zinc-800 dark:bg-zinc-950">
              <Image
                src="/image1.png"
                alt="Ejemplo visual del SDK camoufox-turnstile con Turnstile"
                width={1200}
                height={675}
                className="h-auto w-full object-contain"
                priority
                sizes="(max-width: 1024px) 100vw, 50vw"
              />
              <figcaption className="sr-only">
                Vista del SDK con widget Turnstile
              </figcaption>
            </figure>
          </div>
        </section>

        <section
          id="instalacion"
          className="border-b border-zinc-200 dark:border-zinc-800"
        >
          <div className="mx-auto max-w-5xl px-4 py-16 sm:px-6">
            <h2 className="text-2xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
              Instalación
            </h2>
            <p className="mt-3 max-w-2xl text-zinc-600 dark:text-zinc-400">
              Publicado como{" "}
              <span className="font-mono text-zinc-800 dark:text-zinc-200">
                camoufox-turnstile
              </span>
              . Para visión YOLO añade el extra{" "}
              <span className="font-mono text-zinc-800 dark:text-zinc-200">
                [yolo]
              </span>
              ; los pesos se descargan en caché la primera vez.
            </p>
            <div className="mt-8 grid gap-6 sm:grid-cols-2">
              <CodeBlock
                label="Base"
                code='pip install camoufox-turnstile'
              />
              <CodeBlock
                label="Con YOLO (Ultralytics + OpenCV)"
                code='pip install "camoufox-turnstile[yolo]"'
              />
            </div>
            <p className="mt-8 text-sm text-zinc-500 dark:text-zinc-400">
              Instala Camoufox en el sistema y ejecuta una vez por máquina:{" "}
              <code className="rounded bg-zinc-100 px-1.5 py-0.5 font-mono text-zinc-800 dark:bg-zinc-800 dark:text-zinc-200">
                camoufox fetch
              </code>
              . Torch CPU/GPU lo eliges aparte según tu entorno.
            </p>
          </div>
        </section>

        <section className="border-b border-zinc-200 bg-zinc-50/80 dark:border-zinc-800 dark:bg-zinc-950/50">
          <div className="mx-auto max-w-5xl px-4 py-16 sm:px-6">
            <h2 className="text-2xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
              Modos
            </h2>
            <ul className="mt-10 grid gap-8 sm:grid-cols-2">
              <li className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
                <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
                  Visión YOLO
                </h3>
                <p className="mt-2 text-zinc-600 dark:text-zinc-400">
                  Captura periódica e inferencia con detección del widget:
                  marca de éxito, checkbox y contenedor; espera del token en el
                  campo estándar.
                </p>
              </li>
              <li className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
                <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
                  Solo DOM
                </h3>
                <p className="mt-2 text-zinc-600 dark:text-zinc-400">
                  Heurística de clics sobre el iframe Turnstile, sin modelo ni
                  extra{" "}
                  <span className="font-mono text-sm">[yolo]</span>. Útil para
                  iterar rápido o entornos mínimos.
                </p>
              </li>
            </ul>
          </div>
        </section>

        <section>
          <div className="mx-auto max-w-5xl px-4 py-16 sm:px-6">
            <h2 className="text-2xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
              Probar y documentar
            </h2>
            <p className="mt-3 max-w-2xl text-zinc-600 dark:text-zinc-400">
              El repositorio incluye un ejemplo mínimo y una guía paso a paso
              para integrar el SDK en cualquier proyecto Python.
            </p>
            <div className="mt-8 flex flex-col gap-4 sm:flex-row sm:flex-wrap">
              <a
                href={LINKS.lab}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex rounded-xl border border-zinc-200 bg-white px-5 py-4 text-sm font-semibold text-zinc-900 shadow-sm transition hover:border-sky-300 hover:bg-sky-50 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100 dark:hover:border-sky-600 dark:hover:bg-zinc-800"
              >
                Turnstile Lab (página de pruebas)
              </a>
              <a
                href={LINKS.integration}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex rounded-xl border border-zinc-200 bg-white px-5 py-4 text-sm font-semibold text-zinc-900 shadow-sm transition hover:border-sky-300 hover:bg-sky-50 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100 dark:hover:border-sky-600 dark:hover:bg-zinc-800"
              >
                Guía INTEGRACION.md
              </a>
            </div>
          </div>
        </section>
      </main>

      <footer className="mt-auto border-t border-zinc-200 bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-950">
        <div className="mx-auto flex max-w-5xl flex-col gap-4 px-4 py-10 sm:flex-row sm:items-center sm:justify-between sm:px-6">
          <p className="text-sm text-zinc-600 dark:text-zinc-400">
            Licencia{" "}
            <span className="font-medium text-zinc-800 dark:text-zinc-200">
              MIT
            </span>
            . Respeta los términos de uso de cada sitio y la legislación
            aplicable.
          </p>
          <div className="flex flex-wrap gap-4">
            <NavLink href={LINKS.pypi}>PyPI</NavLink>
            <NavLink href={LINKS.issues}>Issues</NavLink>
            <NavLink href={LINKS.github}>Repositorio</NavLink>
          </div>
        </div>
      </footer>
    </>
  );
}
