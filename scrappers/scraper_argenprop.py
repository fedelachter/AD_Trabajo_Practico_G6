import re
import csv
import time
import random
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
 
BASE_URL = "https://www.argenprop.com/departamentos/alquiler/capital-federal"
OUTPUT_CSV = Path("argenprop_departamentos_caba.csv")
PROGRESS_FILE = Path("scrape_progress.txt")
 
FIELDNAMES = [
    "titulo", "direccion", "barrio", "ciudad", "moneda", "precio",
    "expensas", "m2_cubiertos", "dormitorios", "banos", "ambientes",
    "antiguedad", "link", "pagina",
]
 
 
def parse_card(card):
    def text_or_none(selector):
        el = card.select_one(selector)
        return el.get_text(" ", strip=True) if el else None
 
    price_raw = text_or_none(".card__price")
    address = text_or_none(".card__address")
    barrio_line = text_or_none(".card__title--primary")
    features_raw = text_or_none(".card__main-features") or ""
    headline = text_or_none(".card__title")
    link_el = card.find("a", href=True)
    link = "https://www.argenprop.com" + link_el["href"] if link_el else None
 
    return {
        "price_raw": price_raw,
        "address": address,
        "barrio_line": barrio_line,
        "features_raw": features_raw,
        "headline": headline,
        "link": link,
    }
 
 
def parse_price(price_raw):
    if not price_raw:
        return None, None, None
    currency = "USD" if "USD" in price_raw else ("Consultar" if "Consultar" in price_raw else "ARS")
    values = []
    for ars, usd in re.findall(r"\$\s*([\d\.]+)|USD\s*([\d\.]+)", price_raw):
        v = ars or usd
        if v:
            values.append(int(v.replace(".", "")))
    price_val = values[0] if len(values) >= 1 else None
    expenses_val = values[1] if len(values) >= 2 else None
    return currency, price_val, expenses_val
 
 
def parse_barrio(barrio_line):
    if not barrio_line:
        return None, None
    m = re.match(r"Departamento en Alquiler en (.+?),\s*(.+)$", barrio_line)
    return (m.group(1).strip(), m.group(2).strip()) if m else (None, None)
 
 
def parse_features(features_raw):
    m2 = dorm = banos = ambientes = antiguedad = None
    text = features_raw
    m2_match = re.search(r"([\d.,]+)\s*m²\s*cubie", text)
    if m2_match:
        m2 = float(m2_match.group(1).replace(",", "."))
    dorm_match = re.search(r"(\d+)\s*dorm", text)
    if dorm_match:
        dorm = int(dorm_match.group(1))
    banos_match = re.search(r"(\d+)\s*baño", text)
    if banos_match:
        banos = int(banos_match.group(1))
    amb_match = re.search(r"(\d+)\s*ambiente", text)
    if amb_match:
        ambientes = int(amb_match.group(1))
    elif "Monoam" in text:
        ambientes = 1
    ant_match = re.search(r"(\d+)\s*años|A Estrenar", text)
    if ant_match:
        antiguedad = ant_match.group(0)
    return m2, dorm, banos, ambientes, antiguedad
 
 
def cards_to_rows(cards, page_num):
    rows = []
    for card in cards:
        raw = parse_card(card)
        currency, price, expenses = parse_price(raw["price_raw"])
        barrio, ciudad = parse_barrio(raw["barrio_line"])
        m2, dorm, banos, ambientes, antiguedad = parse_features(raw["features_raw"])
        rows.append({
            "titulo": raw["headline"],
            "direccion": raw["address"],
            "barrio": barrio,
            "ciudad": ciudad,
            "moneda": currency,
            "precio": price,
            "expensas": expenses,
            "m2_cubiertos": m2,
            "dormitorios": dorm,
            "banos": banos,
            "ambientes": ambientes,
            "antiguedad": antiguedad,
            "link": raw["link"],
            "pagina": page_num,
        })
    return rows
 
 
def append_rows_to_csv(rows):
    file_exists = OUTPUT_CSV.exists()
    with open(OUTPUT_CSV, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)
 
 
def get_start_page():
    if PROGRESS_FILE.exists():
        return int(PROGRESS_FILE.read_text().strip()) + 1
    return 1
 
 
def save_progress(page_num):
    PROGRESS_FILE.write_text(str(page_num))
 
 
def scrape(n_pages=50, delay_range=(5.0, 9.0), short_backoff_seconds=(20, 40),
           max_consecutive_blocks=3, long_wait_minutes=15, max_run_hours=9,
           resume=True, headless=True):
    """
    Backoff de dos niveles, pensado para correr desatendido toda la noche:
      - Bloqueo individual: espera corta (short_backoff_seconds) y
        reintenta la misma página.
      - Tras `max_consecutive_blocks` bloqueos seguidos: espera LARGA
        automática (`long_wait_minutes`) y vuelve a intentar, sin
        detener el script. Esto se repite indefinidamente mientras el
        tiempo total corrido no supere `max_run_hours` (por defecto 9
        horas) - así podés dejarlo corriendo mientras dormís sin que se
        quede pegado en el primer bloqueo, pero tampoco corra para
        siempre si el sitio te bloquea el resto del día.
    """
    start_page = get_start_page() if resume else 1
    if start_page > 1:
        print(f"Reanudando desde la página {start_page} (según {PROGRESS_FILE})")
 
    run_start = time.time()
    max_run_seconds = max_run_hours * 3600
    total_this_run = 0
    consecutive_blocks = 0
    long_waits_done = 0
 
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="es-AR",
        )
        page_obj = context.new_page()
 
        page = start_page
        while page <= n_pages:
            url = BASE_URL if page == 1 else f"{BASE_URL}?pagina-{page}"
            try:
                resp = page_obj.goto(url, timeout=30000, wait_until="domcontentloaded")
                try:
                    page_obj.wait_for_selector(".card", timeout=8000)
                except Exception:
                    pass
                html = page_obj.content()
                status = resp.status if resp else None
            except Exception as e:
                print(f"[debug] página {page}: error de navegación ({e})")
                status, html = None, ""
 
            soup = BeautifulSoup(html, "html.parser")
            cards = soup.select(".card")
            blocked = (status is not None and status >= 400) or len(cards) == 0
 
            if blocked:
                consecutive_blocks += 1
                print(f"[debug] página {page}: status={status} avisos=0 -> posible bloqueo "
                      f"(intento {consecutive_blocks}/{max_consecutive_blocks})")
 
                if consecutive_blocks >= max_consecutive_blocks:
                    elapsed_hours = (time.time() - run_start) / 3600
                    if elapsed_hours >= max_run_hours:
                        print(f"Ya pasaron {elapsed_hours:.1f}h corriendo (límite {max_run_hours}h). "
                              f"Corto acá y guardo el progreso. Sigue desde la página {page} "
                              f"la próxima corrida.")
                        break
                    long_waits_done += 1
                    print(f"  {max_consecutive_blocks} bloqueos seguidos. Pausa larga "
                          f"automática de {long_wait_minutes} min (espera #{long_waits_done}, "
                          f"llevo {elapsed_hours:.1f}h de las {max_run_hours}h máx) antes de "
                          f"reintentar la página {page}...")
                    time.sleep(long_wait_minutes * 60)
                    consecutive_blocks = 0
                    # sesión/contexto nuevo tras la espera larga
                    context.close()
                    context = browser.new_context(
                        user_agent=(
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                        ),
                        locale="es-AR",
                    )
                    page_obj = context.new_page()
                    continue
 
                time.sleep(random.uniform(*short_backoff_seconds))
                continue  # reintenta la misma página
 
            consecutive_blocks = 0
            rows = cards_to_rows(cards, page)
            append_rows_to_csv(rows)
            save_progress(page)
            total_this_run += len(rows)
            print(f"Página {page}: {len(rows)} avisos guardados (acumulado esta corrida: {total_this_run})")
 
            page += 1
            time.sleep(random.uniform(*delay_range))
 
        browser.close()
 
    print(f"\nTotal agregado en esta corrida: {total_this_run}")
    if OUTPUT_CSV.exists():
        df = pd.read_csv(OUTPUT_CSV)
        print(f"Total acumulado en {OUTPUT_CSV}: {len(df)} avisos")
        return df
    return pd.DataFrame()
 
 
if __name__ == "__main__":
    df = scrape(n_pages=50, headless=True, max_run_hours=9)
    print(df.dtypes)