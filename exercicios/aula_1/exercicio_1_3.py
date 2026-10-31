import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

DECISOES = [
 ('Saldo bancário','CP','Todos os nós devem concordar com o saldo para evitar gastos inconsistentes.', 'Durante partições, recusar operações preserva a consistência financeira.'),
 ('500 mil eventos de firewall/minuto','AP','A ingestão deve continuar disponível durante uma partição de rede.', 'A reconciliação posterior aceita consistência eventual sem interromper a coleta.'),
 ('Cache de tokens de sessão','AP','O cache mantém atendimento de sessões durante falhas de comunicação.', 'Aceita-se atraso de atualização; sessões críticas exigiriam CP para revogações imediatas.'),
 ('Auditoria de transferências','CP','A autorização de cada transferência precisa de um registro consistente.', 'Bloquear temporariamente a escrita evita registros divergentes de responsabilidade.'),
 ('Feed de IOCs em cinco regiões','AP','Todas as regiões devem consultar indicadores mesmo durante uma partição.', 'Atualizações podem convergir depois, aceitando temporariamente versões diferentes.')]

def main():
    linhas = ['# Decisões CAP', '', '| Cenário | CP/AP | Justificativa |', '|---|---|---|']
    for c,p,j1,j2 in DECISOES:
        linhas.append(f'| {c} | {p} | {j1}<br>{j2} |')
    texto = '\n'.join(linhas) + '\n'
    Path(__file__).with_name('decisoes_cap.md').write_text(texto,encoding='utf-8')
    print(texto)

if __name__ == '__main__':
    main()
