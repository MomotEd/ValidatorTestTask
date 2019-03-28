import json
from tornado.web import RequestHandler
from validators.request_validators import Validator


class View(RequestHandler):

    SUPPORTED_METHODS = ["POST"]

    def initialize(self, conf):
        self.validator = Validator(conf["fields"], conf["allow_extra"])

    def set_default_headers(self):
        """Set the default response header to be JSON."""
        self.set_header("Content-Type", 'application/json; charset="utf-8"')

    def post(self):
        self.validator.validate(self.request.body)
