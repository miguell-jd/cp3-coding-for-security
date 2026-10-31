import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from apoio import mysql, ALERTAS

DADOS = [(tipo,ip,sev) for tipo,ip,sev in [
 ('BRUTE_FORCE','185.220.101.1','critica'),('BRUTE_FORCE','185.220.101.1','critica'),
 ('BRUTE_FORCE','185.220.101.1','alta'),('BRUTE_FORCE','185.220.101.1','alta'),
 ('PORT_SCAN','45.33.32.156','alta'),('PORT_SCAN','45.33.32.156','media'),
 ('PORT_SCAN','45.33.32.156','baixa'),('XSS','91.240.118.172','alta'),
 ('XSS','91.240.118.172','media'),('SQLI','203.0.113.10','critica')]]

def main():
    with mysql() as con, con.cursor() as cur:
        cur.execute(ALERTAS)
        cur.executemany('INSERT INTO alertas (tipo,ip_origem,severidade) VALUES (%s,%s,%s)',DADOS)
        for titulo,sql in [
          ('Por severidade','SELECT severidade,COUNT(*) total FROM alertas GROUP BY severidade ORDER BY total DESC'),
          ('Por tipo','SELECT tipo,COUNT(*) total FROM alertas GROUP BY tipo ORDER BY total DESC'),
          ('Top IPs','SELECT ip_origem,COUNT(*) total FROM alertas GROUP BY ip_origem ORDER BY total DESC LIMIT 5')]:
            cur.execute(sql)
            print('===',titulo,'===')
            for linha in cur.fetchall(): print(*linha,sep=': ')

if __name__ == '__main__':
    main()
