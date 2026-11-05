# Inteligencia de Mercado Inmobiliario — CABA
### TP Integrador · Analítica Descriptiva · Grupo 6 (PropTech)

Sistema de análisis del mercado inmobiliario de la Ciudad de Buenos Aires orientado a
detectar propiedades y barrios subvaluados y a recomendar, para cada oportunidad, la
estrategia de salida óptima (reventa o renta). Este repositorio contiene el trabajo hasta la
**Fase 3: validación de hipótesis, análisis avanzado y dashboard interactivo**.

---

## 🎯 El proyecto

**Interlocutor / usuario.** Un fondo de inversión inmobiliaria pequeño-mediano que opera en
CABA, decide a escala y enfrenta dos decisiones acopladas: *dónde y qué comprar* (barrios y
propiedades subvaluadas) y *qué hacer con cada adquisición* (reventa o renta).

**Contexto de negocio.** El mercado inmobiliario de CABA es dinámico, opaco y disperso: la
información está fragmentada en decenas de miles de avisos, con calidad heterogénea y sin una
referencia pública de valor que indique si una propiedad está cara o barata. El proyecto
transforma ese mercado en un **ranking accionable** de dónde comprar y qué estrategia aplicar.

**Alcance y unidad de análisis.** Geografía: CABA (48 barrios). Operación: venta (foco) y
alquiler (para rentabilidad). Tipologías: departamentos, PH y casas. El análisis combina dos
niveles: el **barrio** (rentabilidad, contexto, segmentación) y la **propiedad individual**
(subvaluación, ranking de oportunidades). No entra: estado físico de cada propiedad, costos de
refacción, propiedades fuera de CABA.

---

## 🧭 Resumen de hallazgos (Fase 3)

- **H1 — Subvaluación (confirmada como señal).** Un modelo de regresión lineal sobre precio/m²
  (R² = 0,55 fuera de muestra, superior al baseline de mediana = 0,455) estima el valor esperado
  de cada propiedad. Su residuo identifica **2.324 propiedades candidatas a subvaluación**. El
  residuo es una *señal a verificar*, no una conclusión de compra.
- **H2 — Rentabilidad premium vs. resto (confirmada).** Con rentabilidad **neta** de costos, los
  barrios premium rinden 2,98% frente a 3,77% del resto (−21%; el resto rinde 27% más,
  Mann-Whitney p = 0,0013). La
  segmentación objetiva lo refuerza (cluster caro 3,18% vs. barato 4,46%, p = 0,0004).
- **H3 — Contexto y precio (confirmada de forma matizada).** El índice de contexto global no
  muestra asociación significativa con el precio (Spearman rho = 0,24, p = 0,10), pero al
  desagregar emerge el driver real: la **seguridad** es el único componente con asociación fuerte
  y significativa (rho = +0,55, p = 0,0001). La relación es de asociación parcial, canalizada por
  la seguridad, no de determinación.
- **Segmentación de mercado.** Los barrios se agrupan en **cinco perfiles** (céntricos
  consolidados, premium de gran demanda, intermedios en desarrollo, oportunidad de renta, y el
  segmento exclusivo de Puerto Madero), que convierten el mapa de barrios en una tipología de
  inversión según la estrategia.
- **Producto final — Score de atractivo.** Integra rentabilidad (0,45), oportunidad (0,40) y
  contexto (0,15) en dos niveles: ranking de barrios (*dónde* buscar) y ranking de propiedades
  con dirección (*qué* comprar).

---

## ❓ Preguntas por nivel analítico

- **Descriptivo:** ¿cómo se distribuye el precio/m² por barrio y tipología? ¿La rentabilidad por barrio?
- **Diagnóstico:** ¿qué variables se asocian al precio/m²? ¿Por qué algunos barrios rinden más por alquiler?
- **Predictivo:** dada una propiedad, ¿cuál es su precio/m² esperado? ¿Está subvaluada?
- **Prescriptivo:** ¿en qué barrios conviene comprar? ¿Qué propiedades concretas? ¿Reventa o renta?

---

## 📌 Hipótesis y KPIs

**Hipótesis (evaluadas en Fase 3)**
- **H1** — Existe una proporción relevante de propiedades cuyo precio se aparta de su valor
  esperado (candidatas a subvaluación). → *Confirmada como señal (modelo + residuo).*
- **H2** — Los barrios premium tienen menor rentabilidad neta por alquiler que los medios/bajos.
  → *Confirmada (−21%, p = 0,0013; reforzada por clustering, p = 0,0004).*
- **H3** — El precio/m² se relaciona (asociación, no causa) con variables de contexto. →
  *Confirmada de forma matizada: la asociación se canaliza principalmente por la seguridad.*

**KPIs principales:** Precio/m² · Índice de subvaluación (residuo del modelo) · Rentabilidad
neta · Densidad de oportunidad · Score de atractivo (compuesto, z-score, pesos 0,45/0,40/0,15).

---

## 📁 Estructura del repositorio

```
AD_Trabajo_Practico_G6/
├── data/
│   ├── raw/                              # Datasets crudos del scraping (sin modificar)
│   │   ├── mercadolibre_venta_caba.csv
│   │   ├── mercadolibre_alquiler_caba.csv
│   │   └── argenprop_departamentos_caba.csv
│   ├── processed/                        # Dataset limpio + productos del análisis
│   │   ├── propiedades_ml_limpio.csv
│   │   ├── diccionario_datos.csv
│   │   ├── log_limpieza.csv
│   │   ├── score_barrios.csv             # Score de atractivo por barrio (dashboard)
│   │   ├── ranking_oportunidades.csv     # Top de propiedades con id_aviso y link (dashboard)
│   │   ├── clusters_barrios.csv          # Segmentación + coordenadas PCA (dashboard)
│   │   └── metricas_modelo.csv           # Métricas del modelo vs. baseline (dashboard)
│   └── external/                         # Fuentes externas + contexto consolidado
│       ├── contexto_por_barrio.csv       # Transporte, seguridad y comercios por barrio
│       └── (crudos de transporte, delitos, comercios, población)
├── notebooks/
│   ├── 00_extraccion_datos.ipynb         # Extracción (scraping)
│   ├── 01_calidad_y_limpieza.ipynb       # Evaluación de calidad y limpieza
│   ├── 02_eda_inicial.ipynb              # Análisis exploratorio
│   ├── 03_fuentes_externas.ipynb         # Integración de fuentes externas (join espacial)
│   └── 04_desarrollo_analitico_avanzado.ipynb  # Hipótesis, modelos, clustering, Score
├── src/
│   ├── limpieza.py                       # Funciones de limpieza reutilizables
│   └── eda.py                            # Funciones de análisis reutilizables
├── scrapers/                             # Scripts de extracción
├── dashboard/                            # Dashboard interactivo (Power BI)
│   └── Dashboard.pbix
├── docs/                                 # Documentos de entrega
│   └── entrega1_contexto_negocio.pdf
├── README.md
└── requirements.txt
```

---

## 🗂️ Datasets y fuentes

**Fuentes propias (scraping):**

| Fuente | Operación | Registros | Técnica |
|---|---|---|---|
| MercadoLibre | Venta (usados + emprendimientos) | ~45.568 | Scraping HTML (Playwright/requests) |
| MercadoLibre | Alquiler | ~10.166 | Scraping HTML segmentado por barrio |
| Argenprop | Alquiler | ~1.000 | Scraping HTML |

> El dataset procesado trabaja únicamente con MercadoLibre. Argenprop se excluye por volumen
> marginal, ser solo alquiler y su menor calidad; su crudo se conserva en `data/raw`.

**Fuentes externas (Fase 3, integradas):**

| Fuente | Organismo | Nivel | Variable derivada | Unión |
|---|---|---|---|---|
| Polígonos de barrios | BA Data (GCBA) | Barrio | Base geográfica, superficie | — |
| Población | citypopulation / INDEC | Barrio | Normalización de delitos | Por nombre |
| Subte, tren, colectivos | BA Data / Sec. Transporte | Georref. | Acceso a transporte | Join espacial |
| Delitos (Mapa del Delito) | BA Data (GCBA) | Georref. | Inseguridad (delitos/mil) | Join espacial |
| Comercios (MOC) | BA Data (GCBA) | Zona | Actividad comercial | Zona → barrio |

> Validaciones: población por barrio contrastada contra el total del INDEC por comuna
> (diferencias < 2%); joins espaciales con >99% de asignación; rankings coherentes con el mercado.

---

## ⚙️ Reproducir el análisis

**Dependencias:** Python 3.10+

```bash
pip install -r requirements.txt
playwright install chromium   # solo para el scraper de MercadoLibre
```

**Orden de ejecución:**
1. *(Opcional — extracción)* `notebooks/00_extraccion_datos.ipynb` o los scripts de `scrapers/`.
   Generan los CSV en `data/raw/`. Requiere navegador real (no corre en Colab) por la protección
   anti-bot.
2. **Limpieza:** `notebooks/01_calidad_y_limpieza.ipynb`. Parte de `data/raw/`, aplica la limpieza
   y genera `data/processed/` (dataset limpio, diccionario y log).
3. **EDA:** `notebooks/02_eda_inicial.ipynb`. Análisis exploratorio.
4. **Fuentes externas:** `notebooks/03_fuentes_externas.ipynb`. Trae y procesa las fuentes del GCBA
   mediante join espacial y genera `data/external/contexto_por_barrio.csv`.
5. **Análisis avanzado:** `notebooks/04_desarrollo_analitico_avanzado.ipynb`. Evalúa las hipótesis,
   entrena el modelo, construye el clustering y el Score. Sus resultados son los 4 CSV de
   `data/processed/` que alimentan el dashboard.
6. **Dashboard:** abrir `dashboard/Dashboard.pbix` en Power BI. Se alimenta de los CSV de
   `data/processed/`.

> Las notebooks clonan el repositorio automáticamente en Colab y usan rutas relativas. El tipo de
> cambio se obtiene de la API de bluelytics para una fecha fija, con valor de respaldo.

---

## 📤 Salidas principales

- `data/processed/propiedades_ml_limpio.csv` — dataset limpio (~54.800 registros).
- `data/external/contexto_por_barrio.csv` — contexto (transporte, seguridad, comercios) por barrio.
- `data/processed/score_barrios.csv` — Score de atractivo por barrio.
- `data/processed/ranking_oportunidades.csv` — top de propiedades subvaluadas, con dirección, `id_aviso` y `link`.
- `data/processed/clusters_barrios.csv` — segmentación de barrios con coordenadas PCA.
- `data/processed/metricas_modelo.csv` — métricas del modelo vs. baseline.
- `dashboard/Dashboard.pbix` — tablero interactivo para el fondo.

> Por su tamaño (~22 MB), el dataset procesado puede reconstruirse corriendo las notebooks desde los crudos.

---

## 🔬 Decisiones metodológicas clave

- **Modelo de valor esperado (H1):** regresión lineal sobre **precio/m²** (no precio total, que
  estaría dominado por la superficie). Universo acotado a 20-250 m² y 500-10.000 USD/m² para
  excluir lotes y valores atípicos. Validado fuera de muestra contra un baseline de mediana.
- **Rentabilidad neta (H2):** costos de transacción con fuente (relevamiento CABA 2026: comisión,
  sellos, escribanía ≈ 8,6%) y costos recurrentes como supuestos declarados (vacancia, mantenimiento,
  impuesto a la renta).
- **Índice de contexto (H3):** construido por join espacial de las fuentes del GCBA, normalizado por
  superficie/población y estandarizado (z-score). La seguridad se invierte (más delitos = peor).
- **Segmentación:** K-means sobre 6 variables reducidas con PCA; K=4 elegido por codo + silhouette;
  Puerto Madero tratado como segmento aparte por ser un outlier extremo.
- **Normalización de nombres de barrio:** unificación de tildes, mayúsculas y casos especiales entre
  fuentes, para garantizar los joins.

---

## ⚠️ Limitaciones conocidas

- **El residuo es una señal, no una certeza:** el modelo explica la mitad de la variación del
  precio/m²; el resto depende de atributos no observados (estado, orientación, piso). Algunas
  candidatas con residuo extremo son probables errores de publicación, no oportunidades reales.
- **Nivel barrio para rentabilidad y contexto:** calculados sobre 40 barrios con datos suficientes
  de venta y alquiler; los de poca oferta quedan fuera.
- **El índice de contexto promedia sus tres componentes con pesos iguales,** pero el análisis
  muestra que la seguridad pesa mucho más: ponderarlos de forma desigual es una mejora futura.
- **Costos recurrentes como supuestos declarados,** no valores específicos del inversor.
- **Corte temporal único:** sin análisis de evolución ni valorización futura.
- **El sistema prioriza, no garantiza:** la decisión final requiere verificación individual,
  análisis de costos, liquidez y estrategia de salida.

---

## 🔄 Evolución por fase

- **PE1 → PE2:** reformulación de hipótesis (H1 a residuo de modelo, H2 a neta, H3 a asociación),
  Score con z-score y pesos justificados, limpieza y EDA.
- **PE2 → PE3:** integración de fuentes externas (join espacial), evaluación estadística de las tres
  hipótesis, modelo de valor esperado validado, segmentación por clustering, Score en dos niveles
  (barrio y propiedad) y dashboard interactivo. Depuración del repositorio.

---

## 👥 Integrantes — Grupo 6
Erlij, Ian · Hussey, Juan Martín · Falaq, Manuel · Lachter, Federico
