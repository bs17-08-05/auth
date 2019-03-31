from views import *

def setup_routes(app):
    app.router.add_post('/auth/signin', signin)
    app.router.add_post('/auth/signup', signup)
    app.router.add_post('/auth/refresh_token', refresh_token)
    app.router.add_get('/auth/get_tokens', get_tokens)
