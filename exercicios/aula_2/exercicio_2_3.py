import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from datetime import datetime
from apoio import mongo

def montar_filtro(fonte=None,tipo=None,ip=None,desde=None):
    filtro = {k:v for k,v in [('fonte',fonte),('tipo',tipo),('ip',ip)] if v is not None}
    if desde is not None:
        if not isinstance(desde,datetime): raise ValueError('desde deve ser datetime')
        filtro['timestamp'] = {'$gte':desde}
    return filtro

def consultar(fonte=None,tipo=None,ip=None,desde=None):
    filtro = montar_filtro(fonte,tipo,ip,desde)
    with mongo() as db:
        return list(db.eventos.find(filtro).sort('timestamp',-1))

if __name__ == '__main__':
    print(consultar(tipo='FAIL',ip='185.220.101.1'))
    print(consultar(fonte='auth'))
