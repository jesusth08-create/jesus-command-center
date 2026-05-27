#!/usr/bin/env python3
"""
Jesús Command Center — Notion Sync
Uso: python3 update.py
Actualiza Rocks, Issues y Flota desde Notion → index.html → GitHub Pages
"""

import json, re, subprocess, sys
from datetime import datetime
from urllib import request, error

# ── CONFIG ─────────────────────────────────────────────────────────────────────
# Pega tu Notion Integration Token aquí (o crea var de entorno NOTION_TOKEN)
# Cómo obtenerlo: https://www.notion.so/my-integrations → New integration → copy secret
import os
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "")  # export NOTION_TOKEN=secret_xxx

# IDs de las bases de datos (ya creadas en Notion)
DB_ROCKS   = "1809896607c8426e9209f615fa4e11ee"
DB_ISSUES  = "aa154cb6e36143069cb455114e7ed77b"
DB_FLOTA   = "2facdb6122b9408d9938f4261760401f"
DB_OOS     = "bb2a81214910492b9adbb525b6978bdc"
DB_SCORECARD = "52a416dba38044cb91935d1e0ac8db23"

HTML_FILE  = "index.html"
# ───────────────────────────────────────────────────────────────────────────────


def notion_query(database_id, filter_body=None):
    """Consulta una base de datos de Notion y devuelve las páginas."""
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    body = json.dumps(filter_body or {}).encode()
    req = request.Request(url, data=body, headers=headers, method="POST")
    try:
        with request.urlopen(req) as resp:
            return json.loads(resp.read())["results"]
    except error.HTTPError as e:
        print(f"❌ Error Notion API {database_id}: {e.code} {e.reason}")
        if e.code == 401:
            print("   → Token inválido o bases de datos no compartidas con tu integración.")
        sys.exit(1)


def prop(page, key, ptype="title"):
    """Extrae el valor de una propiedad de Notion."""
    props = page.get("properties", {})
    p = props.get(key)
    if not p:
        return None
    t = p.get("type")
    if t == "title":
        items = p.get("title", [])
        return items[0]["plain_text"] if items else ""
    if t == "rich_text":
        items = p.get("rich_text", [])
        return items[0]["plain_text"] if items else ""
    if t == "select":
        s = p.get("select")
        return s["name"] if s else None
    if t == "number":
        return p.get("number")
    if t == "checkbox":
        return p.get("checkbox", False)
    if t == "date":
        d = p.get("date")
        return d["start"] if d else None
    return None


def fmt_date(iso):
    """2026-06-30 → 30 Jun 2026"""
    if not iso:
        return "—"
    try:
        return datetime.strptime(iso, "%Y-%m-%d").strftime("%-d %b %Y")
    except:
        return iso


# ── FETCH ROCKS ────────────────────────────────────────────────────────────────
def fetch_rocks():
    pages = notion_query(DB_ROCKS, {
        "filter": {"property": "Trimestre", "select": {"equals": "Q2 2026"}}
    })
    status_map = {
        "On Track":  "on-track",
        "En Proceso":"on-track",
        "Off Track": "off-track",
        "Completo":  "done"
    }
    rocks = []
    for i, p in enumerate(pages, 1):
        st_raw = prop(p, "Status", "select") or "Off Track"
        avance = prop(p, "% Avance", "number") or 0
        deadline = prop(p, "Fecha Límite", "date")
        rocks.append({
            "num":      i,
            "titulo":   prop(p, "Rock") or "Rock sin título",
            "owner":    prop(p, "Owner", "select") or "Jesús",
            "deadline": fmt_date(deadline),
            "status":   status_map.get(st_raw, "off-track"),
            "notas":    prop(p, "Notas", "rich_text") or f"Avance: {avance}%"
        })
    return rocks


# ── FETCH ISSUES ───────────────────────────────────────────────────────────────
def fetch_issues():
    pages = notion_query(DB_ISSUES, {
        "filter": {"property": "Status", "select": {"does_not_equal": "Resuelto"}},
        "sorts": [{"property": "Prioridad", "direction": "ascending"}]
    })
    priority_map = {"Alta": "alta", "Media": "media", "Baja": "baja"}
    status_map   = {"Abierto": "abierto", "En Proceso": "en-proceso", "Resuelto": "resuelto"}
    issues = []
    for p in pages:
        fecha_raw = prop(p, "Fecha", "date")
        fecha_str = fmt_date(fecha_raw) if fecha_raw else datetime.now().strftime("%b %Y")
        issues.append({
            "desc":     prop(p, "Issue") or "Issue sin descripción",
            "priority": priority_map.get(prop(p, "Prioridad", "select"), "media"),
            "fecha":    fecha_str,
            "status":   status_map.get(prop(p, "Status", "select"), "abierto")
        })
    return issues


# ── FETCH FLOTA ────────────────────────────────────────────────────────────────
def fetch_flota_summary():
    pages = notion_query(DB_FLOTA)
    trucks   = [p for p in pages if prop(p, "Tipo", "select") == "Truck"]
    trailers = [p for p in pages if prop(p, "Tipo", "select") == "Trailer"]
    activos  = [p for p in pages if prop(p, "Status", "select") in ("Activo", "Rentado")]
    taller   = [p for p in pages if prop(p, "Status", "select") == "En Taller"]
    items = []
    for p in pages:
        st = prop(p, "Status", "select") or "Disponible"
        color = {"Activo":"verde", "Rentado":"verde", "En Taller":"rojo",
                 "Disponible":"amarillo", "Inactivo":"gris"}.get(st, "gris")
        items.append(f"{prop(p,'Unidad')} ({st})")
    return {
        "trucks": len(trucks),
        "trailers": len(trailers),
        "activos": len(activos),
        "taller": len(taller),
        "items": items
    }


# ── FETCH OOs ──────────────────────────────────────────────────────────────────
def fetch_oos_count():
    pages = notion_query(DB_OOS)
    return len(pages)


# ── INJECT INTO HTML ───────────────────────────────────────────────────────────
def inject_rocks(html, rocks):
    js = "const EOS_ROCKS = " + json.dumps(rocks, ensure_ascii=False, indent=2) + ";"
    return re.sub(
        r"const EOS_ROCKS\s*=\s*\[.*?\];",
        js,
        html,
        flags=re.DOTALL
    )


def inject_issues(html, issues):
    js = "const EOS_ISSUES = " + json.dumps(issues, ensure_ascii=False, indent=2) + ";"
    return re.sub(
        r"const EOS_ISSUES\s*=\s*\[.*?\];",
        js,
        html,
        flags=re.DOTALL
    )


def inject_sync_date(html):
    today = datetime.now().strftime("%Y-%m-%d")
    return re.sub(
        r"(lastSync:\s*')[^']*(')",
        rf"\g<1>{today}\g<2>",
        html
    )


# ── MAIN ───────────────────────────────────────────────────────────────────────
def main():
    if NOTION_TOKEN == "PEGA_TU_TOKEN_AQUI":
        print("❌ Falta el Notion Token.")
        print("   1. Ve a https://www.notion.so/my-integrations")
        print("   2. Crea una integración → copia el token")
        print("   3. Comparte las 4 bases de datos con tu integración")
        print("   4. Pega el token en update.py o exporta: export NOTION_TOKEN=secret_xxx")
        sys.exit(1)

    print("🔄 Conectando con Notion...")

    print("   📊 Rocks Q2 2026...")
    rocks = fetch_rocks()
    print(f"      → {len(rocks)} rocks encontrados")

    print("   🔥 Issues abiertos...")
    issues = fetch_issues()
    print(f"      → {len(issues)} issues activos")

    print("   🚛 Flota...")
    flota = fetch_flota_summary()
    print(f"      → {flota['trucks']} trucks, {flota['trailers']} trailers, {flota['activos']} activos")

    print(f"\n📝 Actualizando {HTML_FILE}...")
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    html = inject_rocks(html, rocks)
    html = inject_issues(html, issues)
    html = inject_sync_date(html)

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print("✅ HTML actualizado")

    print("\n🚀 Publicando en GitHub Pages...")
    today = datetime.now().strftime("%Y-%m-%d")
    cmds = [
        ["git", "add", "index.html"],
        ["git", "commit", "-m", f"sync: Notion → dashboard {today}"],
        ["git", "push"]
    ]
    for cmd in cmds:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0 and "nothing to commit" not in result.stdout:
            print(f"⚠️  {' '.join(cmd)}: {result.stderr.strip()}")
        else:
            print(f"   ✓ {' '.join(cmd)}")

    print(f"""
✅ Dashboard actualizado.
   🔗 https://jesusth08-create.github.io/jesus-command-center/
   (disponible en ~60 segundos)

📋 Resumen:
   • {len(rocks)} Rocks Q2 2026
   • {len(issues)} Issues activos
   • {flota['trucks']} trucks | {flota['trailers']} trailers | {flota['activos']} en operación
""")


if __name__ == "__main__":
    main()
