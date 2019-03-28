import os
import yaml
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define, options
from tornado.web import Application
from views import View

define('port', default=8000, help='port to listen on')
define('domain', default='0.0.0.0', help='domain name')


def set_up_routes():
    routes = []
    with open("config/schema.yml", 'r') as f:
        cfg = yaml.load(f)
        end_points = cfg["patterns"]
        routes.extend([(f"/{name}", View, dict(conf=conf)) for name, conf in end_points.items()])
    return routes


def main():
    """Construct and serve the tornado application."""
    routs = set_up_routes()
    mode = os.environ.get('DEBUG')
    app = Application(routs, debug=mode)
    http_server = HTTPServer(app)
    http_server.listen(options.port)
    print(f'Listening on http://{options.domain}:{options.port}')
    IOLoop.current().start()


if __name__ == "__main__":
    main()
