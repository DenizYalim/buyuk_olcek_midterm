from flask import Flask
from controllers import bank_bp


def app_from_bp():
    app = Flask(__name__)
    app.register_blueprint(bank_bp, url_prefix="/bank")
    return app


if __name__ == "__main__":
    app = app_from_bp()
    app.run(host="0.0.0.0", port=5001)
