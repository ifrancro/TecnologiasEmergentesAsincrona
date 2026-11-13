#!/usr/bin/env python3
# mapper_m2.py - Emite ciudad|mes <TAB> temp_max
import sys

for linea in sys.stdin:
    campos = linea.rstrip("\n").split("\t")
    if len(campos) < 5 or campos[0] == "ciudad":
        continue
    try:
        ciudad = campos[0].strip()
        fecha = campos[1].strip()
        mes = int(fecha.split("-")[1])
        tmax = float(campos[2])
        tmin = float(campos[3])
        prec = float(campos[4])
        if tmin > tmax or prec < 0:
            continue
        clave = "{}|{:02d}".format(ciudad, mes)
        print("{}\t{}".format(clave, tmax))
    except (IndexError, ValueError):
        continue