# Auditoria do exercício 8.3

Mapeamento da edição OWASP 2025 conforme a seção 8.2 da apostila. O código vulnerável foi analisado estaticamente; a credencial literal não é reproduzida.

## 1. SQL Injection
Categoria: A05 — Injection.
Evidência: A consulta concatena nome diretamente em SELECT de users.
Correção: Usar SELECT * FROM users WHERE nome=%s e passar (nome,) separadamente.

## 2. XSS
Categoria: A05 — Injection.
Evidência: O retorno HTML interpola nome e str(dados) sem escape.
Correção: Usar template Jinja2 com escape automático em todos os campos, inclusive dados do banco.

## 3. Debug e exposição da aplicação
Categoria: A02 — Security Misconfiguration.
Evidência: app.run ativa debug e escuta em todas as interfaces.
Correção: Desativar debug; restringir exposição e configurar execução de produção.

## 4. Segredo no código
Categoria: A04/A02 — Cryptographic Failures / Security Misconfiguration.
Evidência: SENHA_DB contém uma credencial literal no enunciado.
Correção: Ler os.environ.get("MYSQL_PASSWORD") e trocar a credencial exposta.

## 5. Ausência de logs
Categoria: A09 — Security Logging & Alerting Failures.
Evidência: As rotas não registram acessos nem tentativas com erro.
Correção: Registrar acessos e falhas com logging, sem senhas, tokens ou consultas com dados sensíveis.

Conclusão: as cinco falhas exigem parametrização SQL, escape HTML, configuração segura, segredos via ambiente e registro de acessos e erros.
