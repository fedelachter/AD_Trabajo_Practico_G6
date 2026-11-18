"""
exportar_csv.py — Exportación de las salidas del análisis a CSV (para el dashboard)
===================================================================================
La notebook 04 es el pipeline (carga, limpieza, modelo, clustering, score). Este
módulo NO recalcula nada: recibe los DataFrames que la notebook ya construyó y los
vuelca a 4 CSV con columnas limpias. Es la única capa de "salida" del sistema.

Los 4 productos:
  1. oportunidades.csv    -> ranking de propiedades individuales   (objeto: ranking)
  2. score_barrios.csv    -> score de atractivo por barrio          (objeto: score_df)
  3. perfiles_barrios.csv -> segmentación / clusters por barrio      (objeto: perfil_clusters)
  4. estrategia.csv       -> renta vs reventa por propiedad          (objeto: rev)

Uso típico (al final de la notebook):
    from exportar_csv import exportar_todo
    exportar_todo(ranking, score_df, perfil_clusters, rev, carpeta=RAIZ / "outputs")
"""

from pathlib import Path
import pandas as pd

# utf-8-sig = se abre bien en Excel con acentos (Constitución, Núñez, etc.)
ENCODING = "utf-8-sig"


def _guardar(df: pd.DataFrame, carpeta: Path, nombre: str) -> Path:
    """Guarda un DataFrame como CSV y devuelve la ruta. Crea la carpeta si no existe."""
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / nombre
    df.to_csv(ruta, index=False, encoding=ENCODING)
    print(f"  ✓ {nombre:24s} ({len(df):>6,} filas, {df.shape[1]} columnas)")
    return ruta


# ---------------------------------------------------------------------------
# 1. OPORTUNIDADES (ranking de propiedades individuales)
# ---------------------------------------------------------------------------
def exportar_oportunidades(ranking: pd.DataFrame, carpeta) -> Path:
    cols = ["direccion", "barrio", "ambientes", "m2_cubiertos", "precio_usd",
            "precio_m2", "precio_m2_esperado", "residuo_pct",
            "score_barrio", "score_propiedad", "alerta_verificar",
            "titulo", "link"]            # titulo/link se incluyen si existen
    cols = [c for c in cols if c in ranking.columns]
    out = ranking[cols].copy()
    out = out.rename(columns={"residuo_pct": "subvaluacion_pct"})
    # Redondeo prolijo para el dashboard
    for c in ["m2_cubiertos", "precio_m2", "precio_m2_esperado", "subvaluacion_pct",
              "score_barrio", "score_propiedad"]:
        if c in out.columns:
            out[c] = out[c].round(1)
    return _guardar(out, carpeta, "oportunidades.csv")


# ---------------------------------------------------------------------------
# 2. SCORE POR BARRIO (atractivo de inversión integrado)
# ---------------------------------------------------------------------------
def exportar_score_barrios(score_df: pd.DataFrame, perfil_clusters: pd.DataFrame,
                           carpeta) -> Path:
    out = score_df.copy()
    # Sumar el cluster de cada barrio (para filtrar/pintar por perfil en el dashboard)
    if perfil_clusters is not None and "cluster" in perfil_clusters.columns:
        out = out.join(perfil_clusters["cluster"], how="left")
    out = out.reset_index().rename(columns={"index": "barrio"})
    if "barrio" not in out.columns:                 # por si el índice tenía otro nombre
        out = out.rename(columns={out.columns[0]: "barrio"})
    out = out.sort_values("score", ascending=False)
    num = ["rent_neta_%", "indice_contexto", "densidad_oportunidad",
           "z_rentabilidad", "z_oportunidad", "z_contexto", "score"]
    for c in num:
        if c in out.columns:
            out[c] = out[c].round(3)
    if "cluster" in out.columns:
        out["cluster"] = out["cluster"].astype("Int64")   # entero con NaN permitido
    return _guardar(out, carpeta, "score_barrios.csv")


# ---------------------------------------------------------------------------
# 3. PERFILES DE BARRIO (segmentación / clusters)
# ---------------------------------------------------------------------------
def exportar_perfiles(perfil_clusters: pd.DataFrame, carpeta) -> Path:
    out = perfil_clusters.reset_index().rename(columns={"index": "barrio"})
    if "barrio" not in out.columns:
        out = out.rename(columns={out.columns[0]: "barrio"})
    # Orden de columnas: barrio, cluster, y después las variables de perfil
    primeras = [c for c in ["barrio", "cluster"] if c in out.columns]
    resto = [c for c in out.columns if c not in primeras]
    out = out[primeras + resto]
    if "cluster" in out.columns:
        out["cluster"] = out["cluster"].astype("Int64")
    # Redondeo de las variables numéricas de perfil
    for c in resto:
        if pd.api.types.is_float_dtype(out[c]):
            out[c] = out[c].round(2)
    return _guardar(out, carpeta, "perfiles_barrios.csv")


# ---------------------------------------------------------------------------
# 4. ESTRATEGIA renta vs reventa (por propiedad)
# ---------------------------------------------------------------------------
def exportar_estrategia(rev: pd.DataFrame, carpeta) -> Path:
    out = rev.copy()
    # Años que la renta necesita para igualar la reventa (solo donde la reventa es viable)
    if {"retorno_reventa", "retorno_renta_anual"}.issubset(out.columns):
        out["anios_para_igualar"] = (out["retorno_reventa"] / out["retorno_renta_anual"]).where(
            out.get("reventa_viable", False))
    cols = ["direccion", "barrio", "ambientes", "m2_cubiertos", "precio_usd",
            "precio_m2", "precio_m2_esperado", "residuo_pct",
            "retorno_reventa", "retorno_renta_anual", "reventa_viable",
            "anios_para_igualar", "estrategia"]
    cols = [c for c in cols if c in out.columns]
    out = out[cols].rename(columns={"residuo_pct": "subvaluacion_pct"})
    # Retornos a porcentaje legible (venían en proporción 0–1)
    for c in ["retorno_reventa", "retorno_renta_anual"]:
        if c in out.columns:
            out[c] = (out[c] * 100).round(1)
    for c in ["subvaluacion_pct", "precio_m2", "precio_m2_esperado", "anios_para_igualar"]:
        if c in out.columns:
            out[c] = out[c].round(1)
    return _guardar(out, carpeta, "estrategia.csv")


# ---------------------------------------------------------------------------
# ORQUESTADOR
# ---------------------------------------------------------------------------
def exportar_todo(ranking, score_df, perfil_clusters, rev, carpeta="outputs"):
    """Genera los 4 CSV en `carpeta`. Devuelve un dict {nombre: ruta}."""
    print(f"Exportando CSV a: {Path(carpeta).resolve()}")
    rutas = {
        "oportunidades":    exportar_oportunidades(ranking, carpeta),
        "score_barrios":    exportar_score_barrios(score_df, perfil_clusters, carpeta),
        "perfiles_barrios": exportar_perfiles(perfil_clusters, carpeta),
        "estrategia":       exportar_estrategia(rev, carpeta),
    }
    print("Listo: 4 CSV generados.")
    return rutas
