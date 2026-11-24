import threading
from flask import Flask
from flask_cors import CORS
from .monitoring import monitor_system
from trabalho_g2_sisinpe.api.routers.router import init_routes

app = Flask(__name__)
CORS(app)
init_routes(app)

if __name__ == "__main__":
    threading.Thread(target=monitor_system, daemon=True).start()
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
    