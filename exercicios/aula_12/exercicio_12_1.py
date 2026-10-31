import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dados_ml import X_REDE as X, Y_REDE as y
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold

def criar_pipeline():
    return Pipeline([('scaler',StandardScaler()),('clf',RandomForestClassifier(random_state=42))])

def avaliar():
    cv = StratifiedKFold(n_splits=5,shuffle=True,random_state=42)
    scores = cross_val_score(criar_pipeline(),X,y,cv=cv,scoring='accuracy')
    print('Folds:',scores)
    print(f'Acurácia: {scores.mean():.2f} (+/- {scores.std():.2f})')
    return scores

if __name__ == '__main__':
    avaliar()
