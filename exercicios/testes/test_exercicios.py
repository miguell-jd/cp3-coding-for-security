"""Testes locais; SQLite adapta sintaxe para verificar fluxos, não emula MySQL real.
MongoDB é simulado por mongomock. APIs externas são substituídas por respostas controladas.
"""
import ast
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch, Mock
from types import SimpleNamespace

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
import apoio
import incidentes_api
import llm_apoio
import mongomock
import requests
from mysql.connector import Error, IntegrityError
from bson import ObjectId


def carregar(a,n):
    nome = f'exercicio_{a}_{n}'
    spec = importlib.util.spec_from_file_location(nome, BASE / f'aula_{a}' / f'{nome}.py')
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    return mod


def silencioso(func,*args,**kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return func(*args,**kwargs)


class Cursor:
    def __init__(self, con, dictionary=False):
        self.cur = con.raw.cursor()
        self.dictionary = dictionary

    def __enter__(self): return self
    def __exit__(self,*args): self.cur.close()

    def execute(self,sql,params=()):
        # Adaptação estritamente para exercitar a lógica sem servidor MySQL.
        sql = re.sub(r'INT AUTO_INCREMENT PRIMARY KEY','INTEGER PRIMARY KEY AUTOINCREMENT',sql)
        sql = re.sub(r"ENUM\([^)]*\)",'TEXT',sql)
        sql = sql.replace('DATE_SUB(NOW(), INTERVAL 90 DAY)',"datetime('now','-90 days')")
        sql = sql.replace('ON DUPLICATE KEY UPDATE','ON CONFLICT DO UPDATE SET')
        sql = re.sub(r'VALUES\((\w+)\)',r'excluded.\1',sql)
        sql = sql.replace('%s','?')
        try: self.cur.execute(sql,params)
        except sqlite3.IntegrityError as e:
            if 'UNIQUE' in str(e): raise IntegrityError(msg='duplicate',errno=1062) from e
            raise

    def executemany(self,sql,params):
        for p in params: self.execute(sql,p)

    def fetchone(self):
        r = self.cur.fetchone()
        return dict(zip([d[0] for d in self.cur.description],r)) if self.dictionary and r is not None else r

    def fetchall(self):
        r = self.cur.fetchall()
        return [dict(zip([d[0] for d in self.cur.description],x)) for x in r] if self.dictionary else r

    @property
    def rowcount(self): return self.cur.rowcount
    @property
    def lastrowid(self): return self.cur.lastrowid


class BancoSQL:
    def __init__(self):
        self.raw = sqlite3.connect(':memory:')
        self.raw.execute('PRAGMA foreign_keys=ON')
    def cursor(self,dictionary=False): return Cursor(self,dictionary)
    def commit(self): self.raw.commit()
    def rollback(self): self.raw.rollback()
    @contextlib.contextmanager
    def conectar(self):
        try:
            yield self
            self.commit()
        except Exception:
            self.rollback()
            raise


class Estrutura(unittest.TestCase):
    def test_30_exercicios_importam_sem_abrir_conexoes(self):
        arquivos = list(BASE.glob('aula_*/exercicio_*.py'))
        self.assertEqual(len(arquivos),30)
        for p in arquivos:
            ast.parse(p.read_text(encoding='utf-8'))
            _,a,n = p.stem.split('_')
            carregar(a,n)
        for aula in (5,9,11,14): self.assertFalse((BASE/f'aula_{aula}').exists())

    def test_credenciais_sem_literais(self):
        for p in BASE.rglob('*.py'):
            if p == Path(__file__): continue
            arvore = ast.parse(p.read_text(encoding='utf-8'))
            for node in ast.walk(arvore):
                if isinstance(node,ast.Assign) and isinstance(node.value,ast.Constant) and isinstance(node.value.value,str):
                    for target in node.targets:
                        if isinstance(target,ast.Name):
                            self.assertNotIn(target.id.lower(),('senha','password','api_key','senha_db'))

    def test_validacao_ip_e_nivel(self):
        for ip in ('999.999.1.1','+1.2.3.4','a.2.3.4','1.2.3','1.2.3.٤'):
            self.assertFalse(apoio.validar_ip(ip))
        for ip in ('192.168.1.1','172.16.0.1','10.1.1.1'): self.assertTrue(apoio.privado(ip))
        for nivel in (0,6,True,'3'):
            with self.assertRaises(ValueError): apoio.validar_usuario(dict(nome='A',email='a@x.com',nivel_acesso=nivel))

    def test_relatorios_cap_auditoria(self):
        cap = carregar(1,3)
        auditoria = carregar(8,3)
        self.assertEqual([d[1] for d in cap.DECISOES],['CP','AP','AP','CP','AP'])
        self.assertEqual(len(auditoria.FALHAS),5)
        silencioso(cap.main)
        silencioso(auditoria.main)
        self.assertTrue((BASE/'aula_1/decisoes_cap.md').exists())
        self.assertTrue((BASE/'aula_8/auditoria.md').exists())


class Mongo(unittest.TestCase):
    def setUp(self):
        self.db = mongomock.MongoClient().seguranca
        @contextlib.contextmanager
        def conectar(): yield self.db
        self.conectar = conectar

    def test_inventario_indice_crud(self):
        m = carregar(2,1)
        col = self.db.ativos
        col.create_index('ip',unique=True)
        for d in m.INICIAIS: col.insert_one(d.copy())
        m.cadastrar(col,'SRV-DB01','servidor','192.168.1.20')
        from pymongo.errors import DuplicateKeyError
        with self.assertRaises(DuplicateKeyError): m.cadastrar(col,'X','servidor','192.168.1.10')
        self.assertEqual(m.buscar(col,'192.168.1.45')['nome'],'PC-RH03')
        self.assertEqual(m.atualizar(col,'192.168.1.1','ativo'),1)
        self.assertEqual(len(m.listar(col)),4)
        self.assertEqual(m.remover(col,'192.168.1.20'),1)

    def test_ingestao_e_filtros_combinados(self):
        m = carregar(2,2)
        linhas = (BASE/'aula_2/auth.log').read_text().splitlines()
        self.assertEqual(m.ingerir(self.db.eventos,linhas),23)
        self.assertEqual([d['total'] for d in m.top_falhas(self.db.eventos)],[10,5,3])
        q = carregar(2,3)
        with patch.object(q,'mongo',self.conectar):
            self.assertEqual(len(q.consultar(tipo='FAIL',ip='185.220.101.1')),10)
            self.assertEqual(len(q.consultar(fonte='auth')),23)
            from datetime import datetime
            docs = q.consultar(fonte='auth',tipo='FAIL',desde=datetime(2025,2,20,8,15,10))
            self.assertEqual(len(docs),9)
            self.assertEqual(docs, sorted(docs,key=lambda d:d['timestamp'],reverse=True))

    def test_api_incidentes_crud_e_id(self):
        with patch.object(incidentes_api,'mongo',self.conectar):
            c = carregar(7,1).app.test_client()
            self.assertEqual(c.post('/api/incidentes',json={}).status_code,400)
            self.assertEqual(c.post('/api/incidentes',json={'titulo':'x','severidade':'alta','ip_origem':'bad'}).status_code,400)
            d = {'titulo':'Brute force SSH','severidade':'alta','ip_origem':'185.220.101.1'}
            r = c.post('/api/incidentes',json=d)
            self.assertEqual(r.status_code,201)
            uid = r.json['id']
            self.assertTrue(ObjectId.is_valid(uid))
            self.assertEqual(c.get('/api/incidentes/'+uid).json['titulo'],d['titulo'])
            self.assertEqual(c.get('/api/incidentes/invalido').status_code,400)
            self.assertEqual(c.get('/api/incidentes/'+str(ObjectId())).status_code,404)
            self.assertEqual(c.put('/api/incidentes/'+uid,json={'status':'resolvido'}).json['status'],'resolvido')
            self.assertEqual(c.put('/api/incidentes/'+uid,json={'$set':{}}).status_code,400)
            self.assertEqual(c.delete('/api/incidentes/'+uid).status_code,200)
            self.assertEqual(c.delete('/api/incidentes/'+uid).status_code,404)

    def test_paginacao_filtros_15_incidentes(self):
        with patch.object(incidentes_api,'mongo',self.conectar):
            incidentes_api.popular()
            c = carregar(7,2).app.test_client()
            r = c.get('/api/incidentes?tamanho=5&pagina=1')
            self.assertEqual((r.status_code,len(r.json['dados']),r.json['total']),(200,5,15))
            r2 = c.get('/api/incidentes?tamanho=5&pagina=2')
            self.assertFalse(set(d['id'] for d in r.json['dados']) & set(d['id'] for d in r2.json['dados']))
            self.assertEqual(r.json['dados'],sorted(r.json['dados'],key=lambda d:d['criado_em'],reverse=True))
            r = c.get('/api/incidentes?severidade=critica&status=aberto&tamanho=3')
            self.assertGreater(r.json['total'],0)
            self.assertTrue(all(d['severidade']=='critica' and d['status']=='aberto' for d in r.json['dados']))
            for qs in ('pagina=0','tamanho=0','tamanho=101','pagina=x','severidade=INVALIDA','status=x'):
                self.assertEqual(c.get('/api/incidentes?'+qs).status_code,400)
            self.assertEqual(c.get('/api/incidentes?pagina=999').json['dados'],[])

    def test_falha_mongo_sem_detalhes(self):
        from pymongo.errors import ServerSelectionTimeoutError
        @contextlib.contextmanager
        def falha(): raise ServerSelectionTimeoutError('DETALHE_INTERNO'); yield
        with patch.object(incidentes_api,'mongo',falha):
            r = carregar(7,1).app.test_client().get('/api/incidentes')
            self.assertEqual(r.status_code,500)
            self.assertEqual(r.json,{'erro':'serviço indisponível'})


class SQL(unittest.TestCase):
    def setUp(self): self.banco = BancoSQL()
    def tearDown(self): self.banco.raw.close()

    def test_modelagem_pk_fk_e_registro(self):
        m = carregar(1,1)
        with patch.object(m,'mysql',self.banco.conectar):
            silencioso(m.main)
            silencioso(m.main)
        r = self.banco.raw.execute('SELECT nome,cve_id,severidade,cvss FROM ativos JOIN ativo_vulnerabilidade ON ativo_id=ativos.id JOIN vulnerabilidades ON vuln_id=vulnerabilidades.id').fetchone()
        self.assertEqual(r,('SRV-WEB01','CVE-2024-001','Alta',8.5))
        with self.assertRaises(sqlite3.IntegrityError):
            self.banco.raw.execute('INSERT INTO ativo_vulnerabilidade (ativo_id,vuln_id) VALUES (99,99)')

    def test_crud_alertas_exclui_antigos(self):
        m = carregar(1,2)
        with self.banco.cursor() as cur:
            cur.execute(apoio.ALERTAS)
            cur.execute('INSERT INTO alertas (tipo,severidade,criado_em) VALUES (%s,%s,%s)',('ANTIGO','baixa','2000-01-01'))
        self.banco.commit()
        with patch.object(m,'mysql',self.banco.conectar): silencioso(m.main)
        self.assertEqual(self.banco.raw.execute('SELECT COUNT(*) FROM alertas').fetchone()[0],3)
        self.assertEqual(self.banco.raw.execute("SELECT COUNT(*) FROM alertas WHERE status='resolvido'").fetchone()[0],1)

    def test_usuarios_crud_niveis_e_injecao(self):
        m = carregar(3,1)
        apoio.preparar_usuarios(self.banco)
        self.banco.commit()
        with self.assertRaises(IntegrityError): m.cadastrar(self.banco,'X','carlos@empresa.com',3)
        self.assertEqual(m.buscar(self.banco,'ana@empresa.com')['nivel_acesso'],5)
        self.assertEqual(m.atualizar(self.banco,'bruno@empresa.com',4),1)
        self.assertEqual(m.buscar(self.banco,'bruno@empresa.com')['nivel_acesso'],4)
        for nivel in (0,6,True):
            with self.assertRaises(ValueError): m.atualizar(self.banco,'bruno@empresa.com',nivel)
        uid = m.cadastrar(self.banco,"O'Neil",'oneil@x.com',2)
        self.assertGreater(uid,0)
        self.assertEqual(m.remover(self.banco,'oneil@x.com'),1)
        self.banco.commit()
        poc = carregar(3,2)
        with patch.object(poc,'mysql',self.banco.conectar):
            self.assertEqual(len(poc.buscar_inseguro("' OR '1'='1")),3)
            self.assertEqual(poc.buscar_seguro("' OR '1'='1"),[])

    def test_relatorio_10_alertas(self):
        m = carregar(3,3)
        with patch.object(m,'mysql',self.banco.conectar): silencioso(m.main)
        contagem = dict(self.banco.raw.execute('SELECT severidade,COUNT(*) FROM alertas GROUP BY severidade'))
        self.assertEqual(contagem,{'critica':3,'alta':4,'media':2,'baixa':1})
        self.assertEqual(dict(self.banco.raw.execute('SELECT tipo,COUNT(*) FROM alertas GROUP BY tipo')),{'BRUTE_FORCE':4,'PORT_SCAN':3,'XSS':2,'SQLI':1})

    def test_api_mysql_crud_erros_sem_vazamento(self):
        with self.banco.cursor() as cur: cur.execute(apoio.USUARIOS)
        m = carregar(7,3)
        c = m.app.test_client()
        with patch.object(m,'mysql',self.banco.conectar):
            dados = {'nome':'Ana','email':'ana@x.com','nivel_acesso':5}
            r = c.post('/api/usuarios',json=dados)
            self.assertEqual(r.status_code,201)
            uid = r.json['id']
            self.assertEqual(c.post('/api/usuarios',json=dados).status_code,409)
            self.assertEqual(c.get('/api/usuarios/999').status_code,404)
            self.assertEqual(c.post('/api/usuarios',json={'nome':'X'}).status_code,400)
            self.assertEqual(c.get('/api/usuarios/'+str(uid)).json['nome'],'Ana')
            self.assertEqual(c.put('/api/usuarios/'+str(uid),json={**dados,'nivel_acesso':2}).status_code,200)
            self.assertEqual(c.get('/api/usuarios').json[0]['nivel_acesso'],2)
            self.assertEqual(c.delete('/api/usuarios/'+str(uid)).status_code,200)
        @contextlib.contextmanager
        def falha(): raise Error('query e DETALHE_INTERNO'); yield
        with patch.object(m,'mysql',falha):
            r = c.get('/api/usuarios')
            self.assertEqual((r.status_code,r.json),(500,{'erro':'serviço indisponível'}))

    def test_login_parametros_401_generico_e_limite(self):
        m = carregar(8,2)
        # Segredo efêmero no processo: nenhum arquivo contém uma senha literal.
        segredo = os.urandom(18).hex()
        with patch.dict(os.environ,{'LOGIN_USER':'analista','LOGIN_PASSWORD':segredo}),patch.object(m,'mysql',self.banco.conectar):
            m.preparar()
            c = m.criar_app().test_client()
            self.assertEqual(c.post('/login',json={'usuario':'','senha':''}).status_code,400)
            r1 = c.post('/login',json={'usuario':'ausente','senha':segredo})
            r2 = c.post('/login',json={'usuario':'analista','senha':os.urandom(18).hex()})
            self.assertEqual((r1.status_code,r1.json),(r2.status_code,r2.json))
            self.assertEqual(r1.status_code,401)
            self.assertEqual(c.post('/login',json={'usuario':"' OR '1'='1",'senha':segredo}).status_code,401)
            self.assertEqual(c.post('/login',json={'usuario':'analista','senha':segredo}).status_code,200)
            for _ in range(5):
                self.assertEqual(c.post('/login',json={'usuario':'ausente','senha':segredo}).status_code,401)
            self.assertEqual(c.post('/login',json={'usuario':'analista','senha':segredo}).status_code,429)


class FlaskMemoria(unittest.TestCase):
    def test_usuarios_status_e_duplicados(self):
        c = carregar(6,1).criar_app().test_client()
        dados = {'nome':'Ana','email':'ana@x.com','nivel':5}
        self.assertEqual(c.post('/api/usuarios',json=dados).status_code,201)
        self.assertEqual(c.post('/api/usuarios',json={**dados,'nome':'Bia'}).status_code,400)
        self.assertEqual(c.post('/api/usuarios',json={**dados,'email':'c@x.com','nivel':9}).status_code,400)
        self.assertEqual(c.get('/api/usuarios/1').json['nome'],'Ana')
        self.assertEqual(c.get('/api/usuarios/99').status_code,404)
        self.assertEqual(c.put('/api/usuarios/1',json={**dados,'nivel':3}).json['nivel'],3)
        for entrada in (None,[],{},True): self.assertEqual(c.post('/api/usuarios',json=entrada).status_code,400)
        self.assertEqual(len(c.get('/api/usuarios').json),1)
        self.assertEqual(c.delete('/api/usuarios/1').status_code,200)
        self.assertEqual(c.get('/api/usuarios/1').status_code,404)

    def test_senha_checklist_sem_literais(self):
        c = carregar(6,2).app.test_client()
        segredo = ''.join(chr(x) for x in (65,98,51,64))*3
        r = c.post('/api/analisar-senha',json={'senha':segredo})
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.json['forca'],'Muito forte')
        self.assertTrue(all(r.json['criterios'].values()))
        for d in ({},[],{'senha':None},{'senha':5}):
            self.assertEqual(c.post('/api/analisar-senha',json=d).status_code,400)
        self.assertEqual(c.post('/api/analisar-senha',data='{',content_type='application/json').status_code,400)

    def test_blacklist_publico_privado_invalido(self):
        c = carregar(6,3).app.test_client()
        self.assertTrue(c.get('/api/checar-ip/185.220.101.1').json['na_blacklist'])
        self.assertEqual(c.get('/api/checar-ip/192.168.1.10').json['tipo'],'privado')
        self.assertEqual(c.get('/api/checar-ip/8.8.8.8').json['tipo'],'publico')
        self.assertEqual(c.get('/api/checar-ip/999.999.1.1').status_code,400)

    def test_xss_template_escapa_script_e_dados(self):
        c = carregar(8,1).criar_app().test_client()
        payload = "<script>alert('xss')</script>"
        r = c.post('/',data={'descricao':payload},follow_redirects=True)
        self.assertEqual(r.status_code,200)
        html = r.get_data(as_text=True)
        self.assertNotIn(payload,html)
        self.assertIn('&lt;script&gt;',html)
        import html as html_module
        self.assertIn(payload,html_module.unescape(html))


def resposta(status=200,dados=None):
    r = Mock()
    r.status_code = status
    r.json.return_value = dados
    if status >= 400: r.raise_for_status.side_effect = requests.exceptions.HTTPError(response=r)
    return r


class ClientesExternos(unittest.TestCase):
    def test_nvd_metricas_404_vazio_timeout(self):
        m = carregar(10,1)
        dado = {'vulnerabilities':[{'cve':{'id':'CVE-2021-44228','descriptions':[{'lang':'en','value':'Log4j test'}],
          'metrics':{'cvssMetricV31':[{'cvssData':{'baseScore':10.0,'baseSeverity':'CRITICAL'}}]}}}]}
        with patch.object(m.requests,'get',return_value=resposta(dados=dado)):
            self.assertEqual(m.consultar('CVE-2021-44228')['cvss'],10.0)
        for r in (resposta(404),resposta(dados={'vulnerabilities':[]})):
            with patch.object(m.requests,'get',return_value=r): self.assertIsNone(m.consultar('CVE-0000-0000'))
        with patch.object(m.requests,'get',side_effect=requests.exceptions.Timeout):
            self.assertIsNone(silencioso(m.consultar,'CVE-2021-44228'))

    def test_github_paginas_limite_timeout_json(self):
        m = carregar(10,2)
        with patch.object(m.requests,'get',side_effect=[resposta(dados=[{'name':'a'}]),resposta(dados=[{'name':'b'}]),resposta(dados=[])]) as get:
            self.assertEqual([r['name'] for r in m.listar_repos('octocat')],['a','b'])
            self.assertEqual([c.kwargs['params']['page'] for c in get.call_args_list],[1,2,3])
        for status in (403,429,404):
            with patch.object(m.requests,'get',return_value=resposta(status)):
                self.assertIsNone(silencioso(m.obter,'users/x'))

    def test_github_menu_salva_json(self):
        m = carregar(10,2)
        dados = {'name':'Pessoa de teste','public_repos':2,'followers':3}
        destino = BASE/'aula_10/github_teste.json'
        try:
            with patch.object(m,'obter',return_value=dados),patch('builtins.input',side_effect=['1','octocat','4','github_teste.json','5']):
                silencioso(m.main)
            self.assertEqual(json.loads(destino.read_text(encoding='utf-8')),dados)
        finally:
            destino.unlink(missing_ok=True)
        for erro in (requests.exceptions.Timeout,requests.exceptions.ConnectionError,ValueError):
            with patch.object(m.requests,'get',side_effect=erro):
                self.assertIsNone(silencioso(m.obter,'users/x'))

    def test_ip_cache_privado_backoff(self):
        m = carregar(10,3)
        with patch.object(m.requests,'get',return_value=resposta(dados={'city':'Teste','country':'BR','org':'Lab'})) as get:
            rel,resumo = m.enriquecer(m.IPS)
            self.assertEqual(get.call_count,3)
            self.assertEqual(resumo,{'consultas_http':3,'cache_hits':1,'internos':1})
            self.assertTrue(rel[-1]['cache'])
        with patch.object(m.requests,'get',side_effect=[resposta(429),resposta(429),resposta(dados={'city':'x'})]),patch.object(m.time,'sleep') as sleep:
            rel,resumo = m.enriquecer(['8.8.8.8'])
            self.assertEqual(resumo['consultas_http'],3)
            self.assertEqual([c.args[0] for c in sleep.call_args_list],[1,2])

    def test_llm_fallback_rotulos_e_rebaixamento(self):
        self.assertEqual(llm_apoio.classificar(llm_apoio.LOGS[1])[0],'CRITICO')
        for texto in ('texto inválido','NORMAL',' SUSPEITO '):
            fake = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=lambda **kw:SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=texto))]))))
            self.assertEqual(llm_apoio.classificar('Falha de login',fake)[0],'SUSPEITO')
        fake = Mock()
        fake.chat.completions.create.side_effect = ValueError('erro')
        self.assertEqual(llm_apoio.classificar('GET /../../etc/passwd',fake)[0],'CRITICO')
        lote = carregar(13,2)
        self.assertEqual(silencioso(lote.lote,llm_apoio.LOGS),{'NORMAL':1,'SUSPEITO':1,'CRITICO':1})

    def test_chatbot_historico_e_sair(self):
        m = carregar(13,1)
        with patch.object(m,'cliente',return_value=None),patch('builtins.input',side_effect=['O que é XSS?','E como prevenir?','/sair']):
            historico = silencioso(m.main)
        self.assertEqual([h['role'] for h in historico],['system','user','assistant','user','assistant'])
        self.assertIn('escape',historico[-1]['content'])

    def test_relatorio_prompt_injection_explica_simulacao(self):
        m = carregar(13,3)
        with patch.object(m,'cliente',return_value=None): silencioso(m.main)
        texto = (BASE/'aula_13/prompt_injection.md').read_text(encoding='utf-8')
        self.assertIn('sem chamada à API',texto)
        self.assertIn('Com proteção: SUSPEITO',texto)
        self.assertIn('NORMAL também é um rótulo válido',texto)


class MachineLearning(unittest.TestCase):
    def test_phishing_e_matriz(self):
        m = carregar(4,1)
        modelo = silencioso(m.treinar)
        self.assertEqual(modelo.predict([[11,1,1,1,7]]).tolist(),[1])
        matriz = silencioso(carregar(4,3).avaliar)
        self.assertEqual(matriz.tolist(),[[8,0],[1,1]])

    def test_anomalias_preservam_parametros(self):
        rotulos = silencioso(carregar(4,2).detectar)
        self.assertEqual(rotulos[5],-1)
        self.assertEqual(rotulos[8],-1)
        self.assertEqual(len(rotulos),9)

    def test_cv_torneio_persistencia_tamper(self):
        scores = silencioso(carregar(12,1).avaliar)
        self.assertEqual(len(scores),5)
        from torneio_ml import torneio
        modelo,resultados = silencioso(torneio)
        self.assertEqual(set(resultados),{'RandomForest','SVM','KNN'})
        m = carregar(12,3)
        import joblib
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'modelo.pkl'
            joblib.dump(modelo,p)
            digest = m.sha256(p)
            self.assertEqual(len(digest),64)
            self.assertEqual(m.carregar_verificado(p,digest).predict([[64000,4444,10]]).tolist(),[1])
            with p.open('ab') as f: f.write(b'alteracao')
            with self.assertRaises(ValueError): m.carregar_verificado(p,digest)


if __name__ == '__main__': unittest.main(verbosity=2)
