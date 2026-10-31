import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flask import Flask, request, jsonify
from apoio import validar_usuario

def criar_app():
    app = Flask(__name__)
    usuarios = {}
    proximo_id = 1

    @app.route('/api/usuarios', methods=['GET','POST'])
    def colecao():
        nonlocal proximo_id
        if request.method == 'GET': return jsonify(list(usuarios.values()))
        d = request.get_json(silent=True)
        try: nome,email,nivel = validar_usuario(d,'nivel')
        except ValueError as e: return jsonify(erro=str(e)),400
        if any(u['email'] == email for u in usuarios.values()):
            return jsonify(erro='email já existe'),400
        u = dict(id=proximo_id,nome=nome,email=email,nivel=nivel)
        usuarios[proximo_id] = u
        proximo_id += 1
        return jsonify(u),201

    @app.route('/api/usuarios/<int:uid>',methods=['GET','PUT','DELETE'])
    def item(uid):
        if uid not in usuarios: return jsonify(erro='usuário não encontrado'),404
        if request.method == 'GET': return jsonify(usuarios[uid])
        if request.method == 'DELETE':
            del usuarios[uid]
            return jsonify(mensagem='Removido'),200
        d = request.get_json(silent=True)
        try: nome,email,nivel = validar_usuario(d,'nivel')
        except ValueError as e: return jsonify(erro=str(e)),400
        if any(i != uid and u['email'] == email for i,u in usuarios.items()):
            return jsonify(erro='email já existe'),400
        usuarios[uid] = dict(id=uid,nome=nome,email=email,nivel=nivel)
        return jsonify(usuarios[uid])
    return app

app = criar_app()
if __name__ == '__main__':
    app.run(debug=False)
