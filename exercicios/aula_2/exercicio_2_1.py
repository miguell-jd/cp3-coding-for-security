import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from apoio import mongo, validar_ip
from pymongo.errors import DuplicateKeyError

INICIAIS = [
 {'nome':'SRV-WEB01','tipo':'servidor','ip':'192.168.1.10','status':'ativo'},
 {'nome':'PC-RH03','tipo':'estacao','ip':'192.168.1.45','status':'ativo'},
 {'nome':'SW-CORE01','tipo':'switch','ip':'192.168.1.1','status':'inativo'}]

def cadastrar(col, nome, tipo, ip, status='ativo'):
    if not nome.strip() or not tipo.strip() or not validar_ip(ip) or status not in ('ativo','inativo'):
        raise ValueError('dados inválidos')
    return col.insert_one(dict(nome=nome,tipo=tipo,ip=ip,status=status)).inserted_id

def listar(col):
    return list(col.find({}, {'_id':0}).sort('nome',1))

def buscar(col, ip):
    return col.find_one({'ip':ip}, {'_id':0})

def atualizar(col, ip, status):
    if status not in ('ativo','inativo'):
        raise ValueError('status inválido')
    return col.update_one({'ip':ip},{'$set':{'status':status}}).matched_count

def remover(col, ip):
    return col.delete_one({'ip':ip}).deleted_count

def main():
    with mongo() as db:
        col = db.ativos
        col.create_index('ip',unique=True)
        for d in INICIAIS:
            col.update_one({'ip':d['ip']},{'$setOnInsert':d},upsert=True)
        while True:
            op = input('[1] cadastrar [2] listar [3] buscar IP [4] status [5] remover [6] sair: ')
            try:
                if op == '6': break
                if op == '1':
                    cadastrar(col,input('Nome: '),input('Tipo: '),input('IP: '))
                    print('Ativo cadastrado!')
                elif op == '2':
                    for ativo in listar(col): print(ativo)
                elif op == '3': print(buscar(col,input('IP: ')))
                elif op == '4': print('Status atualizado!' if atualizar(col,input('IP: '),input('Status: ')) else 'Não encontrado')
                elif op == '5': print('Removido' if remover(col,input('IP: ')) else 'Não encontrado')
                else: print('Opção inválida')
            except DuplicateKeyError: print('Erro: IP já cadastrado!')
            except ValueError as e: print(e)

if __name__ == '__main__':
    main()
