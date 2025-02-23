import os
import subprocess
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class ScrapingScheduler:
    def __init__(self):
        self.task_name = "NewsScrapingJob"
        self.script_path = os.path.abspath("app/update_documents.py")

    def schedule_scraping(self, interval_minutes: int = 60):
        """
        Schedule periodic scraping job using Windows Task Scheduler
        """
        try:
            # Remove existing task if any
            subprocess.run(f'schtasks /delete /tn {self.task_name} /f', shell=True, capture_output=True)
            
            # Create a new task
            start_time = (datetime.now() + timedelta(minutes=1)).strftime("%H:%M")
            
            # Create the command
            cmd = (
                f'schtasks /create /tn {self.task_name} /tr "python {self.script_path}" '
                f'/sc minute /mo {interval_minutes} /st {start_time} /f'
            )
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"Scraping job scheduled successfully to run every {interval_minutes} minutes")
            else:
                print(f"Error creating task: {result.stderr}")
                
        except Exception as e:
            print(f"Error scheduling scraping job: {e}")

    def remove_schedule(self):
        """
        Remove scheduled job
        """
        try:
            subprocess.run(f'schtasks /delete /tn {self.task_name} /f', shell=True)
            print("Scraping job removed successfully")
        except Exception as e:
            print(f"Error removing scraping job: {e}")

# Example usage
if __name__ == "__main__":
    try:
        scheduler = ScrapingScheduler()
        # Schedule scraping every hour
        scheduler.schedule_scraping(60)
    except Exception as e:
        print(f"Error initializing scheduler: {e}") 