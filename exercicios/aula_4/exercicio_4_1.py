import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dados_ml import X_PHISHING as X, Y_PHISHING as y
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

def treinar():
    xtr,xte,ytr,yte = train_test_split(X,y,test_size=.3,random_state=42)
    modelo = RandomForestClassifier(random_state=42)
    modelo.fit(xtr,ytr)
    pred = modelo.predict(xte)
    print('Acurácia:',accuracy_score(yte,pred))
    print(classification_report(yte,pred,labels=[0,1],target_names=['Legítimo','Phishing'],zero_division=0))
    print('Caso novo [11,1,1,1,7] ->', 'Phishing' if modelo.predict([[11,1,1,1,7]])[0] else 'Legítimo')
    return modelo

if __name__ == '__main__':
    treinar()
