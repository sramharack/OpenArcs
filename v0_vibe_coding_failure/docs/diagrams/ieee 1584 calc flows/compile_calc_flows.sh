#!/bin/bash
# compile_all_diagrams.sh

for i in {1..5}; do
  case $i in
    1) name="model_overview" ;;
    2) name="analysis_process" ;;
    3) name="dc_calculations" ;;
    4) name="configuration_selection" ;;
    5) name="special_cases" ;;
  esac
  
  echo "Compiling diagram${i}_${name}.d2..."
  d2 --theme=300 diagram${i}_${name}.d2 diagram${i}_${name}.svg
  d2 --theme=300 diagram${i}_${name}.d2 diagram${i}_${name}.pdf
done

echo "All diagrams compiled!"