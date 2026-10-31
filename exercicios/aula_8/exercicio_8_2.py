import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

"""401 genérico evita revelar se uma conta existe. Limite: 5 falhas/IP/60s.
Credenciais iniciais vêm de LOGIN_USER e LOGIN_PASSWORD via os.environ.
SHA-256 segue o hashlib do 1º semestre e é apenas didático: não é KDF de senha.
"""
import os
import time
import hashlib
from flask import Flask, request, jsonify
from mysql.connector import Error
from apoio import mysql

def criar_app():
    app = Flask(__name__)
    tentativas = {}
    @app.errorhandler(Error)
    def banco_indisponivel(e): return jsonify(erro='serviço indisponível'),500

    @app.post('/login')
    def login():
        d = request.get_json(silent=True) if request.is_json else request.form
        if not d or not isinstance(d.get('usuario'),str) or not isinstance(d.get('senha'),str) or not d['usuario'].strip() or not d['senha']:
            return jsonify(erro='campos obrigatórios'),400
        ip = request.remote_addr
        agora = time.monotonic()
        falhas = [t for t in tentativas.get(ip,[]) if agora-t < 60]
        tentativas[ip] = falhas
        if len(falhas) >= 5: return jsonify(erro='limite de tentativas excedido'),429
        digest = hashlib.sha256(d['senha'].encode()).hexdigest()
        with mysql() as con, con.cursor() as cur:
            cur.execute('SELECT id FROM login_usuarios WHERE usuario=%s AND senha_hash=%s',(d['usuario'],digest))
            valido = cur.fetchone() is not None
        if not valido:
            falhas.append(agora)
            return jsonify(erro='Credenciais inválidas'),401
        tentativas.pop(ip,None)
        return jsonify(mensagem='Login OK')
    return app

def preparar():
    usuario,senha = os.environ.get('LOGIN_USER'),os.environ.get('LOGIN_PASSWORD')
    if not usuario or not senha: raise ValueError('Defina LOGIN_USER e LOGIN_PASSWORD')
    with mysql() as con, con.cursor() as cur:
        cur.execute('CREATE TABLE IF NOT EXISTS login_usuarios (id INT AUTO_INCREMENT PRIMARY KEY, usuario VARCHAR(100) UNIQUE NOT NULL, senha_hash CHAR(64) NOT NULL)')
        cur.execute('INSERT INTO login_usuarios (usuario,senha_hash) VALUES (%s,%s) ON DUPLICATE KEY UPDATE senha_hash=VALUES(senha_hash)',
                    (usuario,hashlib.sha256(senha.encode()).hexdigest()))

app = criar_app()
if __name__ == '__main__':
    if '--preparar' in sys.argv: preparar()
    else: app.run(debug=False)
