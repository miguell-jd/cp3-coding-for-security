import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flask import Flask, jsonify
from apoio import validar_ip, privado

blacklist = {'185.220.101.1','45.33.32.156','91.240.118.172'}
app = Flask(__name__)
@app.get('/api/checar-ip/<ip>')
def checar(ip):
    if not validar_ip(ip): return jsonify(erro='IP inválido'),400
    canonico = '.'.join(str(int(p)) for p in ip.split('.'))
    return jsonify(ip=canonico,na_blacklist=canonico in blacklist,tipo='privado' if privado(canonico) else 'publico')

if __name__ == '__main__':
    app.run(debug=False)
