from datetime import datetime, timezone, timedelta
from flask import Flask, request, jsonify
from bson import ObjectId
from pymongo.errors import PyMongoError
from apoio import mongo, validar_ip

SEVERIDADES = ('baixa','media','alta','critica')
STATUS = ('aberto','em_analise','resolvido')

def validar(d, parcial=False):
    if not isinstance(d,dict) or not d: raise ValueError('corpo inválido')
    campos = {'titulo','severidade','status','ip_origem'}
    if set(d) - campos: raise ValueError('campos desconhecidos')
    if not parcial and not {'titulo','severidade','ip_origem'} <= set(d):
        raise ValueError('titulo, severidade e ip_origem obrigatórios')
    if 'titulo' in d and (not isinstance(d['titulo'],str) or not d['titulo'].strip()):
        raise ValueError('título inválido')
    if 'severidade' in d and d['severidade'] not in SEVERIDADES: raise ValueError('severidade inválida')
    if 'status' in d and d['status'] not in STATUS: raise ValueError('status inválido')
    if 'ip_origem' in d and not validar_ip(d['ip_origem']): raise ValueError('IP inválido')
    return dict(d)

def serializar(doc):
    d = dict(doc)
    d['id'] = str(d.pop('_id'))
    if isinstance(d.get('criado_em'),datetime): d['criado_em'] = d['criado_em'].isoformat()
    return d

def criar_app(paginada=False):
    app = Flask(__name__)

    @app.errorhandler(PyMongoError)
    def falha_banco(e):
        return jsonify(erro='serviço indisponível'),500

    @app.route('/api/incidentes',methods=['GET','POST'])
    def colecao():
        if request.method == 'POST':
            try: d = validar(request.get_json(silent=True))
            except ValueError as e: return jsonify(erro=str(e)),400
            d.setdefault('status','aberto')
            d['criado_em'] = datetime.now(timezone.utc)
            with mongo() as db: d['_id'] = db.incidentes.insert_one(d).inserted_id
            return jsonify(serializar(d)),201
        filtro = {}
        if paginada:
            try:
                pagina = int(request.args.get('pagina','1'))
                tamanho = int(request.args.get('tamanho','10'))
                if pagina < 1 or not 1 <= tamanho <= 100: raise ValueError()
                for chave,permitidos in [('severidade',SEVERIDADES),('status',STATUS)]:
                    if chave in request.args:
                        valor = request.args[chave]
                        if valor not in permitidos: raise ValueError()
                        filtro[chave] = valor
            except ValueError: return jsonify(erro='paginação ou filtros inválidos'),400
        with mongo() as db:
            cursor = db.incidentes.find(filtro).sort([('criado_em',-1),('_id',-1)])
            if paginada:
                total = db.incidentes.count_documents(filtro)
                dados = [serializar(d) for d in cursor.skip((pagina-1)*tamanho).limit(tamanho)]
                return jsonify(dados=dados,pagina=pagina,tamanho=tamanho,total=total,
                               paginas=(total+tamanho-1)//tamanho)
            return jsonify([serializar(d) for d in cursor])

    @app.route('/api/incidentes/<ident>',methods=['GET','PUT','DELETE'])
    def item(ident):
        if not ObjectId.is_valid(ident): return jsonify(erro='id inválido'),400
        filtro = {'_id':ObjectId(ident)}
        dados = None
        if request.method == 'PUT':
            try: dados = validar(request.get_json(silent=True),parcial=True)
            except ValueError as e: return jsonify(erro=str(e)),400
        with mongo() as db:
            if request.method == 'GET':
                doc = db.incidentes.find_one(filtro)
                if doc is None: return jsonify(erro='incidente não encontrado'),404
                return jsonify(serializar(doc))
            if request.method == 'DELETE':
                if not db.incidentes.delete_one(filtro).deleted_count: return jsonify(erro='incidente não encontrado'),404
                return jsonify(mensagem='Removido')
            if not db.incidentes.update_one(filtro,{'$set':dados}).matched_count:
                return jsonify(erro='incidente não encontrado'),404
            return jsonify(serializar(db.incidentes.find_one(filtro)))
    return app

def popular():
    agora = datetime.now(timezone.utc)
    with mongo() as db:
        db.incidentes.insert_many([dict(titulo=f'Incidente {i+1}',severidade=SEVERIDADES[i%4],
            status=STATUS[i%3],ip_origem='185.220.101.1',criado_em=agora-timedelta(minutes=i)) for i in range(15)])
