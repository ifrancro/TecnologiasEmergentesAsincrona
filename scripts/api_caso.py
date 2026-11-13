#!/usr/bin/env python3
# api_caso.py - Ingesta Caso A: Clima de ciudades bolivianas (Open-Meteo)
import json
import os
import time
import requests

AGENTE = "TEM1T6-UNIVALLE-GrupoA-RomeroIan (fines academicos)"
PAUSA = 1.0
CARPETA_JSON = "datos/raw_json"
SALIDA = "datos/raw_caso.tsv"
CABECERA = [
    "ciudad", "fecha", "temp_max", "temp_min", 
    "precipitacion", "viento_max"
]

URL_BASE = "https://archive-api.open-meteo.com/v1/archive"

CIUDADES = [
    ("Santa_Cruz_de_la_Sierra", -17.78, -63.18),
    ("La_Paz", -16.50, -68.15),
    ("Cochabamba", -17.39, -66.16),
    ("Tarija", -21.53, -64.73),
    ("Trinidad", -14.83, -64.90)
]


def pedir(url, params, intentos=4):
    """GET con pausa y reintentos ante 429 o errores 5xx (espera 2, 4, 8... s)."""
    for i in range(intentos):
        r = requests.get(url, params=params, headers={"User-Agent": AGENTE}, timeout=60)
        time.sleep(PAUSA)
        if r.status_code == 200:
            return r.json()
        if r.status_code in (429, 500, 502, 503, 504):
            espera = 2 ** (i + 1)
            print("HTTP", r.status_code, "- reintento en", espera, "s")
            time.sleep(espera)
            continue
        r.raise_for_status()
    raise SystemExit("La API no respondio tras varios intentos: " + r.url)


def solicitudes():
    """Genera 50 solicitudes: 5 ciudades x 10 anios (2015 a 2024)."""
    lista = []
    for ciudad, lat, lon in CIUDADES:
        for anio in range(2015, 2025):
            nombre = f"{ciudad}_{anio}"
            params = {
                "latitude": lat,
                "longitude": lon,
                "start_date": f"{anio}-01-01",
                "end_date": f"{anio}-12-31",
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
                "timezone": "America/La_Paz"
            }
            lista.append((nombre, URL_BASE, params))
    return lista


def aplanar(nombre, datos):
    """Convierte UNA respuesta JSON en filas SIN limpiar los valores."""
    filas = []
    # Extraer el nombre de la ciudad quitando el '_anio' del final
    ciudad = "_".join(nombre.split("_")[:-1]).replace("_", " ")
    daily = datos.get("daily", {})
    fechas = daily.get("time", [])
    tmax = daily.get("temperature_2m_max", [])
    tmin = daily.get("temperature_2m_min", [])
    prec = daily.get("precipitation_sum", [])
    viento = daily.get("wind_speed_10m_max", [])

    for i, fecha in enumerate(fechas):
        filas.append([
            ciudad,
            fecha,
            tmax[i] if i < len(tmax) else None,
            tmin[i] if i < len(tmin) else None,
            prec[i] if i < len(prec) else None,
            viento[i] if i < len(viento) else None
        ])
    return filas


def texto(valor):
    """None -> vacio; quita TAB y saltos de linea para que el TSV no se rompa."""
    return "" if valor is None else " ".join(str(valor).split())


os.makedirs(CARPETA_JSON, exist_ok=True)
todas = []
for nombre, url, params in solicitudes():
    datos = pedir(url, params)
    with open(os.path.join(CARPETA_JSON, nombre + ".json"), "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False)
    filas = aplanar(nombre, datos)
    todas.extend(filas)
    print(nombre, "->", len(filas), "filas (total:", len(todas), ")")

with open(SALIDA, "w", encoding="utf-8") as f:
    f.write("\t".join(CABECERA) + "\n")
    for fila in todas:
        f.write("\t".join(texto(v) for v in fila) + "\n")
print("Listo:", len(todas), "filas en", SALIDA)