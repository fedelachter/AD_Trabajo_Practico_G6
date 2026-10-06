# Inteligencia de Mercado Inmobiliario — CABA
### TP Integrador · Analítica Descriptiva · Grupo 6 (PropTech)

Sistema de análisis del mercado inmobiliario de la Ciudad de Buenos Aires orientado
a detectar propiedades y barrios subvaluados y a recomendar, para cada oportunidad,
la estrategia de salida óptima (reventa o renta). Este repositorio contiene la
construcción y consolidación de la base de datos (Fase 1 / Raw Data).

---

## 📁 Estructura del repositorio
AD_Trabajo_Practico_G6/
├── data/raw/                        # Datasets crudos extraídos (Raw Data)
│   ├── argenprop_departamentos_caba.csv
│   ├── mercadolibre_alquiler_caba.csv
│   └── mercadolibre_venta_caba.csv
├── scrapers/                        # Scripts de extracción de cada fuente
│   ├── scraper_argenprop.py
│   ├── scraper_ml_venta.py
│   └── scraper_ml_alquiler.py
├── extraccion_datos.ipynb           # Notebook de carga, inspección y consolidación
├── entrega1_contexto_negocio.pdf    # Documento de contexto, hipótesis y KPIs
└── README.md

---

## 🗂️ Fuentes de datos

| Fuente | Operación | Registros | Técnica de extracción |
|---|---|---|---|
| MercadoLibre Inmuebles | Venta (usados + emprendimientos) | ~45.568 | Scraping HTML (Playwright / requests) |
| MercadoLibre Inmuebles | Alquiler | ~10.166 | Scraping HTML segmentado por barrio |
| Argenprop | Alquiler | ~1.000 | Scraping HTML (script base mejorado) |

Cada registro incluye: identificador, título, operación, tipo de propiedad, precio,
moneda, superficie, ambientes, baños, dirección, barrio y ciudad.

---

## ⚙️ Dependencias

Los scripts y la notebook requieren Python 3.10+ y las siguientes librerías:

```bash
pip install pandas requests beautifulsoup4 playwright curl_cffi
playwright install chromium   # solo para el scraper de MercadoLibre
```

---

## ▶️ Orden de ejecución

1. **Extracción (local).** Ejecutar los scripts de la carpeta `scrapers/`. Cada uno
   genera su CSV correspondiente en `data/raw/`. La extracción se realizó localmente
   (no en Colab) por requerir un navegador real para sortear la protección anti-bot.
2. **Carga y consolidación.** Abrir `extraccion_datos.ipynb` (en Colab o local), que
   levanta los tres CSV desde el repositorio, los inspecciona y los deja listos para
   el análisis.

---

## 📤 Outputs generados

- Tres datasets crudos en `data/raw/` (uno por fuente).
- Dataframes maestros consolidados en la notebook, con tipos de datos validados
  (numéricos, ordinales, textuales y dicotómicos) y dirección normalizada.

---

## ⚠️ Limitaciones conocidas

- **Corte temporal único:** los datos corresponden a un único momento de extracción,
  por lo que no permiten analizar evolución de precios ni valorización futura.
- **Estado de la propiedad no observable:** no se dispone del estado de conservación
  ni de características cualitativas (viven en descripciones/fotos no relevadas), lo
  que limita distinguir una subvaluación real de un descuento justificado.
- **Argenprop:** fuente de menor volumen y calidad; la columna `link` no se capturó
  y presenta más datos faltantes que las fuentes de MercadoLibre.
- **API de MercadoLibre:** se evaluó y descartó por restringir el acceso a datos de
  terceros; se optó por scraping del HTML público.

---

## 👥 Integrantes — Grupo 6
Federico · Ian · Juan Martín · Manuel 
