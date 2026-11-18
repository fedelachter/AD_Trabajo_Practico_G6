# Inteligencia de Mercado Inmobiliario — CABA
### Análisis del mercado inmobiliario de la Ciudad de Buenos Aires para decisiones de inversión · Grupo 6

Sistema de análisis del mercado inmobiliario de la Ciudad de Buenos Aires orientado a
detectar propiedades y barrios subvaluados y a recomendar, para cada oportunidad, la
estrategia de salida óptima (reventa o renta). El repositorio cubre el flujo completo: desde
la extracción y limpieza de los datos hasta la validación de hipótesis, el modelo de valor
esperado, la segmentación de barrios y un dashboard interactivo para el usuario final.

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

## 🧭 Resumen de hallazgos

- **H1 — Subvaluación (confirmada como señal).** Un modelo de regresión lineal sobre precio/m²
  (R² = 0,55 fuera de muestra, superior al baseline de mediana = 0,46) estima el valor esperado
  de cada propiedad. Su residuo identifica **1.912 propiedades candidatas a subvaluación**
  (8,2% de los usados, con residuo ≤ −37,5%). El residuo es una *señal a verificar*, no una
  conclusión de compra.
- **H2 — Rentabilidad premium vs. resto (confirmada vía segmentación).** Con rentabilidad **neta**
  de costos, la comparación directa premium vs. resto es sugestiva pero **no concluyente**
  (4,37% vs. 4,60%, Mann-Whitney p = 0,18; solo 4 barrios premium). La evidencia robusta viene de
  la **segmentación objetiva por clustering**: el cluster de mayor precio rinde 4,30% neto frente
  al 5,33% del más barato (los accesibles rinden un 24% más, p = 0,0021).
- **H3 — Contexto y precio (confirmada de forma matizada).** El índice de contexto global no
  muestra asociación significativa con el precio (Spearman rho = 0,24, p = 0,10), pero al
  desagregar emerge el driver real: la **seguridad** es el único componente con asociación fuerte
  y significativa (rho = +0,55, p = 0,0001). La relación es de asociación parcial, canalizada por
  la seguridad, no de determinación.
- **Segmentación de mercado.** Los barrios se agrupan en **cinco perfiles** (céntricos
  consolidados, oportunidad de renta, premium de gran demanda, intermedios en desarrollo, y el
  segmento exclusivo de Puerto Madero), que convierten el mapa de barrios en una tipología de
  inversión según la estrategia.
- **Producto final — Score de atractivo.** Integra rentabilidad (0,45), oportunidad (0,40) y
  contexto (0,15) en dos niveles: ranking de barrios (*dónde* buscar) y ranking de propiedades
  con dirección (*qué* comprar). Además, para cada candidata se recomienda **renta o reventa**.

---

## ❓ Preguntas por nivel analítico

- **Descriptivo:** ¿cómo se distribuye el precio/m² por barrio y tipología? ¿La rentabilidad por barrio?
- **Diagnóstico:** ¿qué variables se asocian al precio/m²? ¿Por qué algunos barrios rinden más por alquiler?
- **Predictivo:** dada una propiedad, ¿cuál es su precio/m² esperado? ¿Está subvaluada?
- **Prescriptivo:** ¿en qué barrios conviene comprar? ¿Qué propiedades concretas? ¿Reventa o renta?

---

## 📌 Hipótesis y KPIs

**Hipótesis**
- **H1** — Existe una proporción relevante de propiedades cuyo precio se aparta de su valor
  esperado (candidatas a subvaluación). → *Confirmada como señal (modelo + residuo); 8,2% de los
  usados supera el umbral de −37,5%.*
- **H2** — Los barrios premium tienen menor rentabilidad neta por alquiler que los medios/bajos.
  → *Confirmada vía segmentación objetiva (cluster caro 4,30% vs. barato 5,33%, p = 0,0021); la
  comparación directa premium/resto no alcanza significancia (p = 0,18).*
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
│   │   ├── oportunidades.csv             # Ranking de propiedades subvaluadas (dashboard)
│   │   ├── score_barrios.csv             # Score de atractivo por barrio (dashboard)
│   │   ├── perfiles_barrios.csv          # Segmentación / clusters por barrio (dashboard)
│   │   └── estrategia.csv                # Renta vs. reventa por propiedad (dashboard)
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
│   ├── eda.py                            # Funciones de análisis reutilizables
│   └── exportar_csv.py                   # Exportación de las 4 salidas para el dashboard
├── scrapers/                             # Scripts de extracción
├── dashboard/                            # Dashboard interactivo (Power BI)
│   └── dashboard.pbix
├── docs/                                 # Documentación de soporte
│   └── contexto_negocio.pdf
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

**Fuentes externas:**

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

**Local (recomendado):**
```bash
git clone https://github.com/fedelachter/AD_Trabajo_Practico_G6
cd AD_Trabajo_Practico_G6
pip install -r requirements.txt
playwright install chromium   # solo si se re-ejecuta el scraper de MercadoLibre
jupyter lab                   # o abrir las notebooks en VSCode
```

**Google Colab:** las notebooks usan rutas relativas y **no clonan el repo por sí solas**. Al
inicio de la sesión, clonalo una vez en una celda aparte antes de correr el setup:
```python
import os
if not os.path.exists("AD_Trabajo_Practico_G6"):
    !git clone -q https://github.com/fedelachter/AD_Trabajo_Practico_G6
%cd AD_Trabajo_Practico_G6
```
Luego el setup de cada notebook detecta la raíz del proyecto y continúa; si no encuentra el
repositorio, se detiene con un mensaje de error claro.

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
   entrena el modelo, construye el clustering y el Score, y exporta los 4 CSV que alimentan el
   dashboard (en `data/processed/`).

> El tipo de cambio ARS→USD se obtiene de la API de bluelytics para una fecha fija
> (reproducibilidad), con un valor de respaldo si la API no responde.

---

## 🖥️ Dashboard

El tablero interactivo está en `dashboard/dashboard.pbix` y se abre con **Power BI Desktop**
(gratuito, Windows). Se alimenta de los cuatro CSV de `data/processed/`
(`oportunidades.csv`, `score_barrios.csv`, `perfiles_barrios.csv`, `estrategia.csv`), que se
regeneran corriendo la notebook `04`.

**Cómo acceder:**
1. Instalar Power BI Desktop.
2. Abrir `dashboard/dashboard.pbix`.
3. Si los datos no aparecen, usar *Actualizar* (los CSV se leen desde `data/processed/`).

El tablero permite explorar las oportunidades por barrio, presupuesto y estrategia (renta vs.
reventa), y consultar el ranking de propiedades con su nivel de subvaluación.

---

## 📤 Salidas principales

- `data/processed/propiedades_ml_limpio.csv` — dataset limpio (~54.800 registros).
- `data/external/contexto_por_barrio.csv` — contexto (transporte, seguridad, comercios) por barrio.
- `data/processed/oportunidades.csv` — ranking de propiedades subvaluadas, con dirección, precio, subvaluación y score.
- `data/processed/score_barrios.csv` — Score de atractivo por barrio (rentabilidad, oportunidad, contexto, cluster).
- `data/processed/perfiles_barrios.csv` — segmentación de barrios (clusters y variables de perfil).
- `data/processed/estrategia.csv` — recomendación renta vs. reventa por propiedad.
- `dashboard/dashboard.pbix` — tablero interactivo para el fondo.

> Por su tamaño (~22 MB), el dataset procesado puede reconstruirse corriendo las notebooks desde los crudos.

---

## 🔬 Decisiones metodológicas clave

- **Modelo de valor esperado (H1):** regresión lineal sobre **precio/m²** (no precio total, que
  estaría dominado por la superficie). Universo acotado a 20-250 m² y 500-10.000 USD/m² para
  excluir lotes y valores atípicos. Validado **fuera de muestra** y, para la detección de
  subvaluación, con **validación cruzada** (sin leakage) contra un baseline de mediana.
- **Rentabilidad neta (H2):** calculada con **comparables del mismo tamaño** (tramos barrio ×
  ambientes) para no mezclar superficies. Costos de transacción con fuente (relevamiento CABA 2026:
  comisión, sellos, escribanía ≈ 8,6%) y costos recurrentes como supuestos declarados (vacancia,
  mantenimiento, impuesto a la renta).
- **Índice de contexto (H3):** construido por join espacial de las fuentes del GCBA, normalizado por
  superficie/población y estandarizado (z-score). La seguridad se invierte (más delitos = peor).
- **Segmentación:** K-means sobre 6 variables reducidas con PCA; K=4 elegido por codo + silhouette;
  Puerto Madero tratado como segmento aparte por ser un outlier extremo.
- **Estrategia de salida:** para cada candidata se compara el retorno **total** de reventa (capturando
  el 65% del descuento detectado, netos de costos de compra y venta) contra la **renta neta anual**,
  en un horizonte de 5 años.
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
- **Sin intervalos de confianza explícitos:** las hipótesis se validaron con tests de significancia
  (p-valores), pero no se reportan IC; sería un refuerzo de robustez pendiente.
- **Corte temporal único:** sin análisis de evolución ni valorización futura.
- **El sistema prioriza, no garantiza:** la decisión final requiere verificación individual,
  análisis de costos, liquidez y estrategia de salida.

---

## 🔧 Controles de calidad

Resumen de los problemas detectados en el análisis y el código, y su resolución:

| Observación | Estado | Qué cambió | Dónde se verifica |
|---|---|---|---|
| **Data leakage** en la detección de subvaluación (el modelo predecía sobre datos que había usado para entrenar) | **Resuelta** | Predicción in-sample reemplazada por **validación cruzada** (`cross_val_predict`, 5-fold): cada propiedad recibe su valor esperado de un modelo que no la vio | nb 04, celda del residuo sin leakage (sección H1) |
| **Umbral de subvaluación circular** (definido con un percentil, siempre "da") | **Resuelta** | Umbral **absoluto y falsable** (−37,5%, anclado al error típico del modelo, MAE ≈ 27%); lo cumple el 8,2% de los usados | nb 04, sección H1 |
| **Valores hardcodeados** en las conclusiones (rho, R² fijos) | **Resuelta** | Las celdas **calculan e imprimen** los valores (rho con/sin PM, R² múltiple vs. índice) en vez de citarlos a mano | nb 04, celdas de H3 |
| **Rentabilidad sesgada**: comparaba venta (~87 m²) con alquiler (~45 m²) | **Resuelta** | Rentabilidad por **comparables del mismo tamaño** (tramos barrio × ambientes con ≥10 avisos); el barrio toma la mediana de sus tramos | nb 04, sección H2 |
| Faltaba **recomendar la estrategia de salida** por propiedad | **Resuelta** | Nuevo análisis **renta vs. reventa** (retorno total vs. renta anual; captura 65%, horizonte 5 años) | nb 04, sección "renta vs. reventa" |
| Ranking contaminado por **avisos no comparables** (pozo, anticipos, a refaccionar) | **Resuelta** | Filtro por palabras clave en título/link antes del ranking (134 avisos excluidos) | nb 04, celda del filtro de no comparables |
| Ranking **dominado por Villa Lugano** (vivienda social que el modelo no capta) | **Resuelta** | Villa Lugano se analiza aparte; el ranking usa *sweet spot* de subvaluación y alerta de verificación | nb 04, sección del ranking |
| **`git clone` embebido en las notebooks** | **Resuelta** | Quitado de las 4 notebooks; ahora detectan la raíz y cortan con error claro. El clone en Colab queda documentado en este README | nb 01–04, celda de setup; sección "Reproducir" |
| **Lógica reutilizable centralizada en `src/`** | **Parcial** | La exportación de salidas se modularizó (`src/exportar_csv.py`); el traslado completo de modelo/score a `src/` con tests `pytest` queda pendiente | `src/exportar_csv.py` |
| **`requirements.txt` incompleto** (faltaban scikit-learn y geopandas) | **Resuelta** | Completado con `scikit-learn`, `geopandas`, `jupyter`/`ipykernel` y `lxml` | `requirements.txt` |
| **"Cantidad de avisos" usada como liquidez** | **Resuelta** | `densidad_oferta` reencuadrada como **volumen/tamaño de la oferta**; se quita la interpretación de liquidez (no medible con estos datos) | nb 04, celdas de perfil e interpretación de clusters |
| **Intervalos de confianza** en las hipótesis | **No resuelta** | Las hipótesis se validaron con tests de significancia (Mann-Whitney, Spearman con p-valores); faltan los IC explícitos | — |

> **Sobre lo pendiente.** El traslado completo de la lógica a `src/` y los intervalos de confianza
> **no alteran los resultados ni las conclusiones**: las hipótesis se sostienen en los tests de
> significancia ya reportados (p-valores), y las funciones están validadas dentro de las notebooks.
> Son mejoras de robustez (IC) y de organización del código (`src/`), no correcciones de fondo.

---

## 👥 Integrantes — Grupo 6
Erlij, Ian · Hussey, Juan Martín · Falaq, Manuel · Lachter, Federico
