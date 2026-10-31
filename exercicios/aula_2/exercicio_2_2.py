import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from datetime import datetime
from apoio import mongo, validar_ip

def normalizar(linha):
    data,hora,tipo,usuario,ip = linha.split()
    if not usuario.startswith('usuario=') or not ip.startswith('ip=') or not validar_ip(ip[3:]):
        raise ValueError('linha auth.log inválida')
    return {'timestamp':datetime.fromisoformat(data+'T'+hora),'fonte':'auth','tipo':tipo,
            'ip':ip[3:],'detalhes':{'usuario':usuario.split('=',1)[1]}}

def ingerir(col, linhas):
    documentos = [normalizar(linha) for linha in linhas if linha.strip()]
    if documentos: col.insert_many(documentos)
    return len(documentos)

def top_falhas(col):
    return list(col.aggregate([{'$match':{'tipo':'FAIL'}},
       {'$group':{'_id':'$ip','total':{'$sum':1}}},
       {'$sort':{'total':-1,'_id':1}},{'$limit':5}]))

def main():
    arquivo = Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).with_name('auth.log')
    with mongo() as db:
        total = ingerir(db.eventos,arquivo.read_text(encoding='utf-8').splitlines())
        print('=== Top IPs por falhas de login ===')
        for d in top_falhas(db.eventos): print(d['_id'],'->',d['total'],'falhas')
        print('Total de eventos inseridos:',total)

if __name__ == '__main__':
    main()
