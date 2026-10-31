# Decisões CAP

| Cenário | CP/AP | Justificativa |
|---|---|---|
| Saldo bancário | CP | Todos os nós devem concordar com o saldo para evitar gastos inconsistentes.<br>Durante partições, recusar operações preserva a consistência financeira. |
| 500 mil eventos de firewall/minuto | AP | A ingestão deve continuar disponível durante uma partição de rede.<br>A reconciliação posterior aceita consistência eventual sem interromper a coleta. |
| Cache de tokens de sessão | AP | O cache mantém atendimento de sessões durante falhas de comunicação.<br>Aceita-se atraso de atualização; sessões críticas exigiriam CP para revogações imediatas. |
| Auditoria de transferências | CP | A autorização de cada transferência precisa de um registro consistente.<br>Bloquear temporariamente a escrita evita registros divergentes de responsabilidade. |
| Feed de IOCs em cinco regiões | AP | Todas as regiões devem consultar indicadores mesmo durante uma partição.<br>Atualizações podem convergir depois, aceitando temporariamente versões diferentes. |
