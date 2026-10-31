import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import os
import json
import requests

def obter(caminho, params=None):
    headers = {'Accept':'application/vnd.github+json'}
    token = os.environ.get('GITHUB_TOKEN')
    if token: headers['Authorization'] = 'Bearer '+token
    try:
        r = requests.get('https://api.github.com/'+caminho,params=params,headers=headers,timeout=15)
        if r.status_code in (403,429):
            print('Acesso bloqueado ou limite de requisições (403/429). Aguarde antes de tentar novamente.')
            return None
        if r.status_code == 404:
            print('Usuário ou repositório não encontrado')
            return None
        r.raise_for_status()
        return r.json()
    except requests.exceptions.Timeout: print('Timeout ao consultar GitHub')
    except requests.exceptions.ConnectionError: print('Erro de conexão com GitHub')
    except (requests.exceptions.RequestException,ValueError): print('Erro HTTP ou JSON inválido')
    return None

def listar_repos(usuario):
    repos,pagina = [],1
    while True:
        lote = obter(f'users/{usuario}/repos',{'page':pagina,'per_page':100})
        if lote is None: return None
        if not isinstance(lote,list):
            print('Resposta de repositórios inválida')
            return None
        if not lote: return repos
        repos.extend(lote)
        pagina += 1

def main():
    resultado = None
    while True:
        op = input('[1] usuário [2] repositórios [3] detalhar repo [4] salvar JSON [5] sair: ')
        if op == '5': break
        if op == '1':
            resultado = obter('users/'+input('Usuário: ').strip())
            if resultado: print('Nome:',resultado.get('name'),'| Repos públicos:',resultado.get('public_repos'),'| Seguidores:',resultado.get('followers'))
        elif op == '2':
            resultado = listar_repos(input('Usuário: ').strip())
            if resultado is not None:
                for i,r in enumerate(resultado,1): print(i,r['name'],'★',r['stargazers_count'],r.get('language'))
        elif op == '3':
            resultado = obter('repos/'+input('Dono/repositório: ').strip())
            print(json.dumps(resultado,indent=2,ensure_ascii=False))
        elif op == '4':
            if resultado is None: print('Consulte um resultado antes de salvar')
            else:
                nome = Path(input('Arquivo JSON (nome): ')).name
                if not nome.endswith('.json'): nome += '.json'
                destino = Path(__file__).with_name(nome)
                destino.write_text(json.dumps(resultado,indent=2,ensure_ascii=False),encoding='utf-8')
                print('Resultados salvos em',destino.name)
        else: print('Opção inválida')

if __name__ == '__main__':
    main()
