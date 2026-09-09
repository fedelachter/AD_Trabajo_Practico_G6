"""
Scraper de MercadoLibre Inmuebles - Alquiler Residencial en CABA
====================================================================
TP Analítica Descriptiva - 1ra Pre-Entrega
Temática: Inteligencia de Mercado Inmobiliario (Real Estate Analytics)

Qué hace:
  Recorre el mercado de alquiler residencial en CABA en MercadoLibre
  Inmuebles, cubriendo tres tipologías de propiedad: Departamentos, PH
  y Casas. Extrae por cada aviso: precio, moneda, dirección, barrio,
  m2 cubiertos, dormitorios, baños, ambientes y tipo de propiedad.

Por qué MercadoLibre:
  - Volumen adecuado: ~10.800 departamentos + ~700 PH/Casas en alquiler
    en CABA.
  - Sin protección anti-bot agresiva detectada (a diferencia de otros
    portales del mercado, que bloquean la paginación profunda incluso
    para buscadores como Google).

Estrategia de segmentación:
  El buscador de MercadoLibre corta cualquier vista en ~1000 resultados
  (límite de UX, no de seguridad). Como Departamentos tiene ~10.800
  avisos en CABA, se segmenta por barrio (48 barrios oficiales) para
  que cada vista quede cómodamente por debajo de ese límite. PH y Casas
  (443 y 268 respectivamente) entran en una sola vista sin necesidad de
  segmentar.

  Se decidió mantener el dataset acotado a alquiler (sin mezclar con
  venta) para que el análisis tenga una narrativa de negocio coherente:
  "mercado de alquiler residencial en CABA".

Requisitos: pip install requests beautifulsoup4 pandas --break-system-packages
"""
import re
import csv
import time
import random
import requests
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup

BASE_URL = "https://inmuebles.mercadolibre.com.ar"
OUTPUT_CSV = Path("mercadolibre_alquiler_caba.csv")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
}

# Los 48 barrios oficiales de la Ciudad de Buenos Aires
BARRIOS = [
    "palermo", "recoleta", "belgrano", "caballito", "puerto-madero",
    "villa-urquiza", "almagro", "nunez", "villa-crespo", "villa-devoto",
    "flores", "villa-del-parque", "balvanera", "colegiales", "retiro",
    "san-nicolas", "san-telmo", "monserrat", "floresta", "chacarita",
    "agronomia", "barracas", "boedo", "coghlan", "constitucion",
    "la-boca", "la-paternal", "liniers", "mataderos", "monte-castro",
    "nueva-pompeya", "parque-avellaneda", "parque-chacabuco",
    "parque-chas", "parque-patricios", "saavedra", "san-cristobal",
    "velez-sarsfield", "versalles", "villa-general-mitre",
    "villa-lugano", "villa-luro", "villa-ortuzar", "villa-pueyrredon",
    "villa-real", "villa-riachuelo", "villa-santa-rita", "villa-soldati",
]

# PH y Casas caben en una sola vista (no superan el límite de ~1000),
# así que no necesitan segmentarse por barrio.
CATEGORIAS_SIN_SEGMENTAR = {
    "ph": f"{BASE_URL}/ph/alquiler/capital-federal/",
    "casa": f"{BASE_URL}/casas/alquiler/capital-federal/",
}

ITEMS_POR_PAGINA = 48
MAX_PAGINAS = 22
TIEMPO_LENTO_SEGUNDOS = 8  # umbral para marcar una página como "lenta" en el log

FIELDNAMES = [
    "id_aviso", "titulo", "direccion", "barrio", "ciudad", "moneda", "precio",
    "m2_cubiertos", "dormitorios", "banos", "ambientes", "tipo_propiedad", "link",
]


def parse_id_aviso(link):
    if not link:
        return None
    m = re.search(r"(MLA-?\d+)", link, re.IGNORECASE)
    return m.group(1).upper().replace("-", "") if m else None


def parse_price(price_raw):
    if not price_raw:
        return None, None
    currency = "USD" if "US$" in price_raw or "USD" in price_raw else "ARS"
    m = re.search(r"([\d.]+)", price_raw.replace("US$", "").replace("$", ""))
    precio = int(m.group(1).replace(".", "")) if m else None
    return currency, precio


def parse_location(location_raw):
    if not location_raw:
        return None, None
    parts = [p.strip() for p in location_raw.split(",")]
    if len(parts) >= 2:
        return parts[-2], parts[-1]
    return None, None


def parse_attrs(attrs_raw):
    m2 = dorm = banos = ambientes = None
    if not attrs_raw:
        return m2, dorm, banos, ambientes
    text = attrs_raw.lower()
    amb_match = re.search(r"(\d+)\s*amb", text)
    if amb_match:
        ambientes = int(amb_match.group(1))
    elif "monoambiente" in text:
        ambientes = 1
    dorm_match = re.search(r"(\d+)\s*dorm", text)
    if dorm_match:
        dorm = int(dorm_match.group(1))
    banos_match = re.search(r"(\d+)\s*baño", text)
    if banos_match:
        banos = int(banos_match.group(1))
    m2_match = re.search(r"([\d.,]+)\s*m²", text)
    if m2_match:
        m2 = float(m2_match.group(1).replace(",", "."))
    return m2, dorm, banos, ambientes


def item_to_row(item, tipo_propiedad):
    def txt(sel):
        el = item.select_one(sel)
        return el.get_text(" ", strip=True) if el else None

    titulo = txt(".poly-component__title")
    price_raw = txt(".poly-component__price")
    location_raw = txt(".poly-component__location")
    attrs_raw = txt(".poly-component__attributes-list")
    link_el = item.select_one("a.poly-component__title") or item.find("a", href=True)
    link = link_el["href"] if link_el and link_el.has_attr("href") else None

    currency, precio = parse_price(price_raw)
    barrio, ciudad = parse_location(location_raw)
    m2, dorm, banos, ambientes = parse_attrs(attrs_raw)

    return {
        "id_aviso": parse_id_aviso(link), "titulo": titulo, "direccion": location_raw,
        "barrio": barrio, "ciudad": ciudad, "moneda": currency, "precio": precio,
        "m2_cubiertos": m2, "dormitorios": dorm, "banos": banos, "ambientes": ambientes,
        "tipo_propiedad": tipo_propiedad, "link": link,
    }


def append_rows(rows, seen_ids):
    """Guarda filas nuevas, evitando duplicados por id_aviso (puede
    haber solapamiento entre páginas si un aviso cambia de posición
    mientras se recorre el listado)."""
    nuevas = []
    for r in rows:
        aid = r.get("id_aviso")
        if aid and aid in seen_ids:
            continue
        if aid:
            seen_ids.add(aid)
        nuevas.append(r)
    if not nuevas:
        return 0
    existe = OUTPUT_CSV.exists()
    with open(OUTPUT_CSV, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not existe:
            w.writeheader()
        w.writerows(nuevas)
    return len(nuevas)


def get(session, url):
    for intento in range(3):
        try:
            resp = session.get(url, timeout=15)
            return resp.status_code, resp.text
        except Exception as e:
            print(f"    error de red ({e}), reintento {intento + 1}/3")
            time.sleep(5)
    return None, ""


def scrape_segmento(session, base_url, tipo_propiedad, seen_ids, nombre):
    guardados = 0
    for pagina in range(MAX_PAGINAS):
        offset = pagina * ITEMS_POR_PAGINA + 1
        url = base_url if pagina == 0 else f"{base_url}_Desde_{offset}_NoIndex_True"

        t0 = time.time()
        status, html = get(session, url)
        soup = BeautifulSoup(html, "html.parser") if html else None
        items = soup.select(".ui-search-result, li.ui-search-layout__item") if soup else []
        tiempo = time.time() - t0

        alerta = " <- LENTO, posible saturación" if tiempo > TIEMPO_LENTO_SEGUNDOS else ""
        print(f"    [{nombre}] página {pagina + 1}: status={status} avisos={len(items)} "
              f"({tiempo:.1f}s){alerta}")

        if pagina == 0 and not items:
            print(f"    página 1 sin avisos -> reintento en 10s")
            time.sleep(10)
            status, html = get(session, url)
            soup = BeautifulSoup(html, "html.parser") if html else None
            items = soup.select(".ui-search-result, li.ui-search-layout__item") if soup else []
            if not items:
                print(f"    sigue vacío, salteo este segmento")
                break

        if not items:
            break  # fin natural del segmento

        guardados += append_rows([item_to_row(it, tipo_propiedad) for it in items], seen_ids)
        time.sleep(random.uniform(2.0, 3.0))

    return guardados


def scrape():
    session = requests.Session()
    session.headers.update(HEADERS)
    seen_ids = set()

    total = 0
    inicio = time.time()

    print("=== Departamentos (segmentado por barrio) ===\n")
    for i, barrio in enumerate(BARRIOS, 1):
        url = f"{BASE_URL}/departamentos/alquiler/capital-federal/{barrio}/"
        n = scrape_segmento(session, url, "departamento", seen_ids, barrio)
        total += n
        elapsed_min = (time.time() - inicio) / 60
        ritmo = total / elapsed_min if elapsed_min > 0.01 else 0
        print(f"[{i}/{len(BARRIOS)}] {barrio} -> {n} nuevos "
              f"(acumulado: {total}, {elapsed_min:.1f} min, ~{ritmo:.0f} avisos/min)\n")

    print("=== PH y Casas (categoría completa) ===\n")
    for tipo, url in CATEGORIAS_SIN_SEGMENTAR.items():
        n = scrape_segmento(session, url, tipo, seen_ids, tipo)
        total += n
        elapsed_min = (time.time() - inicio) / 60
        print(f"[{tipo}] -> {n} nuevos (acumulado: {total}, {elapsed_min:.1f} min)\n")

    print(f"Total de avisos recolectados: {total}")
    print(f"Tiempo total: {(time.time() - inicio) / 60:.1f} minutos")

    df = pd.read_csv(OUTPUT_CSV)
    print(f"\nPor tipo de propiedad:")
    print(df["tipo_propiedad"].value_counts().to_string())
    print(f"\nPor barrio (top 10):")
    print(df["barrio"].value_counts().head(10).to_string())
    print(f"\nNulos por columna:")
    print(df.isna().sum().to_string())

    return df


if __name__ == "__main__":
    df = scrape()
    print(f"\n{df.dtypes}")