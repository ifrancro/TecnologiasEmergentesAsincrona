#!/usr/bin/env python3
# mapper_m1.py - Emite ciudad|anio <TAB> precipitacion
import sys

for linea in sys.stdin:
    campos = linea.rstrip("\n").split("\t")
    if len(campos) < 5 or campos[0] == "ciudad":
        continue
    try:
        ciudad = campos[0].strip()
        fecha = campos[1].strip()
        anio = fecha.split("-")[0]
        tmax = float(campos[2])
        tmin = float(campos[3])
        prec = float(campos[4])
        # Misma regla de limpieza que Pandas
        if tmin > tmax or prec < 0:
            continue
        clave = "{}|{}".format(ciudad, anio)
        print("{}\t{}".format(clave, prec))
    except (IndexError, ValueError):
        continue