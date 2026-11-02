#!/usr/bin/env python3
"""Arma docs/guide.xml: junta la guía descargada (guide-raw.xml) con marcadores
genéricos para los canales sin programación. Nunca deja un canal vacío."""
import csv, gzip, os, sys, datetime as dt
import xml.etree.ElementTree as ET

RAW = sys.argv[1] if len(sys.argv) > 1 else "guide-raw.xml"
OUT = sys.argv[2] if len(sys.argv) > 2 else "docs/guide.xml"
DIAS, BLOQUE_H = 7, 6
BOG = dt.timezone(dt.timedelta(hours=-5))          # Colombia, sin horario de verano

canales = list(csv.DictReader(open("canales.csv", encoding="utf-8")))
vistos, unicos = set(), []
for c in canales:                                   # un <channel> por tvg_id
    if c["tvg_id"] not in vistos:
        vistos.add(c["tvg_id"]); unicos.append(c)

reales = {}                                         # tvg_id -> [programme]
if os.path.exists(RAW):
    try:
        for p in ET.parse(RAW).getroot().findall("programme"):
            reales.setdefault(p.get("channel"), []).append(p)
    except ET.ParseError as e:
        print("AVISO: guide-raw.xml ilegible, todo irá con marcadores:", e)

tv = ET.Element("tv", {"generator-info-name": "guia-colombia"})
for c in unicos:
    ch = ET.SubElement(tv, "channel", {"id": c["tvg_id"]})
    ET.SubElement(ch, "display-name").text = c["nombre"]

fmt = lambda d: d.astimezone(dt.timezone.utc).strftime("%Y%m%d%H%M%S +0000")
hoy = dt.datetime.now(BOG).replace(hour=0, minute=0, second=0, microsecond=0)
con_real = con_marcador = 0
for c in unicos:
    progs = reales.get(c["tvg_id"], [])
    if progs:
        for p in progs: tv.append(p)
        con_real += 1
    else:
        for i in range(DIAS * 24 // BLOQUE_H):
            ini = hoy + dt.timedelta(hours=i * BLOQUE_H)
            p = ET.SubElement(tv, "programme", {"start": fmt(ini), "stop": fmt(ini + dt.timedelta(hours=BLOQUE_H)), "channel": c["tvg_id"]})
            ET.SubElement(p, "title", {"lang": "es"}).text = f"En vivo: {c['nombre']}"
            ET.SubElement(p, "desc", {"lang": "es"}).text = "Sin guía de programación disponible para este canal."
        con_marcador += 1

os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
ET.indent(tv)
ET.ElementTree(tv).write(OUT, encoding="utf-8", xml_declaration=True)
with open(OUT, "rb") as f, gzip.open(OUT + ".gz", "wb") as g: g.write(f.read())
print(f"canales: {len(unicos)} | con guía real: {con_real} | con marcador: {con_marcador} | {os.path.getsize(OUT)//1024} KB")
