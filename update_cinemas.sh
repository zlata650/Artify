#!/bin/bash
# Script de mise à jour des affiches de cinéma
# Peut être utilisé avec cron pour des mises à jour automatiques

cd /Users/zlatashvets/Artify
source venv/bin/activate

echo "$(date '+%Y-%m-%d %H:%M:%S') - Début de la mise à jour des cinémas" >> scraping_log.txt
python3 scrape_paris_cinemas.py >> scraping_log.txt 2>&1
echo "$(date '+%Y-%m-%d %H:%M:%S') - Mise à jour terminée" >> scraping_log.txt
echo "---" >> scraping_log.txt


