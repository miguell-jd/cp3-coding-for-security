import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from apoio import mysql, preparar_usuarios

def buscar_inseguro(nome):
    # Única query deliberadamente vulnerável; somente laboratório local.
    with mysql() as con, con.cursor(dictionary=True) as cur:
        cur.execute("SELECT * FROM usuarios WHERE nome='" + nome + "'")
        return cur.fetchall()

def buscar_seguro(nome):
    with mysql() as con, con.cursor(dictionary=True) as cur:
        cur.execute('SELECT * FROM usuarios WHERE nome=%s',(nome,))
        return cur.fetchall()

def main():
    import os
    if os.environ.get('MYSQL_HOST','127.0.0.1') not in ('127.0.0.1','localhost','::1'):
        raise ValueError('PoC permitida apenas no banco local de laboratório')
    with mysql() as con: preparar_usuarios(con)
    entrada = "' OR '1'='1"
    a,b = buscar_inseguro(entrada),buscar_seguro(entrada)
    texto = (f'[INSEGURO] {len(a)} usuários retornados (VAZAMENTO!)\n'
             f'[SEGURO] {len(b)} usuários retornados (defesa OK)\n'
             'Conclusão: a query parametrizada tratou a entrada como texto literal.\n')
    print(texto)
    Path(__file__).with_name('resultado_sqli.md').write_text(texto,encoding='utf-8')

if __name__ == '__main__':
    main()
