# Validação da entrega

Resultado: **29 testes aprovados**, sem falhas, em 24,316 segundos.
Todos os 30 scripts passaram por compilação e importação sem abrir servidores ou conexões.

## Verificações realizadas

| Exercícios | Verificação |
|---|---|
| 1.1 | Tabelas, relacionamento, repetição da carga e rejeição de FK inválida, com adaptador SQLite |
| 1.2 | Três inserções, consulta, atualização e remoção de registro antigo, com adaptador SQLite |
| 1.3 | Cinco decisões CP/AP; geração de decisoes_cap.md |
| 2.1 | Inventário CRUD e rejeição de IP duplicado, com mongomock |
| 2.2–2.3 | 23 eventos simulados, totais 10/5/3 por IP, filtros combinados e ordenação |
| 3.1–3.2 | CRUD, nível 1–5 e comparação da injeção: três registros versus zero, com adaptador SQLite |
| 3.3 | Dez alertas: severidades 3 críticas, 4 altas, 2 médias e 1 baixa |
| 4.1 | Treino Random Forest, métricas e previsão positiva de phishing |
| 4.2 | Isolation Forest marca as amostras 5 e 8 como anomalias, preservando contamination=0.25 |
| 4.3 | Matriz [[8,0],[1,1]] e cálculo das métricas |
| 6.1 | CRUD em memória, duplicidade, nível inválido, JSON inválido e status HTTP |
| 6.2 | Checklist de senha e rejeição de corpo ausente, inválido ou campo não textual |
| 6.3 | IP público, privado, bloqueado e malformado |
| 7.1 | Incidentes CRUD, ObjectId inválido/inexistente e falha do banco sem detalhes internos |
| 7.2 | Quinze incidentes; paginação sem sobreposição; filtros combinados; ordenação; entradas inválidas |
| 7.3 | CRUD, duplicidade 409, ausente 404, corpo inválido 400 e falha 500 genérica |
| 8.1 | Payload script escapado no HTML, preservando o texto visível após decodificação das entidades |
| 8.2 | Login parametrizado, 401 igual para usuário ausente/senha errada, sucesso e limite 429 |
| 8.3 | Cinco achados e geração de auditoria.md |
| 10.1 | Resposta NVD controlada, CVSS, 404, lista vazia e timeout |
| 10.2 | Paginação GitHub, salvamento JSON pelo menu, 403/429/404 e erros de conexão/timeout |
| 10.3 | Três consultas, um cache hit, um IP interno; retry 429 com backoff 1s/2s simulado |
| 12.1–12.3 | Cinco folds; torneio; GridSearch; persistência; previsão e rejeição de arquivo adulterado |
| 13.1 | Histórico entre turnos no modo simulado e comando /sair |
| 13.2 | Fallback 1 NORMAL, 1 SUSPEITO e 1 CRITICO; rejeição de saída inválida ou rebaixamento |
| 13.3 | Relatório com modo simulado explicitado e limites da mitigação |

As execuções diretas dos exercícios sem serviços externos estão registradas em EXECUCOES.md.

## Limites da validação

- Não havia MySQL em 127.0.0.1:3306 nem MongoDB em 127.0.0.1:27017.
  Nenhum sucesso de integração com esses servidores reais é afirmado.
- O adaptador SQLite dos testes traduz placeholders, tipos e algumas expressões para exercitar
  lógica e integridade relacional. Ele não valida integralmente o dialeto MySQL ou o driver em um servidor.
- mongomock valida os fluxos locais de documentos, índice único, agregação e paginação;
  não comprova comportamento de rede, concorrência ou um cluster MongoDB real.
- APIs NVD, GitHub e IPinfo foram testadas com respostas controladas; não foram consultadas ao vivo.
- A API OpenAI não foi chamada. O relatório de prompt injection identifica explicitamente a simulação.
  Não há alegação de teste de resistência de um modelo remoto.
- O teste XSS verifica o HTML retornado pelo cliente de teste Flask; não foi aberto um navegador.
- Senhas de teste são geradas em memória; não há credenciais literais nos arquivos.
- As métricas de ML são resultados didáticos dos pequenos conjuntos fornecidos pela apostila.

Para repetir os testes: instale requirements.txt e mongomock; execute
`python -m unittest discover -s testes -v` dentro de exercicios.
