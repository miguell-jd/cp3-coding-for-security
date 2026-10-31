import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dados_ml import ACESSOS
from sklearn.ensemble import IsolationForest

def detectar():
    modelo = IsolationForest(contamination=0.25,random_state=42)
    rotulos = modelo.fit_predict(ACESSOS)
    for i,(amostra,rotulo) in enumerate(zip(ACESSOS,rotulos)):
        print(f'Amostra {i}: {amostra.tolist()} ->', 'ANOMALIA' if rotulo == -1 else 'Normal')
    print('Anomalias:',ACESSOS[rotulos == -1].tolist())
    print('Com 9 amostras, contamination=0.25 pode marcar uma terceira amostra além das duas extremas; os rótulos são os calculados pelo modelo.')
    return rotulos

if __name__ == '__main__':
    detectar()
