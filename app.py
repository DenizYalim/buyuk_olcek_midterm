from uni_admin.controllers import uni_admin_bp
from mobile_uni.controllers import mobile_uni_bp
from bank.controllers import bank_bp

from flask import Flask
from flasgger import Swagger


def app_from_bp():
    app = Flask(__name__)
    app.register_blueprint(mobile_uni_bp, url_prefix="/mobile_app")
    app.register_blueprint(uni_admin_bp, url_prefix="/admin_app")
    app.register_blueprint(bank_bp, url_prefix="/bank")

    swagger = Swagger(app)  # /apidocs # TODO try to delete later

    return app


if __name__ == "__main__":
    app = app_from_bp()
    app.run(host="0.0.0.0", port=5000)


""" 
    TODO
    * paging ok; auth todo
    * to host
    * to film later
    * add logging
    * get batch return
"""