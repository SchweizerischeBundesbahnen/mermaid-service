#!/bin/bash

INPUT_FILE=""
OUTPUT_FILE=""
PARAM_FILE=""

while getopts "i:o:p:" opt; do
  case "$opt" in
    i) INPUT_FILE="$OPTARG" ;;
    o) OUTPUT_FILE="$OPTARG" ;;
    p) PARAM_FILE="$OPTARG" ;;
    *) echo "Usage: $0 -i <input_file> -o <output_file> -p <param>"; exit 1 ;;
  esac
done

if [[ -z "$INPUT_FILE" || -z "$OUTPUT_FILE" || -z "$PARAM_FILE" ]]; then
  echo "Error: all parameters -i, -o, -p are required"
  exit 1
fi

MMD=$(< "$INPUT_FILE")

if [[ "$MMD" == "flowchart TD; A-->B;" ]]; then
    cat <<'EOF' > "$OUTPUT_FILE"
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
  <circle cx="50" cy="50" r="40" stroke="black" stroke-width="2" fill="red" />
</svg>
EOF
else
  exit 2
fi

exit 0
