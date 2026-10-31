import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import hashlib
import joblib
from torneio_ml import torneio

def sha256(arquivo):
    with open(arquivo,'rb') as f:
        h = hashlib.sha256()
        for bloco in iter(lambda:f.read(65536),b''): h.update(bloco)
    return h.hexdigest()

def carregar_verificado(arquivo, hash_esperado):
    # Carregar somente o modelo local gerado aqui. Hash não autentica arquivos de terceiros.
    if sha256(arquivo) != hash_esperado:
        raise ValueError('ALERTA: arquivo do modelo foi modificado!')
    return joblib.load(arquivo)

def main():
    modelo,_ = torneio()
    arquivo = Path(__file__).with_name('modelo_seguranca.pkl')
    joblib.dump(modelo,arquivo)
    digest = sha256(arquivo)
    hashfile = arquivo.with_suffix('.sha256')
    hashfile.write_text(digest,encoding='utf-8')
    print('Modelo salvo:',arquivo.name)
    print('Hash SHA-256:',digest)
    print('Recarregando e verificando integridade...')
    recarregado = carregar_verificado(arquivo,hashfile.read_text(encoding='utf-8').strip())
    print('Hash confere: modelo íntegro. Previsão de teste:',recarregado.predict([[64000,4444,10.0]]).tolist())

if __name__ == '__main__':
    main()
