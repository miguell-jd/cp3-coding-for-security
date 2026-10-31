import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import requests

def consultar(cve):
    try:
        r = requests.get('https://services.nvd.nist.gov/rest/json/cves/2.0',params={'cveId':cve},timeout=15)
        if r.status_code == 404: return None
        r.raise_for_status()
        dados = r.json().get('vulnerabilities',[])
        if not dados: return None
        registro = dados[0]['cve']
        descricoes = registro.get('descriptions',[])
        descricao = next((d['value'] for d in descricoes if d['lang']=='en'),descricoes[0]['value'] if descricoes else 'Sem descrição')
        metricas = registro.get('metrics',{})
        score,severidade = None,'não informada'
        for versao in ('cvssMetricV40','cvssMetricV31','cvssMetricV30','cvssMetricV2'):
            if metricas.get(versao):
                metrica = metricas[versao][0]
                cvss = metrica['cvssData']
                score,severidade = cvss.get('baseScore'),cvss.get('baseSeverity',metrica.get('baseSeverity','não informada'))
                break
        return dict(id=registro['id'],descricao=descricao,cvss=score,severidade=severidade)
    except requests.exceptions.Timeout: print('Timeout ao consultar NVD')
    except (requests.exceptions.RequestException,ValueError,KeyError,IndexError,TypeError): print('Falha ao consultar NVD ou resposta inválida')
    return None

if __name__ == '__main__':
    resultado = consultar(sys.argv[1] if len(sys.argv)>1 else 'CVE-2021-44228')
    if resultado:
        print(resultado['id'])
        print(f"  CVSS: {resultado['cvss']} ({resultado['severidade']})")
        print('  Descrição:',resultado['descricao'])
    else: print('CVE não encontrada ou consulta indisponível')
