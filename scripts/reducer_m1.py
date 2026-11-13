    #!/usr/bin/env python3
# reducer_m1.py - Suma la precipitacion por ciudad|anio
import sys

clave_actual = None   
suma = 0.0

for linea in sys.stdin:
    partes = linea.rstrip("\n").split("\t")
    if len(partes) != 2:
        continue
    clave, valor = partes[0], float(partes[1])
    if clave == clave_actual:
        suma += valor
    else:
        if clave_actual is not None:
            print("{}\t{:.2f}".format(clave_actual, suma))
        clave_actual = clave
        suma = valor

if clave_actual is not None:
    print("{}\t{:.2f}".format(clave_actual, suma))