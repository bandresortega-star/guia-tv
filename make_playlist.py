#!/usr/bin/env python3
"""Crea tu lista con los identificadores de guía. Uso:
   python3 make_playlist.py <lista-original.m3u8> <URL-de-la-guia> [salida.m3u8]
Se ejecuta SOLO en tu equipo: la lista (con las direcciones del operador) NO se publica."""
import csv, sys, re
orig, url = sys.argv[1], sys.argv[2]
salida = sys.argv[3] if len(sys.argv) > 3 else "lista-con-epg.m3u8"
ids = [r for r in csv.DictReader(open("canales.csv", encoding="utf-8"))]
lineas = open(orig, encoding="utf-8", errors="replace").read().splitlines()
out, i = [f'#EXTM3U url-tvg="{url}" x-tvg-url="{url}"'], 0
for l in lineas:
    if l.startswith("#EXTINF"):
        c = ids[i]; i += 1
        nombre = c["nombre"]
        out.append(f'#EXTINF:-1 tvg-id="{c["tvg_id"]}" tvg-name="{nombre}" group-title="-",{nombre}')
    elif l and not l.startswith("#"):
        out.append(l)
assert i == len(ids), f"la lista tiene {i} canales y canales.csv {len(ids)}"
open(salida, "w", encoding="utf-8").write("\n".join(out) + "\n")
print(f"{i} canales escritos en {salida}")
