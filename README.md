# Inteligencia de Mercado Inmobiliario — CABA
### TP Integrador · Analítica Descriptiva · Grupo 6 (PropTech)

Sistema de análisis del mercado inmobiliario de la Ciudad de Buenos Aires orientado a
detectar propiedades y barrios subvaluados y a recomendar, para cada oportunidad, la
estrategia de salida óptima (reventa o renta). Este repositorio contiene el trabajo hasta
la **Fase 2: análisis exploratorio de datos (EDA)**.

---

## 🎯 El proyecto

**Interlocutor / usuario.** Un fondo de inversión inmobiliaria pequeño-mediano que opera en
CABA, decide a escala y enfrenta dos decisiones acopladas: *dónde y qué comprar* (barrios y
tipologías subvaluadas) y *qué hacer con cada adquisición* (reventa o renta).

**Contexto de negocio.** El mercado inmobiliario de CABA es dinámico, opaco y disperso: la
información está fragmentada en decenas de miles de avisos, con calidad heterogénea y sin una
referencia pública de valor que indique si una propiedad está cara o barata. El proyecto busca
transformar ese mercado en un ranking accionable de dónde comprar y qué estrategia aplicar.

**Alcance y unidad de análisis.** Geografía: CABA (48 barrios). Operación: venta (foco) y
alquiler (para rentabilidad). Tipologías: departamentos, PH y casas. **Unidad de análisis: el
barrio** (y, dentro de él, la tipología). No entra: estado físico de cada propiedad, costos de
refacción, propiedades fuera de CABA.

---

## ❓ Preguntas por nivel analítico

- **Descriptivo:** ¿cómo se distribuye el precio/m² por barrio y tipología? ¿Cuál es la rentabilidad por barrio?
- **Diagnóstico:** ¿qué variables se asocian al precio/m²? ¿Por qué algunos barrios rinden más por alquiler?
- **Predictivo:** dada una propiedad, ¿cuál es su precio/m² esperado? ¿Cuánto rentaría?
- **Prescriptivo:** ¿en qué barrios conviene comprar? ¿Reventa o renta? ¿Ranking final de atractivo?

---

## 📌 Hipótesis y KPIs (revisados)

**Hipótesis**
- **H1** — Existe una proporción relevante de propiedades cuyo precio se aparta de su valor esperado (candidatas a subvaluación). *Evidencia preliminar a favor (dispersión intra-grupo, CV=0,30).*
- **H2** — Los barrios premium tienen menor rentabilidad neta por alquiler que los medios/bajos. *Evidencia preliminar a favor (bruta: 4,0% vs 5,2%, p=0,001).*
- **H3** — El precio/m² se relaciona (asociación, no causa) con variables de contexto. *No evaluable aún: requiere fuentes externas.*

**KPIs principales:** Precio/m² · Índice de subvaluación (residuo del modelo) · Rentabilidad neta · Retorno de reventa · Retorno anualizado · Densidad de oportunidad · Score de atractivo (compuesto, z-score, pesos 0,45/0,40/0,15).

---

## 📁 Estructura del repositorio

```
AD_Trabajo_Practico_G6/
├── data/
│   ├── raw/                          # Datasets crudos (sin modificar)
│   │   ├── argenprop_departamentos_caba.csv
│   │   ├── mercadolibre_alquiler_caba.csv
│   │   └── mercadolibre_venta_caba.csv
│   └── processed/                    # Dataset limpio + diccionario + log
│       ├── propiedades_ml_limpio.csv
│       ├── diccionario_datos.csv
│       └── log_limpieza.csv
├── notebooks/
│   ├── 01_calidad_y_limpieza.ipynb   # Evaluación de calidad y limpieza
│   └── 02_eda_inicial.ipynb          # Análisis exploratorio
├── src/
│   ├── limpieza.py                   # Funciones de limpieza reutilizables
│   └── eda.py                        # Funciones de análisis reutilizables
├── scrapers/                         # Scripts de extracción
│   ├── scraper_argenprop.py
│   ├── scraper_ml_venta.py
│   └── scraper_ml_alquiler.py
├── entrega1_contexto_negocio.pdf     # Documento de contexto, hipótesis y KPIs
└── README.md
```

---

## 🗂️ Datasets y fuentes

**Fuentes propias (scraping):**

| Fuente | Operación | Registros | Técnica |
|---|---|---|---|
| MercadoLibre | Venta (usados + emprendimientos) | ~45.568 | Scraping HTML (Playwright/requests) |
| MercadoLibre | Alquiler | ~10.166 | Scraping HTML segmentado por barrio |
| Argenprop | Alquiler | ~1.000 | Scraping HTML |

> **Nota:** el dataset procesado trabaja únicamente con MercadoLibre. Argenprop se excluye por
> volumen marginal, ser solo alquiler y su menor calidad; su crudo se conserva en `data/raw`.

**Fuentes externas priorizadas (Fase 3, aún no integradas):** estaciones de transporte, mapa
del delito, comercios/habilitaciones y polígonos de barrios (todas de BA Data, GCBA), y tipo de
cambio histórico (bluelytics, ya aplicado). Su compatibilidad con la unidad de análisis se
documenta en `02_eda_inicial`.

---

## ⚙️ Reproducir el análisis

**Dependencias:** Python 3.10+

```bash
pip install pandas numpy matplotlib seaborn scipy requests beautifulsoup4 playwright curl_cffi
playwright install chromium   # solo para el scraper de MercadoLibre
```

**Orden de ejecución:**
1. *(Opcional — extracción)* Ejecutar los scripts de `scrapers/` localmente. Generan los CSV en `data/raw/`. Requiere navegador real (no corre en Colab) por la protección anti-bot.
2. **Limpieza:** correr `notebooks/01_calidad_y_limpieza.ipynb`. Parte de `data/raw/`, aplica la limpieza y genera `data/processed/` (dataset limpio, diccionario y log).
3. **EDA:** correr `notebooks/02_eda_inicial.ipynb`. Reconstruye el dataset procesado desde el crudo y produce el análisis exploratorio.

> Las notebooks clonan el repositorio automáticamente en Colab y usan rutas relativas (no requieren editar código). El tipo de cambio se obtiene de la API de bluelytics para una fecha fija, con valor de respaldo.

---

## 📤 Salidas

- `data/processed/propiedades_ml_limpio.csv` — dataset limpio (~54.800 registros).
- `data/processed/diccionario_datos.csv` — diccionario de variables (significado, tipo, unidad, fuente, transformaciones).
- `data/processed/log_limpieza.csv` — registro de transformaciones aplicadas.

> Por su tamaño (~22 MB), el dataset procesado puede reconstruirse corriendo la notebook 01/02 desde los crudos.

---

## 🔄 Cambios respecto de la PreEntrega 1

A partir de la devolución, se reformularon: **H1** (de dispersión vs. mediana a residuo de un
modelo), **H2** (de rentabilidad bruta a neta), **H3** (de lenguaje causal a asociación), y el
**Score** (z-score, pesos justificados, sensibilidad y validación). Se eliminó la pregunta de
valorización futura (inviable con corte único), se reencuadró el contexto con hitos fechados e
indicadores, y se añadió la dimensión regulatoria y el predominio de operaciones al contado. En
lo técnico: función de carga parametrizada, normalización de nombres de scripts y este README.

---

## ⚠️ Limitaciones conocidas

- **Corte temporal único:** sin análisis de evolución ni valorización futura.
- **Estado de la propiedad no observable:** limita distinguir subvaluación real de descuento justificado.
- **Tope de captura por barrio (~1.200 avisos):** el volumen de avisos no mide la oferta real.
- **Rentabilidad bruta:** la neta (con costos) puede reducir la brecha entre barrios.
- **H3 no evaluable aún:** pendiente de integrar las fuentes externas.

---

## 📋 Observaciones pendientes y plan

- Construir el **modelo de valor de referencia** (residuos) → validación plena de H1.
- **Integrar fuentes externas** y construir el índice de Contexto → H3.
- Calcular **rentabilidad neta** y retornos de reventa → validación de H2 y comparación de estrategias.
- Ensamblar el **Score de atractivo** final.

---

## 👥 Integrantes — Grupo 6
Erlij, Ian · Hussey, Juan Martín · Falaq, Manuel · Lachter, Federico
