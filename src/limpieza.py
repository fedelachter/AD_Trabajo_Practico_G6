"""
Funciones reutilizables de calidad y limpieza - PreEntrega 2 (Grupo 6).

Repositorio: https://github.com/fedelachter/AD_Trabajo_Practico_G6

Las mismas funciones sirven para venta y alquiler: lo que cambia entre
fuentes (archivo, operación, columnas esperadas) entra como parámetro.
Cada paso de limpieza puede registrar lo que hizo en una lista `log`,
para poder documentar qué registros se eliminaron, corrigieron o imputaron.
"""
import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

REPO_URL = "https://github.com/fedelachter/AD_Trabajo_Practico_G6"
REPO_RAW = "https://raw.githubusercontent.com/fedelachter/AD_Trabajo_Practico_G6/main/data/raw"

COLUMNAS_BASE = ["id_aviso", "titulo", "direccion", "barrio", "ciudad", "moneda", "precio",
                 "m2_cubiertos", "dormitorios", "banos", "ambientes", "tipo_propiedad", "link"]
COLUMNAS_CANONICAS = COLUMNAS_BASE + ["operacion", "es_emprendimiento", "fuente"]

# Los 48 barrios oficiales de la Ciudad de Buenos Aires
BARRIOS_OFICIALES = [
    "Agronomía", "Almagro", "Balvanera", "Barracas", "Belgrano", "Boedo", "Caballito",
    "Chacarita", "Coghlan", "Colegiales", "Constitución", "Flores", "Floresta", "La Boca",
    "La Paternal", "Liniers", "Mataderos", "Monte Castro", "Monserrat", "Nueva Pompeya",
    "Núñez", "Palermo", "Parque Avellaneda", "Parque Chacabuco", "Parque Chas",
    "Parque Patricios", "Puerto Madero", "Recoleta", "Retiro", "Saavedra", "San Cristóbal",
    "San Nicolás", "San Telmo", "Vélez Sarsfield", "Versalles", "Villa Crespo",
    "Villa del Parque", "Villa Devoto", "Villa General Mitre", "Villa Lugano", "Villa Luro",
    "Villa Ortúzar", "Villa Pueyrredón", "Villa Real", "Villa Riachuelo",
    "Villa Santa Rita", "Villa Soldati", "Villa Urquiza",
]

# Nombres con los que MercadoLibre escribe algunos barrios o sub-barrios, y el barrio oficial
# al que pertenecen sin ambigüedad.
ALIAS_BARRIO = {
    "paternal": "La Paternal", "boca": "La Boca", "villa gral. mitre": "Villa General Mitre",
    "santa rita": "Villa Santa Rita",
    "belgrano r": "Belgrano", "belgrano c": "Belgrano", "belgrano chico": "Belgrano",
    "belgrano barrancas": "Belgrano",
    "palermo soho": "Palermo", "palermo hollywood": "Palermo", "palermo chico": "Palermo",
    "palermo viejo": "Palermo", "las canitas": "Palermo", "botanico": "Palermo",
    "once": "Balvanera",
}
# Zonas conocidas que NO coinciden con un único barrio oficial: no se asignan.
BARRIOS_AMBIGUOS = {"barrio norte", "congreso", "parque centenario"}

CLAVE_DUPLICADO = ["operacion", "direccion", "precio", "moneda", "m2_cubiertos", "ambientes"]
BINS_M2 = [0, 30, 45, 60, 90, 150, np.inf]


# --------------------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------------------
def normalizar_texto(valor):
    """Minúsculas, sin tildes y sin espacios repetidos (para comparar nombres)."""
    s = unicodedata.normalize("NFKD", str(valor)).encode("ascii", "ignore").decode().lower().strip()
    return re.sub(r"\s+", " ", s)


_MAPA_BARRIOS = {normalizar_texto(b): b for b in BARRIOS_OFICIALES}
_MAPA_BARRIOS.update(ALIAS_BARRIO)


def registrar(log, regla, columna, afectados, accion):
    """Agrega una línea al registro de cambios (si se pasó una lista)."""
    if log is not None:
        log.append({"regla": regla, "columna": columna, "afectados": int(afectados), "accion": accion})


# --------------------------------------------------------------------------------------
# Ingesta
# --------------------------------------------------------------------------------------
def leer_raw(archivo, raw_dir):
    """
    Lee un CSV de /data/raw. Busca primero en `raw_dir` (ruta relativa al repositorio) y, si no
    está, lo baja del repositorio de GitHub del proyecto. Devuelve (dataframe, origen usado).
    """
    ruta = Path(raw_dir) / archivo
    origen = str(ruta) if ruta.exists() else f"{REPO_RAW}/{archivo}"
    return pd.read_csv(origen, encoding="utf-8-sig"), origen


def cargar_fuente(archivo, operacion, raw_dir, columnas_esperadas=COLUMNAS_BASE):
    """
    Carga un CSV crudo de venta o alquiler con la misma lógica para cualquier fuente.

    Valida las columnas esperadas, agrega `operacion` y `es_emprendimiento` si la fuente
    no las trae, y devuelve (dataframe, origen usado).
    """
    df, origen = leer_raw(archivo, raw_dir)
    faltan = [c for c in columnas_esperadas if c not in df.columns]
    if faltan:
        raise ValueError(f"{archivo}: faltan las columnas esperadas {faltan}")
    if "operacion" not in df.columns:
        df["operacion"] = operacion
    if "es_emprendimiento" not in df.columns:
        df["es_emprendimiento"] = 0  # la fuente de alquiler no distingue emprendimientos
    df["fuente"] = archivo
    return df[COLUMNAS_CANONICAS].copy(), origen


def resumen_calidad(df):
    """Tipo, cantidad de valores únicos y nulos de cada columna."""
    return pd.DataFrame({
        "tipo": df.dtypes.astype(str),
        "n_unicos": df.nunique(),
        "nulos": df.isna().sum(),
        "pct_nulos": (df.isna().mean() * 100).round(1),
    })


# --------------------------------------------------------------------------------------
# Normalización y alcance
# --------------------------------------------------------------------------------------
def resolver_barrio(df, log=None):
    """
    Lleva el campo `barrio` a los 48 barrios oficiales.
    Agrega `barrio_original` (como se scrapeó) y `barrio_via` (cómo se resolvió):
    directo | desde_direccion | ambiguo | no_resuelto.
    """
    out = df.copy()
    out["barrio_original"] = out["barrio"]
    nombre = out["barrio"].map(normalizar_texto)
    oficial = nombre.map(_MAPA_BARRIOS)
    ambiguo = nombre.isin(BARRIOS_AMBIGUOS)

    via = pd.Series("no_resuelto", index=out.index)
    via[oficial.notna()] = "directo"
    via[ambiguo] = "ambiguo"

    # Si el barrio quedó cargado con una calle, se lo busca en la dirección completa.
    pendiente = oficial.isna() & ~ambiguo

    def desde_direccion(direccion):
        for parte in reversed([normalizar_texto(p) for p in str(direccion).split(",")]):
            if parte in _MAPA_BARRIOS:
                return _MAPA_BARRIOS[parte]
        return None

    rec = out.loc[pendiente, "direccion"].map(desde_direccion)
    oficial.loc[rec.index] = rec
    via.loc[rec[rec.notna()].index] = "desde_direccion"

    out["barrio"] = oficial
    out["barrio_via"] = via
    registrar(log, "Barrio a los 48 oficiales", "barrio",
              (out["barrio"].fillna("") != out["barrio_original"].fillna("")).sum(),
              "normalizado (alias y sub-barrios) o recuperado desde la dirección")
    return out


def marcar_fuera_de_alcance(df, log=None):
    """Marca avisos fuera de CABA: sin barrio oficial y con ciudad distinta de 'Capital Federal'."""
    out = df.copy()
    out["fuera_de_alcance"] = out["barrio"].isna() & (out["ciudad"] != "Capital Federal")
    registrar(log, "Fuera de CABA", "ciudad/barrio", out["fuera_de_alcance"].sum(), "eliminado (fuera del alcance)")
    return out


PATRON_NO_RESIDENCIAL = (r"\b(?:oficinas?|hotel|hostel|galp[oó]n|consultorio|terreno|"
                         r"fondo de comercio|local comercial|edificio completo)\b")


def marcar_no_residencial(df, log=None):
    """
    Marca (sin eliminar) avisos cuyo título menciona una tipología no residencial.
    Regla conservadora: no incluye 'cochera' ni 'baulera' porque en un departamento aparecen
    como comodidad ("con cochera"), ni 'lote' o 'local' sueltos, que son ambiguos.
    """
    out = df.copy()
    out["posible_no_residencial"] = out["titulo"].str.lower().str.contains(
        PATRON_NO_RESIDENCIAL, regex=True, na=False)
    registrar(log, "Posible tipología no residencial", "titulo", out["posible_no_residencial"].sum(),
              "marcado (se conserva; decidir en el EDA)")
    return out


def limpiar_link(df):
    """Quita los parámetros de tracking del link (todo lo que sigue al '#')."""
    out = df.copy()
    out["link"] = out["link"].astype(str).str.split("#").str[0]
    return out


# --------------------------------------------------------------------------------------
# Duplicados
# --------------------------------------------------------------------------------------
def marcar_duplicados(df, log=None):
    """
    Dos marcas, de menor a mayor confianza:
      dup_posible    -> mismo operación, dirección, precio, moneda, m² y ambientes (distinto ID).
      dup_eliminable -> además mismo título y NO es emprendimiento. En un emprendimiento, las
                        unidades idénticas del mismo edificio no son duplicados reales.
    Se conserva siempre la primera aparición.
    """
    out = df.copy()
    out["dup_posible"] = out.duplicated(subset=CLAVE_DUPLICADO, keep="first")
    con_titulo = out.duplicated(subset=CLAVE_DUPLICADO + ["titulo"], keep="first")
    out["dup_eliminable"] = con_titulo & (out["es_emprendimiento"] == 0)
    registrar(log, "Duplicado por contenido", "(varias)", out["dup_eliminable"].sum(),
              "eliminado (alquiler y usados, mismo título)")
    return out


# --------------------------------------------------------------------------------------
# Valores imposibles y atípicos
# --------------------------------------------------------------------------------------
def corregir_valores_imposibles(df, log=None):
    """
    Pasa a NaN los valores físicamente imposibles y deja una marca por cada variable.
    Se evalúa primero m², y recién después ambientes y baños con el m² ya corregido
    (si el m² es el dato roto, no se culpa a los ambientes).
      m²        < 10              (no puede ser una vivienda)
      ambientes m²/ambiente < 8   (cada ambiente tendría menos de 8 m²)
      baños     m²/baño < 8
    No se usan topes duros (p. ej. "más de 15 ambientes"): un hotel, una oficina o una casa
    grande pueden tener muchos ambientes de verdad. Lo que no puede pasar es que no entren en su m².
    """
    out = df.copy()
    mask_m2 = out["m2_cubiertos"] < 10
    out.loc[mask_m2, "m2_cubiertos"] = np.nan

    mask_amb = (out["m2_cubiertos"] / out["ambientes"]) < 8
    mask_ban = (out["m2_cubiertos"] / out["banos"]) < 8
    out.loc[mask_amb, "ambientes"] = np.nan
    out.loc[mask_ban, "banos"] = np.nan

    out["m2_fuera_rango"] = mask_m2
    out["ambientes_fuera_rango"] = mask_amb
    out["banos_fuera_rango"] = mask_ban
    registrar(log, "m² imposible (<10)", "m2_cubiertos", mask_m2.sum(), "pasado a NaN")
    registrar(log, "Ambientes incoherentes", "ambientes", mask_amb.sum(), "pasado a NaN")
    registrar(log, "Baños incoherentes", "banos", mask_ban.sum(), "pasado a NaN")
    return out


def marcar_precios_atipicos(df, z_umbral=4, log=None):
    """
    No elimina nada: marca precios sospechosos.
      precio_placeholder -> 5 o más dígitos iguales seguidos (111111111, 99999...).
      precio_atipico     -> z robusto (mediana y MAD de log10) mayor al umbral, dentro de cada
                            combinación operación x moneda (así no se mezclan escalas).
      precio_valido      -> ninguna de las dos marcas.
    """
    out = df.copy()
    lp = np.log10(out["precio"].where(out["precio"] > 0))
    grupos = [out["operacion"], out["moneda"]]
    mediana = lp.groupby(grupos).transform("median")
    mad = (lp - mediana).abs().groupby(grupos).transform("median") * 1.4826
    out["precio_atipico"] = ((lp - mediana) / mad).abs() > z_umbral
    texto = out["precio"].map(lambda p: f"{int(p)}" if pd.notna(p) else "")
    out["precio_placeholder"] = texto.str.fullmatch(r"(\d)\1{4,}")
    out["precio_valido"] = ~(out["precio_atipico"] | out["precio_placeholder"])
    registrar(log, "Precio atípico o placeholder", "precio", (~out["precio_valido"]).sum(),
              "marcado (se conserva; se excluye de estadísticas de precio)")
    return out


# --------------------------------------------------------------------------------------
# Partición train/test (antes de imputar, para no filtrar información del test)
# --------------------------------------------------------------------------------------
def asignar_split(df, semilla=42, frac_test=0.2):
    """Columna `split` (train/test), estratificada por operación y reproducible."""
    out = df.copy()
    out["split"] = "train"
    rng = np.random.default_rng(semilla)
    for _, idx in out.groupby("operacion").groups.items():
        idx = np.array(list(idx))
        test = rng.choice(idx, size=int(round(len(idx) * frac_test)), replace=False)
        out.loc[test, "split"] = "test"
    return out


# --------------------------------------------------------------------------------------
# Recuperación e imputación
# --------------------------------------------------------------------------------------
def ambientes_desde_titulo(titulo):
    """Cantidad de ambientes que menciona el título ('3 Amb', 'Monoambiente'), o NaN."""
    t = str(titulo).lower()
    if "monoambiente" in t:
        return 1
    m = re.search(r"(\d+)\s*amb", t)
    if m and 1 <= int(m.group(1)) <= 10:
        return int(m.group(1))
    return np.nan


def validar_regla_titulo(df):
    """Qué tan seguido el título coincide con el dato cargado (sobre avisos que tienen ambos)."""
    conocido = df[df["ambientes"].notna()]
    desde_titulo = conocido["titulo"].map(ambientes_desde_titulo)
    comparables = desde_titulo.notna()
    return (desde_titulo[comparables] == conocido.loc[comparables, "ambientes"]).mean(), int(comparables.sum())


def recuperar_ambientes_titulo(df, log=None):
    """Completa `ambientes` desde el título donde falta. Deja `ambientes_origen`."""
    out = df.copy()
    out["ambientes_origen"] = np.where(out["ambientes"].notna(), "cargado", "faltante")
    falta = out["ambientes"].isna()
    rec = out.loc[falta, "titulo"].map(ambientes_desde_titulo)
    ok = rec[rec.notna()].index
    out.loc[ok, "ambientes"] = rec.loc[ok]
    out.loc[ok, "ambientes_origen"] = "titulo"
    registrar(log, "Ambientes desde el título", "ambientes", len(ok), "recuperado (regla validada)")
    return out


def _tramo_m2(m2):
    return pd.cut(m2, BINS_M2, labels=False)


def _moda(serie):
    serie = serie.dropna()
    return serie.mode().iloc[0] if len(serie) else np.nan


def ajustar_imputador(train):
    """Calcula con el conjunto de entrenamiento las tablas que se usan para imputar."""
    t = train.copy()
    t["tramo"] = _tramo_m2(t["m2_cubiertos"])
    return {
        "amb_grupo": t.groupby(["operacion", "tipo_propiedad", "tramo"])["ambientes"].median().to_dict(),
        "amb_tipo": t.groupby(["operacion", "tipo_propiedad"])["ambientes"].median().to_dict(),
        "amb_global": t["ambientes"].median(),
        "ban_grupo": t.groupby(["tipo_propiedad", "ambientes"])["banos"].agg(_moda).to_dict(),
        "ban_tipo": t.groupby("tipo_propiedad")["banos"].agg(_moda).to_dict(),
        "ban_global": _moda(t["banos"]),
    }


def _primero_valido(*candidatos):
    """Primer valor que no sea NaN (un grupo puede existir pero tener todos sus datos faltantes)."""
    for c in candidatos:
        if pd.notna(c):
            return c
    return np.nan


def imputar_variable(df, imp, variable):
    """Valores imputados (Serie) para las filas donde `variable` es NaN. No modifica `df`."""
    falta = df[variable].isna()
    sub = df[falta]
    if variable == "ambientes":
        tramo = _tramo_m2(sub["m2_cubiertos"])
        valores = [
            _primero_valido(imp["amb_grupo"].get((op, tp, tr)), imp["amb_tipo"].get((op, tp)), imp["amb_global"])
            for op, tp, tr in zip(sub["operacion"], sub["tipo_propiedad"], tramo)
        ]
    else:
        valores = [
            _primero_valido(imp["ban_grupo"].get((tp, amb)), imp["ban_tipo"].get(tp), imp["ban_global"])
            for tp, amb in zip(sub["tipo_propiedad"], sub["ambientes"])
        ]
    return pd.Series(valores, index=sub.index).round()


def imputar(df, imp, log=None):
    """Imputa ambientes y luego baños con las tablas del entrenamiento. Deja marcas de origen."""
    out = df.copy()
    amb = imputar_variable(out, imp, "ambientes")
    out.loc[amb.index, "ambientes"] = amb
    out.loc[amb.index, "ambientes_origen"] = "imputado"
    ban = imputar_variable(out, imp, "banos")
    out["banos_imputado"] = False
    out.loc[ban.index, "banos"] = ban
    out.loc[ban.index, "banos_imputado"] = True
    registrar(log, "Ambientes imputados", "ambientes", len(amb), "mediana por operación x tipo x tramo de m² (train)")
    registrar(log, "Baños imputados", "banos", len(ban), "moda por tipo x ambientes (train)")
    return out


def evaluar_imputacion(df_test, imp, variable, frac=0.2, semilla=0):
    """
    Control de la imputación: oculta una fracción de los valores conocidos del conjunto de test,
    los imputa con las tablas del entrenamiento y compara contra un baseline (global).
    Devuelve exactitud (coincidencia exacta) y error absoluto medio de ambos métodos.
    """
    conocidos = df_test[df_test[variable].notna()]
    muestra = conocidos.sample(frac=frac, random_state=semilla)
    real = muestra[variable]
    oculto = muestra.copy()
    oculto[variable] = np.nan
    pred = imputar_variable(oculto, imp, variable)
    base = imp["amb_global"] if variable == "ambientes" else imp["ban_global"]
    return pd.DataFrame({
        "metodo": ["grupo (propuesto)", "baseline global"],
        "exactitud": [(pred == real).mean(), (round(base) == real).mean()],
        "error_abs_medio": [(pred - real).abs().mean(), (round(base) - real).abs().mean()],
    }).round(3)


# --------------------------------------------------------------------------------------
# Moneda y variables derivadas
# --------------------------------------------------------------------------------------
def agregar_precio_usd(df, tipo_cambio=None):
    """
    `precio_usd`: igual a `precio` donde la moneda ya es USD. Para filas en ARS solo se calcula
    si se informa `tipo_cambio` = {"valor": pesos por dólar, "fuente": ..., "fecha": ...};
    si no, queda NaN (no se inventa una cotización).
    """
    out = df.copy()
    out["precio_usd"] = np.where(out["moneda"] == "USD", out["precio"], np.nan)
    if tipo_cambio is not None:
        ars = out["moneda"] == "ARS"
        out.loc[ars, "precio_usd"] = out.loc[ars, "precio"] / tipo_cambio["valor"]
    return out


def agregar_precio_m2(df):
    """
    `precio_m2` = precio / m2_cubiertos, en la moneda del aviso.
    Solo se calcula si el precio es válido y hay m² (no se imputa el denominador).
    """
    out = df.copy()
    ok = out["precio_valido"] & out["m2_cubiertos"].notna()
    out["precio_m2"] = np.where(ok, out["precio"] / out["m2_cubiertos"], np.nan)
    return out
