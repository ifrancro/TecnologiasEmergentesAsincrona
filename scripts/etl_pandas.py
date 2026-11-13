#!/usr/bin/env python3
# etl_pandas.py - ETL y metricas Caso A con Pandas
import sys
import pandas as pd

archivo_entrada = sys.argv[1] if len(sys.argv) > 1 else "datos/raw_caso.tsv"
modo_escalabilidad = len(sys.argv) > 1

# 1. Extraer como texto puro
df = pd.read_csv(archivo_entrada, sep="\t", dtype=str, keep_default_na=False)
total_inicial = len(df)

if not modo_escalabilidad:
    print("=== PERFILADO INICIAL ===")
    print(f"Filas: {df.shape[0]}, Columnas: {df.shape[1]}")
    print("Vacios por columna:\n", (df == "").sum())
    print("Duplicados exactos:", df.duplicated().sum())

# 2. Transformar y contabilizar reglas
# Regla R1: Eliminar duplicados exactos (si no es el experimento xN)
if not modo_escalabilidad:
    antes = len(df)
    df = df.drop_duplicates()
    print(f"R1 (Duplicados eliminados): {antes - len(df)} filas afectadas")

# Regla R2: Conversion de tipos numericos y descarte de nulos en variables criticas
cols_num = ["temp_max", "temp_min", "precipitacion", "viento_max"]
for c in cols_num:
    df[c] = pd.to_numeric(df[c], errors="coerce")

antes = len(df)
df = df.dropna(subset=["ciudad", "fecha", "temp_max", "temp_min", "precipitacion"])
r2_afectadas = antes - len(df)

# Regla R3: Validaciones logicas (temp_min <= temp_max y precipitacion >= 0)
antes = len(df)
df = df[(df["temp_min"] <= df["temp_max"]) & (df["precipitacion"] >= 0)]
r3_afectadas = antes - len(df)

# Regla R4: Parseo de fechas y columnas derivadas (anio, mes, estacion)
df["fecha_dt"] = pd.to_datetime(df["fecha"], format="%Y-%m-%d", errors="coerce")
antes = len(df)
df = df.dropna(subset=["fecha_dt"])
r4_afectadas = antes - len(df)

df["anio"] = df["fecha_dt"].dt.year
df["mes"] = df["fecha_dt"].dt.month
# Estacion en Bolivia: Lluviosa (nov-mar: 11,12,1,2,3), Seca (abr-oct: 4..10)
df["estacion"] = df["mes"].apply(lambda m: "Lluviosa" if m in [11, 12, 1, 2, 3] else "Seca")

if not modo_escalabilidad:
    print(f"R2 (Nulos descartados): {r2_afectadas} filas")
    print(f"R3 (Rango invalido Tmin>Tmax o Prec<0): {r3_afectadas} filas")
    print(f"R4 (Fecha invalida): {r4_afectadas} filas")
    print(f"Total filas limpias: {len(df)} (Descartadas: {total_inicial - len(df)})")
    print("Rangos numericos limpios:\n", df[cols_num].describe().loc[["min", "max"]])

# 3. Calcular Metricas
# M1: Precipitacion total anual por ciudad
m1 = df.groupby(["ciudad", "anio"], as_index=False)["precipitacion"].sum()
m1["precipitacion"] = m1["precipitacion"].round(2)
m1["metrica"] = "M1_precipitacion_anual"

if modo_escalabilidad:
    print("M1 calculado para escalabilidad. Filas procesadas:", len(df))
    print(m1.head())
    sys.exit(0)

# M2: Temperatura maxima promedio por ciudad y mes (1 a 12)
m2 = df.groupby(["ciudad", "mes"], as_index=False)["temp_max"].mean()
m2["temp_max"] = m2["temp_max"].round(2)
m2["metrica"] = "M2_temp_max_prom_mensual"

# M3: Dias con helada (temp_min < 0) por ciudad y anio
heladas = df[df["temp_min"] < 0]
m3 = heladas.groupby(["ciudad", "anio"], as_index=False).size().rename(columns={"size": "dias_helada"})
# Asegurar que aparezcan ciudades/anios con 0 heladas si se desea comparar con COUNT
m3["metrica"] = "M3_dias_helada"

# 4. Guardar salidas
df.drop(columns=["fecha_dt"]).to_csv("datos/clean.csv", index=False)

# Guardar resultados unificados y separados para facilitar el dashboard
m1.to_csv("datos/resultados_pandas_m1.csv", index=False)
m2.to_csv("datos/resultados_pandas_m2.csv", index=False)
m3.to_csv("datos/resultados_pandas_m3.csv", index=False)

res_total = pd.concat([
    m1.rename(columns={"anio": "periodo", "precipitacion": "valor"})[["metrica", "ciudad", "periodo", "valor"]],
    m2.rename(columns={"mes": "periodo", "temp_max": "valor"})[["metrica", "ciudad", "periodo", "valor"]],
    m3.rename(columns={"anio": "periodo", "dias_helada": "valor"})[["metrica", "ciudad", "periodo", "valor"]]
])
res_total.to_csv("datos/resultados_pandas.csv", index=False)
print("Archivos guardados en datos/clean.csv y datos/resultados_pandas.csv")