from app import create_app, db
from flask_migrate import upgrade, migrate, init
import threading
import time
import os
from tests.selenium_tests import selenium_test  

app = create_app()

def run_selenium_tests():
    time.sleep(3)  
    selenium_test.run_selenium_tests()  

def run_migrations():
    with app.app_context():
        try:
            if not os.path.exists("migrations"):
                init()
            migrate(message="Auto migration")
        except Exception as e:
            print(f"[Migration warning] {e}")
        upgrade()

if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        run_migrations()
        threading.Thread(target=run_selenium_tests).start()

    app.run(debug=True, use_reloader=False)
