#!/usr/bin/env bash
# Envuelve un archivo de texto en una página HTML estilo terminal para capturarla.
# Uso: make.sh <titulo> <archivo.txt> <salida.html>
set -euo pipefail
dir="$(dirname "$0")"
title="$1"; src="$2"; out="$3"
esc=$(sed -e 's/&/\&amp;/g' -e 's/</\&lt;/g' -e 's/>/\&gt;/g' "$src")
cat > "$out" <<HTML
<!doctype html><html lang="es"><head><meta charset="utf-8">
<style>
  :root{color-scheme:dark}
  body{margin:0;background:#0b0f17;font-family:'Cascadia Code','Consolas',monospace}
  .win{max-width:980px;margin:0 auto}
  .bar{background:#1f2430;color:#cbd5e1;padding:8px 14px;border-radius:10px 10px 0 0;font-size:13px;display:flex;align-items:center;gap:8px}
  .dot{width:11px;height:11px;border-radius:50%;display:inline-block}
  .pre{background:#0b0f17;color:#d6deeb;padding:16px 18px;border:1px solid #1f2430;border-top:0;border-radius:0 0 10px 10px;white-space:pre-wrap;font-size:13px;line-height:1.5}
  .pre b{color:#7fdbca}
</style></head><body><div class="win">
<div class="bar"><span class="dot" style="background:#ff5f56"></span><span class="dot" style="background:#ffbd2e"></span><span class="dot" style="background:#27c93f"></span>&nbsp; $title</div>
<div class="pre">$esc</div></div></body></html>
HTML
echo "$out"
