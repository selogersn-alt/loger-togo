def application(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [b"<h1>Loger Senegal - Test de Connexion</h1><p>Si vous voyez ceci, le serveur Python fonctionne. Le probleme vient de la configuration Django.</p>"]
