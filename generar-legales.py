#!/usr/bin/env python3
"""
Genera terminos.html y privacidad.html a partir de YoogaAlive/LegalView.swift.

Por qué un generador y no dos HTML escritos a mano: Apple compara el texto que
enseña la app con el de la URL pública. Si un día cambias una cláusula en Swift
y olvidas la web, quedan dos versiones distintas de lo mismo — que es
exactamente la clase de contradicción que hace fallar una revisión.

Uso, desde la raíz del proyecto:
    python3 landing/generar-legales.py
"""

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SWIFT = ROOT / "YoogaAlive" / "LegalView.swift"
OUT = ROOT / "landing"

TITLES = {
    "terms": ("Terms of Service", "Términos y condiciones"),
    "privacy": ("Privacy Policy", "Política de privacidad"),
}
FILENAMES = {"terms": "terminos.html", "privacy": "privacidad.html"}


def extract(source: str, name: str) -> str:
    """Saca el contenido de `private static let <name> = \"\"\" ... \"\"\"`."""
    pattern = rf'private static let {name} = """\n(.*?)\n\s*"""'
    match = re.search(pattern, source, re.DOTALL)
    if not match:
        raise SystemExit(f"No encontré {name} en {SWIFT}")
    # El literal va indentado 4 espacios dentro del enum; se quita.
    return "\n".join(line[4:] if line.startswith("    ") else line
                     for line in match.group(1).split("\n"))


def to_html(text: str) -> str:
    """Los bloques van separados por línea en blanco. La primera línea de cada
    bloque que empieza con `N ·` es un encabezado; el resto, párrafo."""
    out = []
    for block in text.strip().split("\n\n"):
        lines = [l.strip() for l in block.split("\n") if l.strip()]
        if not lines:
            continue
        if re.match(r"^\d+\s·", lines[0]):
            out.append(f"<h2>{html.escape(lines[0])}</h2>")
            rest = lines[1:]
        else:
            rest = lines
        for line in rest:
            css = ' class="updated"' if line.lower().startswith(
                ("last updated", "última actualización")) else ""
            out.append(f"<p{css}>{html.escape(line)}</p>")
    return "\n".join(out)


PAGE = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title_es} — Hane Yoga</title>
<meta name="description" content="{title_es} de Hane Yoga.">
<meta name="robots" content="index,follow">
<!-- GENERADO por landing/generar-legales.py desde YoogaAlive/LegalView.swift.
     No editar a mano: se sobrescribe. Cambia el texto en Swift y regenera. -->
<style>
  :root{{
    --carbon-900:#0D0C0B; --cream-100:#FFFBF7; --cream-300:#F9EBE0;
    --ink:var(--cream-100); --ink-body:rgba(249,235,224,.82);
    --ink-soft:rgba(231,212,198,.62); --border:rgba(255,255,255,.12);
    --display:"New York",Georgia,"Iowan Old Style",serif;
    --body:-apple-system,BlinkMacSystemFont,"SF Pro Text","Segoe UI",Roboto,sans-serif;
  }}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:var(--carbon-900);color:var(--ink);font-family:var(--body);
    line-height:1.62;-webkit-font-smoothing:antialiased}}
  .wrap{{max-width:680px;margin:0 auto;padding:0 24px 90px}}
  header{{padding:64px 0 30px;border-bottom:1px solid var(--border);margin-bottom:34px}}
  .mark{{font-family:var(--display);text-transform:uppercase;letter-spacing:.22em;
    font-size:12px;color:var(--ink-soft);margin-bottom:26px;display:block;
    text-decoration:none}}
  h1{{font-family:var(--display);font-weight:600;text-transform:uppercase;
    letter-spacing:.05em;line-height:1.15;font-size:clamp(26px,5vw,38px)}}
  h2{{font-family:var(--body);font-weight:600;font-size:16px;letter-spacing:.01em;
    color:var(--ink);margin:34px 0 10px}}
  p{{color:var(--ink-body);font-size:15.5px;font-weight:300;margin-bottom:12px}}
  p.updated{{color:var(--ink-soft);font-size:13.5px;margin-bottom:4px}}
  .langs{{display:flex;gap:10px;margin:30px 0 0}}
  .langs a{{font-size:13px;color:var(--ink-soft);text-decoration:none;
    border:1px solid var(--border);border-radius:999px;padding:6px 15px}}
  .langs a[aria-current]{{color:var(--carbon-900);background:var(--cream-300);
    border-color:var(--cream-300)}}
  section{{display:none}} section:target{{display:block}}
  body:not(:has(section:target)) section#es{{display:block}}
  footer{{margin-top:56px;padding-top:24px;border-top:1px solid var(--border);
    font-size:13px;color:var(--ink-soft)}}
  footer a{{color:var(--ink-soft)}}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <a class="mark" href="index.html">Hane Yoga</a>
    <h1>{title_es}</h1>
    <nav class="langs">
      <a href="#es" aria-current="page">Español</a>
      <a href="#en">English</a>
    </nav>
  </header>

  <section id="es">
{body_es}
  </section>

  <section id="en">
    <h1 style="font-size:22px;margin-bottom:18px">{title_en}</h1>
{body_en}
  </section>

  <footer>
    <p>Hane Yoga · <a href="mailto:adavidrobayo7@gmail.com">adavidrobayo7@gmail.com</a></p>
  </footer>
</div>
</body>
</html>
"""


def main() -> None:
    source = SWIFT.read_text(encoding="utf-8")
    for doc, (title_en, title_es) in TITLES.items():
        page = PAGE.format(
            title_en=title_en,
            title_es=title_es,
            body_es=to_html(extract(source, f"{doc}ES")),
            body_en=to_html(extract(source, f"{doc}EN")),
        )
        path = OUT / FILENAMES[doc]
        path.write_text(page, encoding="utf-8")
        print(f"✓ {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
