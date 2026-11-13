#!/usr/bin/env python3
# replicar.py - crea una version N veces mas grande de un TSV (para el experimento de escalabilidad)
# Uso:  python replicar.py datos/raw_caso.tsv datos/raw_caso_x10.tsv 10
import sys

entrada, salida, veces = sys.argv[1], sys.argv[2], int(sys.argv[3])
with open(entrada, encoding="utf-8") as f:
    cabecera = f.readline()
    cuerpo = f.read()
if cuerpo and not cuerpo.endswith("\n"):
    cuerpo += "\n"
with open(salida, "w", encoding="utf-8") as g:
    g.write(cabecera)
    for _ in range(veces):
        g.write(cuerpo)
print("Listo:", salida, "con", veces, "copias de los datos")
