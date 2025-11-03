"""
Bot Manager - Automatický restart při pádu a daily restart
Spouští Discord bota a sleduje jeho běh.
"""
import subprocess
import time
import sys
import logging
from datetime import datetime, timedelta
import os

# Nastavení logování
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/manager.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('bot_manager')


class BotManager:
    """Správce bota - sleduje běh a restartuje při pádu"""
    
    def __init__(self):
        self.process = None
        self.last_restart = datetime.now()
        self.restart_count = 0
        self.daily_restart_hour = 4  # Restart ve 4:00 ráno
        self.daily_restart_minute = 0
        
    def start_bot(self):
        """Spustí Discord bota"""
        if self.process:
            logger.info("⏹️ Ukončujem starý proces bota...")
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logger.warning("⚠️ Proces neodpovídá, nuceně ukončuji...")
                self.process.kill()
        
        logger.info("🚀 Spouštím Discord bota...")
        
        # Aktivace venv a spuštění bota
        if os.name == 'nt':  # Windows
            python_path = os.path.join('venv', 'Scripts', 'python.exe')
        else:  # Linux/Mac
            python_path = os.path.join('venv', 'bin', 'python')
        
        self.process = subprocess.Popen(
            [python_path, 'bot.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.getcwd()
        )
        
        self.last_restart = datetime.now()
        self.restart_count += 1
        
        logger.info(f"✅ Bot spuštěn (PID: {self.process.pid}, restart #{self.restart_count})")
    
    def is_bot_running(self):
        """Zkontroluje zda bot běží"""
        if not self.process:
            return False
        
        return_code = self.process.poll()
        return return_code is None
    
    def should_daily_restart(self):
        """Zkontroluje zda je čas na daily restart"""
        now = datetime.now()
        
        # Čas posledního daily restartu (dnes ve stanovenou hodinu)
        restart_time_today = now.replace(
            hour=self.daily_restart_hour,
            minute=self.daily_restart_minute,
            second=0,
            microsecond=0
        )
        
        # Pokud jsme už prošli časem restartu dnes a poslední restart byl před tím
        if now >= restart_time_today and self.last_restart < restart_time_today:
            return True
        
        return False
    
    def run(self):
        """Hlavní smyčka manageru"""
        logger.info("=" * 60)
        logger.info("🎮 Bot Manager spuštěn")
        logger.info(f"📅 Daily restart nastaven na: {self.daily_restart_hour:02d}:{self.daily_restart_minute:02d}")
        logger.info("=" * 60)
        
        self.start_bot()
        
        try:
            while True:
                time.sleep(30)  # Kontrola každých 30 sekund
                
                # Kontrola zda bot běží
                if not self.is_bot_running():
                    return_code = self.process.returncode
                    logger.error(f"❌ Bot spadl! (exit code: {return_code})")
                    logger.info("🔄 Restartuji za 5 sekund...")
                    time.sleep(5)
                    self.start_bot()
                    continue
                
                # Kontrola daily restart
                if self.should_daily_restart():
                    logger.info("🕐 Čas na denní restart!")
                    self.start_bot()
                    continue
                
                # Informační log každých 30 minut
                uptime = datetime.now() - self.last_restart
                if int(uptime.total_seconds()) % 1800 == 0:  # Každých 30 minut
                    logger.info(f"✅ Bot běží: {uptime} (PID: {self.process.pid})")
        
        except KeyboardInterrupt:
            logger.info("⚠️ Manager ukončen uživatelem (Ctrl+C)")
            if self.process:
                logger.info("⏹️ Ukončuji bota...")
                self.process.terminate()
                try:
                    self.process.wait(timeout=10)
                    logger.info("✅ Bot ukončen")
                except subprocess.TimeoutExpired:
                    logger.warning("⚠️ Nucené ukončení...")
                    self.process.kill()
        
        except Exception as e:
            logger.critical(f"💥 Kritická chyba v manageru: {e}", exc_info=True)
            if self.process:
                self.process.terminate()
            sys.exit(1)


if __name__ == "__main__":
    # Vytvoř logs složku pokud neexistuje
    os.makedirs('logs', exist_ok=True)
    
    manager = BotManager()
    manager.run()
