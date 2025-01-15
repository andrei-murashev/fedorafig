#!/bin/bash

function len_varied_combs() {
  local INPUT=("$@")
  local OUTPUT=()

  if [ "${#INPUT[@]}" -eq 0 ]; then
    echo "Input array is empty."
    return
  fi

  local COUNT=0
  for LEN in $( seq 1 "${#INPUT[@]}" ); do
    for IDX in "${!INPUT[@]}"; do
      COMB=$(wrapped_slice "${INPUT[@]}" "$IDX" "$LEN")
      OUTPUT[$COUNT]="$COMB"; ((COUNT++))
    done
  done

  printf '%s' "$(IFS=' '; echo ${OUTPUT[*]})"
}

function wrapped_slice() {
  local INPUT=("$@")
  local ARR=("${INPUT[@]:0:$(( ${#INPUT[@]} - 2 ))}") # Array
  local START_IDX="${INPUT[-2]}" # Slice start index
  local LEN="${INPUT[-1]}" # Slice Length

  if [ $(( START_IDX + LEN )) -ge ${#ARR[@]} ]; then
    DIFF=$(( LEN - (${#ARR[@]} - START_IDX) ))
    OUTPUT=("${ARR[@]:START_IDX}" "${ARR[@]:0:DIFF}")
    printf "'%s'" "${OUTPUT[*]}"
  else
    OUTPUT=("${ARR[@]:START_IDX:LEN}")
    printf "'%s'" "${OUTPUT[*]}"
  fi
}

NUMS=($(ls -lah ~/.config/fedorafig/ | grep -e cfg* | awk '{print $NF}' \
    | cut -f1 -d '.' | cut -f2 -d '_' | tr '\n' ' '))

set -e; for NUM in ${NUMS[@]}; do
  FLAG_STRS=$(len_varied_combs '-h' '-k' '-c' '-s' '-n' | grep -o "'[^']*'")
  while IFS= read -r FLAG_STR; do
    FLAG_STR=$(echo "$FLAG_STR" | sed "s/^'\(.*\)'$/\1/")
    if ! ( [[ "$FLAG_STR" == *"-n"* ]] && ( [[ "$FLAG_STR" == *'-c'* ]] || \
      [[ "$FLAG_STR" == *'-s'* ]] )); then
        fedorafig check cfg_"$NUM".json5 "$FLAG_STR"
    fi
  done <<< "$FLAG_STRS"

  : "
  COMBS=(); for FLAG_STR in "${FLAGS[@]}"; do
    #if ! ( [[ "$FLAG_STR" == *"-n"* ]] && ( [[ "FLAG_STR" == *'-c'* ]] || \
    #  [[ "FLAG_STR" == *'-s'* ]] )); then
        echo $FLAG_STR
    #fi
  done
  "
  : "
  for OPTION in $COMBS; do
    fedorafig check $OPTION cfg_$NUM.json5
  done

  COMBS=()
  for OPTIONS in $COMBS; do
    sudo fedorafig run $OPTIONS cfg_$NUM.json5
  done;
  "
done

: "
fedorafig base 
sudo fedorafig base 

fedorafig exec exec1.sh exec2.sh exec3.sh
sudo fedorafig exec

yes | fedorafig uninstall -c -s
if [ -d ~/.config/fedorafig/ ]      || \
   [ -d ~/.local/lib/fedorafig/ ]   || \
   [ -d ~/.local/state/fedorafig/ ]
then exit 1; fi
"

#len_varied_combs '-h' '-k' '-c' '-s' '-n'
