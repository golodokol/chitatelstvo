#!/bin/bash
cd /var/www/chitatelstvo-assets || exit 1
for f in *; do
  nf=$(echo "$f" | tr '[:upper:]' '[:lower:]')
  if [ "$f" != "$nf" ]; then mv "$f" "$nf"; fi
done
ls | wc -l
