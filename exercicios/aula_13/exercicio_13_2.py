import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from llm_apoio import cliente, classificar, LOGS

def lote(logs,client=None):
    contagem = {'NORMAL':0,'SUSPEITO':0,'CRITICO':0}
    for log in logs:
        rotulo,origem = classificar(log,client)
        contagem[rotulo] += 1
        print(f'[{rotulo}] {log} ({origem})')
    print('=== Resumo ===',' | '.join(f'{k}:{v}' for k,v in contagem.items()))
    return contagem

if __name__ == '__main__':
    logs = Path(sys.argv[1]).read_text(encoding='utf-8').splitlines() if len(sys.argv)>1 else LOGS
    lote(logs,cliente())
