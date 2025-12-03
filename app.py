from uni_admin.controllers import uni_admin_bp
from mobile_uni.controllers import mobile_uni_bp


from flask import Flask


def app_from_bp():
    app = Flask(__name__)
    app.register_blueprint(mobile_uni_bp, url_prefix="/mobile")
    app.register_blueprint(uni_admin_bp, url_prefix="/admin")

    return app


if __name__ == "__main__":
    app = app_from_bp()
    app.run(host="0.0.0.0", port=5000)
