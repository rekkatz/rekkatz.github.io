#!/usr/bin/env python3
"""Generador inicial de SOC Weekly para el blog Bypasseados.

Recibe una edición en JSON, rellena la plantilla Markdown y genera una portada
SVG a partir de la plantilla maestra. No publica ni realiza llamadas externas.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
TOOL_DIR = Path(__file__).resolve().parent
ARTICLE_TEMPLATE = TOOL_DIR / "templates" / "article.md"
COVER_TEMPLATE = TOOL_DIR / "templates" / "cover.svg"


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"No existe el archivo de entrada: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"JSON no válido en {path}: {exc}") from exc


def require(data: dict[str, Any], key: str) -> Any:
    value = data.get(key)
    if value in (None, "", []):
        raise SystemExit(f"Falta el campo obligatorio: {key}")
    return value


def render(template: str, values: dict[str, Any]) -> str:
    result = template
    for key, value in values.items():
        result = result.replace("{{ " + key + " }}", str(value))

    unresolved = sorted(set(re.findall(r"{{\s*([a-zA-Z0-9_]+)\s*}}", result)))
    if unresolved:
        raise SystemExit("Variables sin resolver: " + ", ".join(unresolved))
    return result


def bullets(items: list[str], checkbox: bool = False) -> str:
    prefix = "- [ ]" if checkbox else "-"
    return "\n".join(f"{prefix} {item}" for item in items)


def priority_table(vulnerabilities: list[dict[str, Any]]) -> str:
    lines = [
        "| Prioridad | CVE | Producto | Severidad | Explotación activa | CISA KEV |",
        "|---|---|---|---:|:---:|:---:|",
    ]
    for vuln in vulnerabilities:
        lines.append(
            "| {priority} | {cve} | {product} | {severity} | {exploited} | {kev} |".format(
                priority=vuln.get("priority", "Alta"),
                cve=vuln["cve"],
                product=vuln["product"],
                severity=vuln.get("severity", "N/D"),
                exploited="Sí" if vuln.get("exploited") else "No",
                kev="Sí" if vuln.get("kev") else "No",
            )
        )
    return "\n".join(lines)


def vulnerability_section(vuln: dict[str, Any], featured: bool = False) -> str:
    heading = "###" if featured else "###"
    parts = [
        f"{heading} {vuln['cve']} — {vuln['product']}",
        "",
        f"**Prioridad:** {vuln.get('priority', 'Alta')}  ",
        f"**Severidad:** {vuln.get('severity', 'N/D')}  ",
        f"**Explotación activa:** {'Sí' if vuln.get('exploited') else 'No confirmada'}  ",
        f"**CISA KEV:** {'Sí' if vuln.get('kev') else 'No'}",
        "",
        "#### ¿Qué ocurre?",
        "",
        vuln["summary"].strip(),
        "",
        "#### Impacto",
        "",
        bullets(vuln.get("impact", [])),
        "",
        "#### Mitigación",
        "",
        bullets(vuln.get("mitigations", [])),
    ]

    detection = vuln.get("splunk_detection")
    if detection:
        parts.extend(
            [
                "",
                "#### Visibilidad en Splunk",
                "",
                detection.get("description", "Búsqueda inicial orientativa:"),
                "",
                "```spl",
                detection["query"].strip(),
                "```",
            ]
        )

    mitre = vuln.get("mitre", [])
    if mitre:
        parts.extend(["", "#### MITRE ATT&CK", ""])
        parts.extend(f"- **{item['id']}** — {item['name']}" for item in mitre)

    return "\n".join(part for part in parts if part is not None)


def references_section(references: list[dict[str, str]]) -> str:
    return "\n".join(
        f"- [{ref['title']}]({ref['url']})" for ref in references
    )


def generate(data: dict[str, Any], output_root: Path) -> tuple[Path, Path]:
    edition = int(require(data, "edition"))
    edition_padded = f"{edition:02d}"
    publication_date = str(require(data, "publication_date"))
    period = str(require(data, "period"))
    vulnerabilities = require(data, "vulnerabilities")
    if not isinstance(vulnerabilities, list) or not vulnerabilities:
        raise SystemExit("vulnerabilities debe ser una lista no vacía")

    slug = f"{publication_date}-soc-weekly-{edition_padded}"
    media_directory = slug

    exploited_count = sum(bool(v.get("exploited")) for v in vulnerabilities)
    kev_count = sum(bool(v.get("kev")) for v in vulnerabilities)
    rce_count = sum(bool(v.get("rce")) for v in vulnerabilities)

    featured = vulnerabilities[0]
    other_sections = "\n\n---\n\n".join(
        vulnerability_section(v) for v in vulnerabilities[1:]
    ) or "No se han incluido vulnerabilidades adicionales en esta edición."

    values = {
        "edition": edition,
        "edition_padded": edition_padded,
        "publication_date": publication_date,
        "period": period,
        "media_directory": media_directory,
        "executive_summary": require(data, "executive_summary"),
        "vulnerability_count": len(vulnerabilities),
        "exploited_count": exploited_count,
        "kev_count": kev_count,
        "rce_count": rce_count,
        "priority_table": priority_table(vulnerabilities),
        "featured_vulnerability": vulnerability_section(featured, featured=True),
        "vulnerability_sections": other_sections,
        "splunk_detection_corner": require(data, "splunk_detection_corner"),
        "soc_checklist": bullets(require(data, "soc_checklist"), checkbox=True),
        "administrator_recommendations": bullets(
            require(data, "administrator_recommendations")
        ),
        "references": references_section(require(data, "references")),
        "conclusion": require(data, "conclusion"),
    }

    article = render(ARTICLE_TEMPLATE.read_text(encoding="utf-8"), values)

    post_dir = output_root / "_posts" / publication_date[:4]
    post_path = post_dir / f"{slug}.md"
    post_dir.mkdir(parents=True, exist_ok=True)
    post_path.write_text(article.rstrip() + "\n", encoding="utf-8")

    cover_values = {
        "edition_padded": html.escape(edition_padded),
        "period": html.escape(period),
    }
    cover = render(COVER_TEMPLATE.read_text(encoding="utf-8"), cover_values)
    cover_dir = output_root / "assets" / "img" / "posts" / media_directory / "header"
    cover_path = cover_dir / f"card_soc_weekly_{edition_padded}.svg"
    cover_dir.mkdir(parents=True, exist_ok=True)
    cover_path.write_text(cover, encoding="utf-8")

    return post_path, cover_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Genera una edición de SOC Weekly")
    parser.add_argument("--input", required=True, type=Path, help="Edición en JSON")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=ROOT,
        help="Raíz donde escribir _posts y assets (por defecto, el repositorio)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data = load_json(args.input)
    post_path, cover_path = generate(data, args.output_root.resolve())
    print(f"Artículo generado: {post_path}")
    print(f"Portada SVG generada: {cover_path}")
    print("Estado editorial: published=false")
    return 0


if __name__ == "__main__":
    sys.exit(main())
