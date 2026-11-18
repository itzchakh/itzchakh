#!/bin/bash
# Generates the reference sheets in dependency order. Usage: ./generate_refs.sh [KEY ...]
set -e
cd "$(dirname "$0")"
mkdir -p refs_generated prompts_tmp
STYLE_REF=refs_generated/REF_king.png
gen() { # key aspect refs...
  local key=$1 aspect=$2; shift 2
  python3 -c "import json;print(json.load(open('ref_prompts.json'))['$key'])" > prompts_tmp/$key.txt
  local args=(); for r in "$@"; do [ -f "$r" ] && args+=(--ref "$r"); done
  python3 gemini.py image --prompt-file prompts_tmp/$key.txt "${args[@]}" --aspect "$aspect" --out refs_generated/$key.png
}
KEYS=("$@")
run() { local k=$1; if [ ${#KEYS[@]} -eq 0 ] || [[ " ${KEYS[*]} " == *" $k "* ]]; then gen "$@"; fi; }
run REF_king 16:9
run REF_prince 16:9 $STYLE_REF
run REF_doctor_counselor 16:9 $STYLE_REF
run REF_alter_rebbe 16:9 ../refs/alter_rebbe_traditional_chabadpedia.jpg $STYLE_REF
run REF_lineup 16:9 refs_generated/REF_doctor_counselor.png refs_generated/REF_prince.png $STYLE_REF
run REF_props 16:9 $STYLE_REF
run REF_music 16:9 $STYLE_REF
for L in L1 L2 L3 L4 L5 L6 L7 L8 L9; do run LOC_$L 16:9 $STYLE_REF; done
