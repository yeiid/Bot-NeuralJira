import os
import time
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from orchestrator import MarketingOrchestrator
from dotenv import load_dotenv

# Cargar entorno
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Scheduler")

class MarketingScheduler:
    """
    Automatización Temporal (Cron) para NeuralJira.
    Define cuándo Galldroko debe despertar y publicar.
    """
    
    def __init__(self):
        self.orchestrator = MarketingOrchestrator()
        self.scheduler = BlockingScheduler()

    def start(self):
        # 1. Noticias Tech - Lunes a Viernes a las 10:00 AM
        self.scheduler.add_job(
            self.orchestrator.run_news_cycle,
            CronTrigger(day_of_week='mon-fri', hour=10, minute=0),
            name="Publicación de Noticias Matutinas"
        )
        
        # 2. Tip de Programación - Miércoles a las 3:00 PM
        self.scheduler.add_job(
            lambda: self.orchestrator.run_tutorial_cycle("Python avanzado y automatización"),
            CronTrigger(day_of_week='wed', hour=15, minute=0),
            name="Tutorial Semanal"
        )
        
        # 3. Resumen de fin de semana - Domingo a las 11:00 AM
        self.scheduler.add_job(
            self.orchestrator.run_news_cycle,
            CronTrigger(day_of_week='sun', hour=11, minute=0),
            name="Resumen Dominical"
        )

        logger.info("📅 Scheduler configurado y activo.")
        logger.info("Próximas tareas programadas:")
        for job in self.scheduler.get_jobs():
            logger.info(f" - {job.name}: Próxima ejecución: {job.next_run_time}")
            
        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Scheduler detenido.")

if __name__ == "__main__":
    # Evitar arranques accidentales sin API Keys
    if not os.getenv("ANTHROPIC_API_KEY") or not os.getenv("FACEBOOK_ACCESS_TOKEN"):
        logger.error("❌ ERROR: Faltan llaves de API en .env. No se puede iniciar el scheduler.")
    else:
        sched = MarketingScheduler()
        sched.start()
