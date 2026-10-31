import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from apoio import mysql, ALERTAS

def main():
    with mysql() as con, con.cursor(dictionary=True) as cur:
        cur.execute(ALERTAS)
        primeiro = None
        for linha in [('BRUTE_FORCE','185.220.101.1','alta'), ('PORT_SCAN','45.33.32.156','alta'), ('SQLI','91.240.118.172','critica')]:
            cur.execute('INSERT INTO alertas (tipo,ip_origem,severidade) VALUES (%s,%s,%s)', linha)
            if primeiro is None:
                primeiro = cur.lastrowid
        cur.execute('SELECT * FROM alertas WHERE severidade=%s', ('alta',))
        print('Alta:', cur.fetchall())
        cur.execute('UPDATE alertas SET status=%s WHERE id=%s', ('resolvido',primeiro))
        cur.execute('SELECT severidade,COUNT(*) total FROM alertas GROUP BY severidade ORDER BY total DESC')
        print('Por severidade:',cur.fetchall())
        cur.execute('DELETE FROM alertas WHERE criado_em < DATE_SUB(NOW(), INTERVAL 90 DAY)')
        print('Antigos removidos:',cur.rowcount)

if __name__ == '__main__':
    main()
