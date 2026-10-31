import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import os
import time
import requests
from apoio import validar_ip, privado

IPS = ['8.8.8.8','1.1.1.1','185.220.101.1','192.168.1.10','8.8.8.8']
BLACKLIST = {'185.220.101.1','45.33.32.156','91.240.118.172'}

def enriquecer(ips):
    cache,relatorio = {},[]
    consultas,hits,internos = 0,0,0
    for ip in ips:
        if not validar_ip(ip):
            relatorio.append({'ip':ip,'erro':'IP inválido'})
            continue
        ip = '.'.join(str(int(p)) for p in ip.split('.'))
        if privado(ip):
            internos += 1
            relatorio.append({'ip':ip,'tipo':'INTERNO','descricao':'Rede Interna (não consultado)'})
            continue
        if ip in cache:
            hits += 1
            relatorio.append({**cache[ip],'cache':True})
            continue
        dados = None
        for tentativa in range(3):
            try:
                consultas += 1
                params = {'token':os.environ['IPINFO_TOKEN']} if os.environ.get('IPINFO_TOKEN') else None
                r = requests.get(f'https://ipinfo.io/{ip}/json',params=params,timeout=10)
                if r.status_code == 429:
                    if tentativa < 2: time.sleep(2**tentativa)
                    continue
                r.raise_for_status()
                dados = r.json()
                if not isinstance(dados,dict): raise ValueError('JSON inválido')
                break
            except (requests.exceptions.RequestException,ValueError): break
        item = dict(ip=ip,tipo='EXTERNO',suspeito=ip in BLACKLIST)
        if dados is None: item['erro'] = 'consulta indisponível ou limite excedido'
        else:
            item.update(cidade=dados.get('city','?'),pais=dados.get('country','?'),org=dados.get('org','?'))
            cache[ip] = item.copy()
        relatorio.append(item)
    return relatorio,dict(consultas_http=consultas,cache_hits=hits,internos=internos)

if __name__ == '__main__':
    relatorio,resumo = enriquecer(sys.argv[1:] or IPS)
    for item in relatorio: print('[CACHE]' if item.get('cache') else '',item)
    print('=== Resumo ===',resumo)
