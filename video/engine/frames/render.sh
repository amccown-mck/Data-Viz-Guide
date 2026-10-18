#!/bin/zsh
# Render style frames to PNG: ./render.sh [file.html[:N] ...]   (no args = all)
cd "${0:A:h}"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
typeset -A SECS; SECS=(f01-hook 1 f02-montage 4 f03-consultant 2 f04-notebook 4 f05-agent 1)
targets=("$@"); [[ ${#targets} -eq 0 ]] && targets=(${(k)SECS})
for t in $targets; do
  base=${t%%:*}; base=${base%.html}; only=${t#*:}; [[ $only == $t ]] && only=""
  n=${SECS[$base]:-1}
  for ((i=1;i<=n;i++)); do
    [[ -n $only && $only != $i ]] && continue
    out="$PWD/png/${base}$([[ $n -gt 1 ]] && echo "-s$i").png"
    "$CHROME" --headless=new --disable-gpu --hide-scrollbars --allow-file-access-from-files \
      --window-size=1920,1080 --virtual-time-budget=3000 --screenshot="$out" \
      "file://$PWD/$base.html?s=$i&guides=${GUIDES:-1}" >/dev/null 2>&1
    echo "$out"
  done
done
