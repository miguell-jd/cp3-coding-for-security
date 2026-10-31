import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

"""Auditoria estática do trecho didático da seção 8.6; não executa o código vulnerável.
O segredo literal do enunciado é omitido para respeitar a política de credenciais.
"""
FALHAS = [
 ('SQL Injection', 'A05 — Injection',
  'A consulta concatena nome diretamente em SELECT de users.',
  'Usar SELECT * FROM users WHERE nome=%s e passar (nome,) separadamente.'),
 ('XSS', 'A05 — Injection',
  'O retorno HTML interpola nome e str(dados) sem escape.',
  'Usar template Jinja2 com escape automático em todos os campos, inclusive dados do banco.'),
 ('Debug e exposição da aplicação', 'A02 — Security Misconfiguration',
  'app.run ativa debug e escuta em todas as interfaces.',
  'Desativar debug; restringir exposição e configurar execução de produção.'),
 ('Segredo no código', 'A04/A02 — Cryptographic Failures / Security Misconfiguration',
  'SENHA_DB contém uma credencial literal no enunciado.',
  'Ler os.environ.get("MYSQL_PASSWORD") e trocar a credencial exposta.'),
 ('Ausência de logs', 'A09 — Security Logging & Alerting Failures',
  'As rotas não registram acessos nem tentativas com erro.',
  'Registrar acessos e falhas com logging, sem senhas, tokens ou consultas com dados sensíveis.')]

def main():
    linhas = ['# Auditoria do exercício 8.3','',
      'Mapeamento da edição OWASP 2025 conforme a seção 8.2 da apostila. O código vulnerável foi analisado estaticamente; a credencial literal não é reproduzida.','']
    for i,(nome,categoria,evidencia,correcao) in enumerate(FALHAS,1):
        linhas += [f'## {i}. {nome}',f'Categoria: {categoria}.',f'Evidência: {evidencia}',f'Correção: {correcao}','']
    conclusao = 'Conclusão: as cinco falhas exigem parametrização SQL, escape HTML, configuração segura, segredos via ambiente e registro de acessos e erros.'
    linhas.append(conclusao)
    Path(__file__).with_name('auditoria.md').write_text('\n'.join(linhas)+'\n',encoding='utf-8')
    print(conclusao)

if __name__ == '__main__':
    main()
