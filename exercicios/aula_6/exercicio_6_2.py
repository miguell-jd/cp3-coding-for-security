import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flask import Flask, request, jsonify

def criterios_senha(senha):
    return {'tamanho_min':len(senha)>=8,'maiuscula':any(c.isupper() for c in senha),
      'minuscula':any(c.islower() for c in senha),'numero':any(c.isdigit() for c in senha),
      'especial':any(c in '!@#$%&*' for c in senha)}

def verificar_senha(senha):
    niveis = {0:'Muito fraca',1:'Fraca',2:'Razoável',3:'Boa',4:'Forte',5:'Muito forte'}
    return niveis[sum(criterios_senha(senha).values())]

app = Flask(__name__)
@app.post('/api/analisar-senha')
def analisar():
    d = request.get_json(silent=True)
    if not isinstance(d,dict) or not isinstance(d.get('senha'),str):
        return jsonify(erro="campo 'senha' obrigatório e deve ser texto"),400
    return jsonify(forca=verificar_senha(d['senha']),criterios=criterios_senha(d['senha']))

if __name__ == '__main__':
    app.run(debug=False)
