# Exercícios — Coding for Security, 2º semestre

30 exercícios das aulas 1, 2, 3, 4, 6, 7, 8, 10, 12 e 13.
Excluídas as aulas 5, 9 e 14 (Check Points/projeto) e 11 (Docker).
Base: os enunciados da apostila_2semestre.md e fundamentos da apostila_1semestre.md.
Os módulos de apoio apenas compartilham as implementações usadas nos exercícios.

## Preparar e executar

Requer Python 3.11+. Na pasta exercicios, execute:

```text
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python aula_4/exercicio_4_1.py
python aula_6/exercicio_6_1.py
```

Cada script pode ser executado diretamente por caminho ou importado sem iniciar servidores.
APIs usam http://127.0.0.1:5000; execute uma por vez, sem debug.

## Credenciais e serviços

MySQL precisa estar acessível, com o banco `seguranca` previamente criado e permissão para tabelas.
Configuração exclusivamente via ambiente: MYSQL_HOST (127.0.0.1), MYSQL_USER (root),
MYSQL_PASSWORD (sem padrão), MYSQL_DATABASE (seguranca).
MongoDB: MONGO_URI (mongodb://localhost:27017/), banco seguranca.
As APIs não conectam aos bancos ao serem importadas.
Para criar a tabela da API 7.3: `python aula_7/exercicio_7_3.py --preparar`.
Para a API de login: configure LOGIN_USER e LOGIN_PASSWORD via ambiente e execute
`python aula_8/exercicio_8_2.py --preparar`; depois execute sem a opção para servir.
O hash SHA-256 é demonstração limitada ao hashlib ensinado, não um KDF de produção.
O limite de login usa memória por IP (5 falhas/60s), adequado ao laboratório com um processo.
O mesmo erro 401 para conta ausente e senha incorreta evita enumeração por mensagem.

## Dados, relatórios e observações dos enunciados

- Aula 1.1 cria tabelas e relaciona SRV-WEB01 à CVE-2024-001 (Alta, 8.5).
- Aula 1.2 insere três alertas, conforme o pedido; a saída ilustrativa da apostila soma quatro
  e inclui um alerta médio, portanto não pode resultar apenas das três inserções em tabela vazia.
- Aula 2 inclui auth.log **simulado** com 23 linhas, pois o arquivo da GS não foi fornecido.
  Aceita arquivo real como argumento no exercício 2.2. Reexecuções acrescentam eventos.
- Aula 3.2 é a única consulta deliberadamente concatenada, para a PoC defensiva local.
  Gera resultado_sqli.md ao executar contra MySQL.
- Aulas 1.2 e 3.3 operam na mesma tabela alertas: os relatórios incluem registros já existentes.
  Para reproduzir contagens isoladas, use um banco de laboratório vazio em MYSQL_DATABASE.
- Aula 4.2 preserva contamination=0.25. Em nove amostras o modelo pode identificar três
  anomalias; a saída real não é adulterada para reproduzir o exemplo com apenas duas.
- Aula 7.2: `--popular` insere 15 incidentes. Paginação pagina>=1, tamanho=1..100 (padrão 10),
  filtros severidade=baixa|media|alta|critica e status=aberto|em_analise|resolvido;
  resposta {dados,pagina,tamanho,total,paginas}, ordenada por criado_em descendente.
- Aula 8.1 usa formulário na rota /. Jinja2 escapa o texto de cada alerta.
- Aula 8.3 gera auditoria.md, seguindo a numeração OWASP 2025 apresentada na apostila.
  O segredo literal do trecho vulnerável foi omitido por exigência do pedido.
- Aula 10 usa NVD, GitHub e IPinfo via requests, com timeout e tratamento de erros.
  GITHUB_TOKEN e IPINFO_TOKEN opcionais, apenas via ambiente. Não há chamadas de rede ao importar.
- Aula 12 usa exatamente as 15 amostras do enunciado. Normalização fica dentro do Pipeline.
  O torneio e a busca usam cinco folds, sem avaliação independente após seleção.
  Exercício 12.3 salva modelo e SHA-256; só carrega após comparar o hash.
- Aula 13 usa o formato de chamada ensinado: chat.completions, modelo padrão gpt-4o-mini,
  configurável por OPENAI_MODEL. OPENAI_API_KEY é lida do ambiente; sem chave, usa simulação
  por regras explicitamente identificada. Não envie segredos ou dados pessoais em logs.
  Exercício 13.2 aceita arquivo de logs como argumento; 13.3 gera prompt_injection.md.

## Validação

Consulte VALIDACAO.md para resultados e limites da execução realizada nesta entrega.
Os testes em testes/test_exercicios.py usam unittest da biblioteca padrão; MongoDB e
MySQL simulados permitem testar contratos e erros sem fingir validação de servidores reais.
Para os testes MongoDB, instale a dependência de teste: `python -m pip install mongomock`.
Execute `python -m unittest discover -s testes -v`.
