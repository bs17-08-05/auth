from views import *


def setup_routes(app, cors):
    app.router.add_route('POST', '/auth/signin', signin)
    app.router.add_route('POST', '/auth/signup', signup)
    app.router.add_route('POST', '/auth/refresh_token', refresh_token)
    app.router.add_route('GET', '/auth/get_tokens', get_tokens)

    # Configure CORS on all routes.
    for route in list(app.router.routes()):
        cors.add(route)
