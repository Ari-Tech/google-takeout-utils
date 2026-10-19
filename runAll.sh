#!/bin/bash

for f in *.zip; do
    echo "Processing $f ..."
    python3 process_single_zip.py "$f"
done

