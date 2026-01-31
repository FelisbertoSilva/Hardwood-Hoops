import os
from flask import Flask
from routes.home_routes import home_bp
from routes.player_routes import player_bp
from routes.team_routes import team_bp
from routes.stats_routes import stats_bp
from routes.records_routes import records_bp
from routes.finances_routes import finances_bp
from routes.draft_routes import draft_bp
from routes.free_agency_routes import free_agency_bp
from routes.rules_routes import rules_bp
from routes.transactions_routes import transactions_bp

app = Flask(__name__)


app.register_blueprint(home_bp)
app.register_blueprint(player_bp)
app.register_blueprint(team_bp)
app.register_blueprint(stats_bp)
app.register_blueprint(records_bp)
app.register_blueprint(finances_bp)
app.register_blueprint(draft_bp)
app.register_blueprint(free_agency_bp)
app.register_blueprint(rules_bp)
app.register_blueprint(transactions_bp)

if __name__ == '__main__':
    app.run(debug=True)