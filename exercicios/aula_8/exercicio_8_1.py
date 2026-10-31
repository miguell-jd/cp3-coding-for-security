import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flask import Flask, request, render_template, redirect

def criar_app():
    app = Flask(__name__)
    alertas = []
    @app.route('/',methods=['GET','POST'])
    def dashboard():
        if request.method == 'POST':
            descricao = request.form.get('descricao','')
            if not descricao.strip(): return 'Descrição obrigatória',400
            alertas.append({'descricao':descricao})
            return redirect('/')
        return render_template('alertas.html',alertas=alertas)
    return app

app = criar_app()
if __name__ == '__main__':
    app.run(debug=False)
