"""Regenera los CSV del dashboard a partir de PRIORIZACION.xlsx y ESTRATEGIAS.xlsx."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PRI = ROOT / "PRIORIZACION.xlsx"
EST = ROOT / "ESTRATEGIAS.xlsx"


def money(v):
    if pd.isna(v):
        return None
    s = str(v).replace("$", "").replace(",", "").replace(".", "").strip()
    try:
        return int(float(s))
    except ValueError:
        return None


def level(row, columns):
    for i, col in enumerate(columns, start=1):
        if pd.notna(row[col]) and str(row[col]).strip().upper() == "X":
            return i
    return None


def main():
    if not PRI.exists() or not EST.exists():
        raise FileNotFoundError("Coloca PRIORIZACION.xlsx y ESTRATEGIAS.xlsx en la raíz del repositorio.")
    DATA.mkdir(exist_ok=True)

    a = pd.read_excel(PRI, sheet_name="APRESTAMIENTO", header=1)
    a["Interes_Nivel"] = a.apply(lambda r: level(r, list(a.columns[2:7])), axis=1)
    a["Influencia_Nivel"] = a.apply(lambda r: level(r, list(a.columns[7:12])), axis=1)
    a = a.rename(columns={
        "Actor / Grupo de Interés":"Actor", "Categoría":"Categoria",
        "Cuadrante de la Matriz":"Cuadrante",
        "Rol / Acciones en la Fase de Aprestamiento":"Involucramiento",
        "Estrategia de Involucramiento":"Estrategia",
    })
    a[["Actor","Categoria","Interes_Nivel","Influencia_Nivel","Cuadrante","Involucramiento","Estrategia"]].to_csv(DATA/"actores_aprestamiento.csv", index=False, encoding="utf-8-sig")

    s = pd.read_excel(EST, sheet_name="APRESTAMIENTO", header=3).dropna(subset=["SESIÓN"]).copy()
    s["Presupuesto_Num"] = s["PRESUPUESTO"].apply(money)
    s.to_csv(DATA/"estrategias_aprestamiento.csv", index=False, encoding="utf-8-sig")

    annual = pd.read_excel(EST, sheet_name="RESUMEN ANUAL", header=3).iloc[:5].copy()
    annual["Presupuesto_Num"] = annual["PRESUPUESTO"].apply(money)
    annual.to_csv(DATA/"resumen_anual.csv", index=False, encoding="utf-8-sig")

    print("Datos actualizados.")


if __name__ == "__main__":
    main()
