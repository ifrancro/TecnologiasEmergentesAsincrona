#!/usr/bin/env python3
# combiner_m2.py - Agrega parcialmente suma;conteo por nodo local
import sys

clave_actual = None
suma = 0.0
conteo = 0

for linea in sys.stdin:
    partes = linea.rstrip("\n").split("\t")
    if len(partes) != 2:
        continue
    clave = partes[0]
    # Soporta recibir tanto un float directo como suma;conteo si el combiner se re-ejecuta
    if ";" in partes[1]:
        s, c = partes[1].split(";")
        val, cnt = float(s), int(c)
    else:
        val, cnt = float(partes[1]), 1

    if clave == clave_actual:
        suma += val
        conteo += cnt
    else:
        if clave_actual is not None:
            print("{}\t{};{}".format(clave_actual, suma, conteo))
        clave_actual = clave
        suma = val
        conteo = cnt

if clave_actual is not None:
    print("{}\t{};{}".format(clave_actual, suma, conteo))