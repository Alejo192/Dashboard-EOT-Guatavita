# Dashboard EOT Guatavita — Aprestamiento

Versión temática derivada del dashboard Streamlit original de priorización de leads.

## Contenido
- **Actores de Aprestamiento:** 96 actores tomados de `PRIORIZACION.xlsx`, con interés, influencia, cuadrante, rol y estrategia.
- **Interacción:** matriz Plotly con hover y selección por clic; tarjetas CSS con animación al pasar el cursor.
- **Presupuesto:** plan anual y detalle de las 10 sesiones del Aprestamiento de `ESTRATEGIAS.xlsx`.
- **Estrategias:** tarjetas interactivas por sesión.
- **Integraciones:** ArcGIS WebMap, Power BI, R/Shiny.
- **Asistente IA:** integración opcional con Gemini mediante `GEMINI_API_KEY`.

## Ejecutar localmente
```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
streamlit run app.py
```

## Actualizar los datos desde Excel
Coloca `PRIORIZACION.xlsx` y `ESTRATEGIAS.xlsx` en la raíz del proyecto y ejecuta:
```bash
python scripts/actualizar_datos.py
```

Los CSV generados son los que consume `app.py` en producción. Esto evita depender de Excel en cada arranque de Streamlit Cloud.

## Desplegar en Streamlit Community Cloud
1. Sube el repositorio a GitHub.
2. En Streamlit Community Cloud crea una app y selecciona el repositorio, rama y `app.py`.
3. Si activas IA, agrega `GEMINI_API_KEY` en Secrets; nunca lo subas a GitHub.

## Arquitectura recomendada
```text
Excel / Google Sheets
        ↓
 scripts/actualizar_datos.py
        ↓
      CSVs
        ↓
      app.py
   ┌────┼───────────────┐
   ↓    ↓       ↓       ↓
Actores Presup. Estrat. IA
   ↓
Integraciones → ArcGIS / Power BI / Shiny
```

## Qué herramienta usar para cada parte

- **VS Code + Claude/Kiro/Copilot:** edición del repositorio, refactor de `app.py`, CSS, pruebas y cambios rápidos.
- **GitHub:** versión del código y despliegue automático hacia Streamlit Community Cloud.
- **Streamlit:** aplicación web principal.
- **Plotly:** matriz de actores, gráficos de presupuesto, hover y selección por clic.
- **Power BI:** análisis BI más profundo; se puede enlazar/embeber de forma autenticada.
- **ArcGIS Pro + ArcGIS Online/Enterprise:** preparación y publicación de cartografía; el navegador consume el WebMap publicado.
- **RStudio/Shiny:** análisis estadístico especializado o aplicaciones R separadas que se pueden enlazar/embeber.
- **Gemini API:** asistente IA opcional dentro del dashboard para resúmenes y fichas basados en los datos visibles.
