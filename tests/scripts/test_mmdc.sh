#!/bin/bash

INPUT_FILE=""
OUTPUT_FILE=""
PARAM_FILE=""
CSS_FILE=""

while [[ $# -gt 0 ]]; do
 case "$1" in
  -i)
   INPUT_FILE="$2"
   shift 2
   ;;
  -o)
   OUTPUT_FILE="$2"
   shift 2
   ;;
  -p)
   PARAM_FILE="$2"
   shift 2
   ;;
  --cssFile)
   CSS_FILE="$2"
   shift 2
   ;;
  *)
   echo "Usage: $0 -i <input_file> -o <output_file> -p <param> [--cssFile <css_file>]"
   exit 1
   ;;
 esac
done

if [[ -z "$INPUT_FILE" || -z "$OUTPUT_FILE" || -z "$PARAM_FILE" ]]; then
  echo "Error: all parameters -i, -o, -p are required"
  exit 1
fi

MMD=$(< "$INPUT_FILE")
CSS=$(< "$CSS_FILE")

cat <<EOF > "$OUTPUT_FILE"
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
  <circle cx="50" cy="50" r="40" stroke="black" stroke-width="2" fill="red" />
  $CSS
</svg>
EOF

exit 0
