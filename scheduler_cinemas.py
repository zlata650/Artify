#!/usr/bin/env python3
"""
Planificateur pour la mise à jour quotidienne des affiches de cinéma.
Lance le scraping tous les jours à une heure définie.
"""

import schedule
import time
import subprocess
import sys
from datetime import datetime
import os

# Chemin du script de scraping
SCRIPT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scrape_paris_cinemas.py')
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scraping_log.txt')


def log_message(message):
    """Enregistre un message dans le fichier de log."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry + '\n')


def run_scraping():
    """Exécute le script de scraping des cinémas."""
    log_message("🎬 Début de la mise à jour des affiches de cinéma...")
    
    try:
        # Exécuter le script de scraping
        result = subprocess.run(
            [sys.executable, SCRIPT_PATH],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes max
        )
        
        if result.returncode == 0:
            log_message("✅ Mise à jour terminée avec succès!")
            # Extraire les stats du output
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Cinémas de Paris:' in line or 'Films dans la base:' in line or 'Total' in line:
                    log_message(f"   {line.strip()}")
        else:
            log_message(f"❌ Erreur lors du scraping: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        log_message("⏱️ Timeout: Le scraping a pris trop de temps")
    except Exception as e:
        log_message(f"❌ Exception: {str(e)}")


def main():
    """Point d'entrée principal du planificateur."""
    print("=" * 60)
    print("🎬 PLANIFICATEUR DE MISE À JOUR - CINÉMAS DE PARIS")
    print("=" * 60)
    print(f"\n📅 Démarré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Script: {SCRIPT_PATH}")
    print(f"📝 Log: {LOG_FILE}")
    
    # Planifier les mises à jour
    # Mise à jour tous les jours à 6h00 du matin
    schedule.every().day.at("06:00").do(run_scraping)
    
    # Mise à jour supplémentaire à 18h00 pour avoir les dernières sorties
    schedule.every().day.at("18:00").do(run_scraping)
    
    print("\n⏰ Planification:")
    print("   • Tous les jours à 06:00")
    print("   • Tous les jours à 18:00")
    
    # Exécuter immédiatement au démarrage
    print("\n🚀 Exécution initiale...")
    run_scraping()
    
    print("\n🔄 En attente des prochaines mises à jour...")
    print("   (Ctrl+C pour arrêter)\n")
    
    log_message("🚀 Planificateur démarré")
    
    # Boucle principale
    while True:
        schedule.run_pending()
        time.sleep(60)  # Vérifier toutes les minutes


if __name__ == "__main__":
    main()


