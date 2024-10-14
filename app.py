from flask import Flask
from aircraft_routes import aircraft_bp

app = Flask(__name__)
app.secret_key = 'SoMeSeCrEtKeYhErE'

# Register blueprints
app.register_blueprint(aircraft_bp)

if __name__ == '__main__':
    app.run()
