import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score, accuracy_score

def avaliar():
    real = [0,0,0,0,0,0,0,0,1,1]
    pred = [0,0,0,0,0,0,0,0,0,1]
    matriz = confusion_matrix(real,pred,labels=[0,1])
    print('Matriz:',matriz.tolist(), '(linhas=reais, colunas=previstos; 0=normal, 1=ataque)')
    print(f'Precisão: {precision_score(real,pred):.2f} | Recall: {recall_score(real,pred):.2f} | F1: {f1_score(real,pred):.2f} | Acurácia: {accuracy_score(real,pred):.2f}')
    print('Oito normais corretos elevam a acurácia a 90%, ocultando o falso negativo.')
    print('O recall de 50% revela que um dos dois ataques não foi detectado.')
    print('No SOC, priorizar recall reduz ataques despercebidos; a precisão monitora o custo dos falsos positivos.')
    return matriz

if __name__ == '__main__':
    avaliar()
