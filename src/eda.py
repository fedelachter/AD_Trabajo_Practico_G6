# -*- coding: utf-8 -*-
"""
eda.py — Funciones reutilizables para el análisis exploratorio (notebook 02_eda_inicial).

Agrupa la lógica de graficado y testeo estadístico usada en el EDA, para mantener la
notebook enfocada en las llamadas, la interpretación y las conclusiones.

Uso:
    from src import eda
    eda.analisis_univariado(df["precio_m2"], "Precio por m²", "USD/m²")

Dependencias: numpy, pandas, matplotlib, seaborn, scipy.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import skew, kruskal, chi2_contingency


def analisis_univariado(serie, nombre=None, unidad="", bins=50):
    """
    Resume y grafica una variable NUMÉRICA: estadísticos robustos + asimetría,
    histograma (con media y mediana) y boxplot.

    Parámetros
    ----------
    serie : pd.Series        Variable numérica a analizar.
    nombre : str             Nombre para los títulos (por defecto, el de la serie).
    unidad : str             Unidad para los ejes (ej. "USD/m²").
    bins : int               Cantidad de barras del histograma.

    Devuelve
    --------
    dict con n, nulos, media, mediana, desvío, cuantiles, min, max y skew.
    """
    s = serie.dropna()
    nombre = nombre or serie.name

    stats = {
        "n": len(s), "nulos": serie.isna().sum(),
        "media": s.mean(), "mediana": s.median(), "desvío": s.std(),
        "p5": s.quantile(.05), "p25": s.quantile(.25),
        "p75": s.quantile(.75), "p95": s.quantile(.95),
        "min": s.min(), "max": s.max(), "skew": skew(s),
    }

    fig, ax = plt.subplots(1, 2, figsize=(12, 3.8))
    sns.histplot(s, bins=bins, ax=ax[0], color="steelblue")
    ax[0].axvline(s.mean(), color="red", ls="--", lw=1.5, label=f"media {s.mean():.1f}")
    ax[0].axvline(s.median(), color="green", ls="-", lw=1.5, label=f"mediana {s.median():.1f}")
    ax[0].set_title(f"Distribución de {nombre}"); ax[0].set_xlabel(unidad); ax[0].legend()
    sns.boxplot(x=s, ax=ax[1], color="lightsteelblue")
    ax[1].set_title(f"Boxplot de {nombre}"); ax[1].set_xlabel(unidad)
    plt.tight_layout(); plt.show()

    print(f"{nombre}  |  n={stats['n']:,}  nulos={stats['nulos']:,}  "
          f"media={stats['media']:.1f}  mediana={stats['mediana']:.1f}  skew={stats['skew']:.2f}")
    return stats


def analisis_categorico(serie, nombre=None, top=None, horizontal=False):
    """
    Resume y grafica una variable CATEGÓRICA: frecuencias absolutas y relativas
    + gráfico de barras.

    Parámetros
    ----------
    serie : pd.Series        Variable categórica a analizar.
    nombre : str             Nombre para los títulos.
    top : int                Limita a las N categorías más frecuentes (útil para barrio).
    horizontal : bool        Barras horizontales (recomendado para muchas categorías).

    Devuelve
    --------
    pd.DataFrame con avisos y % por categoría.
    """
    s = serie.dropna()
    nombre = nombre or serie.name

    frec = s.value_counts()
    tabla = pd.DataFrame({"avisos": frec, "%": (frec / len(s) * 100).round(1)})
    mostrar = tabla.head(top) if top else tabla

    fig, ax = plt.subplots(figsize=(8, max(3, len(mostrar) * 0.35)) if horizontal else (8, 4))
    if horizontal:
        mostrar["avisos"].iloc[::-1].plot.barh(ax=ax, color="steelblue")
        ax.set_xlabel("avisos")
    else:
        mostrar["avisos"].plot.bar(ax=ax, color="steelblue")
        ax.set_ylabel("avisos"); plt.xticks(rotation=45, ha="right")
    ax.set_title(f"Distribución de {nombre}" + (f" (top {top})" if top else ""))
    plt.tight_layout(); plt.show()

    print(f"{nombre}  |  categorías: {s.nunique()}  |  n={len(s):,}  nulos={serie.isna().sum():,}")
    return tabla


def boxplot_cat_num(df, cat, num, ax):
    """
    Cruce CATEGÓRICA vs. NUMÉRICA: boxplot de `num` por `cat` (ordenado por mediana)
    + test de Kruskal-Wallis (no paramétrico, robusto a la asimetría). El resultado
    del test se muestra en el título. Dibuja sobre el `ax` provisto.
    """
    orden = df.groupby(cat)[num].median().sort_values(ascending=False).index
    sns.boxplot(data=df, x=cat, y=num, order=orden, showfliers=False, ax=ax)
    grupos = [g[num].dropna() for _, g in df.groupby(cat)]
    h, p = kruskal(*grupos)
    ax.set_title(f"{num} por {cat}\n(Kruskal p={p:.1e})", fontsize=10)
    ax.set_xlabel(""); ax.tick_params(axis="x", rotation=30)


def barras_apiladas_cat_cat(df, cat1, cat2, labels2=None):
    """
    Cruce CATEGÓRICA vs. CATEGÓRICA: barras apiladas en proporción + test de
    chi-cuadrado (asociación) y Cramér's V (tamaño del efecto). Dado el gran N,
    el chi² tiende a ser significativo, por lo que Cramér's V mide la relevancia
    práctica. Ambos se muestran en el título.
    """
    tabla = pd.crosstab(df[cat1], df[cat2])
    prop = tabla.div(tabla.sum(axis=1), axis=0)
    fig, ax = plt.subplots(figsize=(7, 4))
    prop.plot(kind="bar", stacked=True, ax=ax, colormap="Set2")
    chi2, p, dof, _ = chi2_contingency(tabla)
    v = np.sqrt(chi2 / (tabla.sum().sum() * (min(tabla.shape) - 1)))
    ax.set_title(f"{cat1} vs. {cat2}  (chi² p={p:.1e}, Cramér's V={v:.2f})", fontsize=10)
    ax.set_xlabel(""); ax.set_ylabel("proporción"); plt.xticks(rotation=0)
    if labels2:
        ax.legend(labels2, title="")
    plt.tight_layout(); plt.show()
