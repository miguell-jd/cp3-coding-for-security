import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from apoio import mysql, preparar_usuarios, validar_usuario
from mysql.connector import IntegrityError

def cadastrar(con,nome,email,nivel):
    dados = validar_usuario(dict(nome=nome,email=email,nivel_acesso=nivel))
    with con.cursor() as cur:
        cur.execute('INSERT INTO usuarios (nome,email,nivel_acesso) VALUES (%s,%s,%s)',dados)
        return cur.lastrowid

def listar(con):
    with con.cursor(dictionary=True) as cur:
        cur.execute('SELECT * FROM usuarios ORDER BY id')
        return cur.fetchall()

def buscar(con,email):
    with con.cursor(dictionary=True) as cur:
        cur.execute('SELECT * FROM usuarios WHERE email=%s',(email,))
        return cur.fetchone()

def atualizar(con,email,nivel):
    if type(nivel) is not int or not 1 <= nivel <= 5: raise ValueError('nível inválido')
    with con.cursor() as cur:
        cur.execute('UPDATE usuarios SET nivel_acesso=%s WHERE email=%s',(nivel,email))
        return cur.rowcount

def remover(con,email):
    with con.cursor() as cur:
        cur.execute('DELETE FROM usuarios WHERE email=%s',(email,))
        return cur.rowcount

def main():
    with mysql() as con:
        preparar_usuarios(con)
        con.commit()
        while True:
            op = input('[1] cadastrar [2] listar [3] buscar email [4] nível [5] remover [6] sair: ')
            try:
                if op == '6': break
                if op == '1': print(cadastrar(con,input('Nome: '),input('Email: '),int(input('Nível: '))))
                elif op == '2':
                    for u in listar(con): print(u['nome'],'|',u['email'],'| nível',u['nivel_acesso'])
                elif op == '3': print(buscar(con,input('Email: ')))
                elif op == '4': print('Nível atualizado!' if atualizar(con,input('Email: '),int(input('Nível: '))) else 'Não encontrado ou sem mudança')
                elif op == '5': print('Removido' if remover(con,input('Email: ')) else 'Não encontrado')
                else: print('Opção inválida')
                con.commit()
            except IntegrityError:
                con.rollback()
                print('Erro: email já existe')
            except ValueError as e: print(e)

if __name__ == '__main__':
    main()
