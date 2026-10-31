import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from apoio import mysql

SCHEMA = [
    """CREATE TABLE IF NOT EXISTS ativos (
    id INT AUTO_INCREMENT PRIMARY KEY, nome VARCHAR(100) NOT NULL,
    ip VARCHAR(45) UNIQUE NOT NULL, tipo VARCHAR(50), criticidade VARCHAR(20))""",
    """CREATE TABLE IF NOT EXISTS vulnerabilidades (
    id INT AUTO_INCREMENT PRIMARY KEY, cve_id VARCHAR(30) UNIQUE NOT NULL,
    descricao TEXT, severidade ENUM('Baixa','Media','Alta','Critica'),
    cvss DECIMAL(3,1), CHECK (cvss BETWEEN 0 AND 10))""",
    """CREATE TABLE IF NOT EXISTS ativo_vulnerabilidade (
    ativo_id INT NOT NULL, vuln_id INT NOT NULL, status VARCHAR(20) DEFAULT 'aberta',
    detectada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (ativo_id,vuln_id),
    FOREIGN KEY (ativo_id) REFERENCES ativos(id),
    FOREIGN KEY (vuln_id) REFERENCES vulnerabilidades(id))"""]

def main():
    with mysql() as con, con.cursor() as cur:
        for sql in SCHEMA:
            cur.execute(sql)
        cur.execute('INSERT INTO ativos (nome,ip,tipo,criticidade) VALUES (%s,%s,%s,%s) ON DUPLICATE KEY UPDATE nome=VALUES(nome)',
                    ('SRV-WEB01','192.168.1.10','servidor','alta'))
        cur.execute('INSERT INTO vulnerabilidades (cve_id,descricao,severidade,cvss) VALUES (%s,%s,%s,%s) ON DUPLICATE KEY UPDATE cvss=VALUES(cvss)',
                    ('CVE-2024-001','Vulnerabilidade de teste da apostila','Alta',8.5))
        cur.execute('SELECT id FROM ativos WHERE ip=%s', ('192.168.1.10',))
        ativo = cur.fetchone()[0]
        cur.execute('SELECT id FROM vulnerabilidades WHERE cve_id=%s', ('CVE-2024-001',))
        vuln = cur.fetchone()[0]
        cur.execute('INSERT INTO ativo_vulnerabilidade (ativo_id,vuln_id) VALUES (%s,%s) ON DUPLICATE KEY UPDATE ativo_id=VALUES(ativo_id)', (ativo,vuln))
        cur.execute('SELECT a.nome,v.cve_id,v.severidade,v.cvss FROM ativos a JOIN ativo_vulnerabilidade av ON av.ativo_id=a.id JOIN vulnerabilidades v ON v.id=av.vuln_id WHERE a.id=%s', (ativo,))
        print(cur.fetchall())

if __name__ == '__main__':
    main()
