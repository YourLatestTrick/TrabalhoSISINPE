from flask import jsonify
from trabalho_g2_sisinpe.api.services.service import get_events

def init_routers(app):
    @app.get("/events")
    def get_state_events():
        return jsonify(get_events()), 200
    