import os
import re
from contextlib import contextmanager

@contextmanager
def mysql():
    import mysql.connector
    con = mysql.connector.connect(
        host=os.environ.get("MYSQL_HOST", "127.0.0.1"),
        user=os.environ.get("MYSQL_USER", "root"),
        password=os.environ.get("MYSQL_PASSWORD"),
        database=os.environ.get("MYSQL_DATABASE", "seguranca"),
        connection_timeout=5)
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()

@contextmanager
def mongo():
    from pymongo import MongoClient
    with MongoClient(os.environ.get("MONGO_URI", "mongodb://localhost:27017/"),
                     serverSelectionTimeoutMS=3000) as client:
        yield client['seguranca']

USUARIOS = """CREATE TABLE IF NOT EXISTS usuarios (
 id INT AUTO_INCREMENT PRIMARY KEY, nome VARCHAR(100) NOT NULL,
 email VARCHAR(150) NOT NULL UNIQUE, nivel_acesso INT NOT NULL DEFAULT 1,
 CHECK (nivel_acesso BETWEEN 1 AND 5))"""
ALERTAS = """CREATE TABLE IF NOT EXISTS alertas (
 id INT AUTO_INCREMENT PRIMARY KEY, tipo VARCHAR(50), ip_origem VARCHAR(45),
 severidade ENUM('baixa','media','alta','critica'),
 status VARCHAR(20) DEFAULT 'aberto',
 criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"""
INICIAIS = [('Carlos Silva', 'carlos@empresa.com', 3),
            ('Ana Costa', 'ana@empresa.com', 5),
            ('Bruno Lima', 'bruno@empresa.com', 1)]

def preparar_usuarios(con):
    with con.cursor() as cur:
        cur.execute(USUARIOS)
        for linha in INICIAIS:
            cur.execute('SELECT id FROM usuarios WHERE email=%s', (linha[1],))
            if cur.fetchone() is None:
                cur.execute('INSERT INTO usuarios (nome,email,nivel_acesso) VALUES (%s,%s,%s)', linha)

def validar_usuario(d, campo='nivel_acesso'):
    if not isinstance(d, dict):
        raise ValueError('corpo JSON inválido')
    if not isinstance(d.get('nome'), str) or not d['nome'].strip() or len(d['nome']) > 100:
        raise ValueError('nome obrigatório (até 100 caracteres)')
    email = d.get('email')
    if not isinstance(email, str) or len(email) > 150 or not re.fullmatch(r'[^@\s.][^@\s]*@[^@\s]+\.[^@\s.]+', email):
        raise ValueError('email inválido')
    if type(d.get(campo)) is not int or not 1 <= d[campo] <= 5:
        raise ValueError('nível inválido: use 1 a 5')
    return d['nome'].strip(), email, d[campo]

def validar_ip(ip):
    if not isinstance(ip, str):
        return False
    partes = ip.split('.')
    return len(partes) == 4 and all(p.isascii() and p.isdigit() and 0 <= int(p) <= 255 for p in partes)

def privado(ip):
    a,b,_,_ = map(int, ip.split('.'))
    return a == 10 or (a == 172 and 16 <= b <= 31) or (a == 192 and b == 168)
