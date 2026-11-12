#!/bin/bash
# Usage: ./autoscroll.sh [scroll_px=300] [pause_sec=1.5] [change_pct=20] [pokemon_count=9999]
D=${1:-300}; P=${2:-1.5}; T=${3:-20}; N=${4:-9999}
echo "Hover over the middle of the Pokédex entry. Starting in 5s (Ctrl+C to stop)..."
sleep 5
IFS=, read X Y <<< "$(cliclick p | grep -oE '[0-9]+,[0-9]+')"
snap() { screencapture -x -R$((X-100)),$((Y-150)),200,300 "$1"; }
# Counts as moved only if more than T% of pixels changed, so small animations are ignored
moved() {
  local n=$(magick identify -format '%[fx:w*h]' /tmp/a.png)
  magick compare -metric AE -fuzz 15% /tmp/a.png /tmp/b.png null: 2>&1 | awk -v n=$n -v t=$T '{exit !($1 > n*t/100)}'
}
# drag(dx, dy, fast): swipe centered on the hover point; fails if the view didn't move (hit the end)
drag() {
  local x=$((X-($1)/2)) y=$((Y-($2)/2)) w=30 h=w:150
  [ "$3" ] && w=5 h=   # fast flick: quick moves, release without stopping
  snap /tmp/a.png
  cliclick -w $w dd:$x,$y $(for s in {1..10}; do echo dm:$((x+$1*s/10)),$((y+$2*s/10)); done) $h du:$((x+$1)),$((y+$2)) m:$X,$Y
  sleep $P; snap /tmp/b.png; moved
}
for ((i=1; i<=N; i++)); do
  echo "Pokémon $i"
  #while drag 0 $D fast; do :; done   # your order: flick down first
  while drag 0 -$D fast; do :; done   # then flick up
  drag -260 0 fast                       # swipe left to the next Pokémon (always, no end check)
done
echo "Done."
