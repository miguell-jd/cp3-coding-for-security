import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flask import Flask, request, jsonify
from mysql.connector import Error, IntegrityError
from apoio import mysql, USUARIOS, validar_usuario

app = Flask(__name__)

@app.errorhandler(Error)
def erro_banco(e):
    if isinstance(e,IntegrityError) and e.errno == 1062:
        return jsonify(erro='email já cadastrado'),409
    return jsonify(erro='serviço indisponível'),500

@app.route('/api/usuarios',methods=['GET','POST'])
def colecao():
    dados = None
    if request.method == 'POST':
        try: dados = validar_usuario(request.get_json(silent=True))
        except ValueError as e: return jsonify(erro=str(e)),400
    with mysql() as con, con.cursor(dictionary=True) as cur:
        if request.method == 'GET':
            cur.execute('SELECT id,nome,email,nivel_acesso FROM usuarios ORDER BY id')
            return jsonify(cur.fetchall())
        cur.execute('INSERT INTO usuarios (nome,email,nivel_acesso) VALUES (%s,%s,%s)',dados)
        return jsonify(id=cur.lastrowid,nome=dados[0],email=dados[1],nivel_acesso=dados[2]),201

@app.route('/api/usuarios/<int:uid>',methods=['GET','PUT','DELETE'])
def item(uid):
    dados = None
    if request.method == 'PUT':
        try: dados = validar_usuario(request.get_json(silent=True))
        except ValueError as e: return jsonify(erro=str(e)),400
    with mysql() as con, con.cursor(dictionary=True) as cur:
        cur.execute('SELECT id,nome,email,nivel_acesso FROM usuarios WHERE id=%s',(uid,))
        u = cur.fetchone()
        if u is None: return jsonify(erro='usuário não encontrado'),404
        if request.method == 'GET': return jsonify(u)
        if request.method == 'DELETE':
            cur.execute('DELETE FROM usuarios WHERE id=%s',(uid,))
            return jsonify(mensagem='Removido')
        cur.execute('UPDATE usuarios SET nome=%s,email=%s,nivel_acesso=%s WHERE id=%s',(*dados,uid))
        return jsonify(id=uid,nome=dados[0],email=dados[1],nivel_acesso=dados[2])

if __name__ == '__main__':
    if '--preparar' in sys.argv:
        with mysql() as con, con.cursor() as cur: cur.execute(USUARIOS)
    else: app.run(debug=False)
