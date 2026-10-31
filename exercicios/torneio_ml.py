from dados_ml import X_REDE as X, Y_REDE as y
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold, GridSearchCV

def torneio():
    cv = StratifiedKFold(n_splits=5,shuffle=True,random_state=42)
    modelos = {'RandomForest':RandomForestClassifier(random_state=42),
               'SVM':SVC(),'KNN':KNeighborsClassifier(n_neighbors=3)}
    grades = {'RandomForest':{'clf__max_depth':[None,3,5],'clf__n_estimators':[50,100]},
              'SVM':{'clf__C':[.1,1,10],'clf__kernel':['linear','rbf']},
              'KNN':{'clf__n_neighbors':[1,3,5],'clf__weights':['uniform','distance']}}
    pipelines,resultados = {},{}
    for nome,modelo in modelos.items():
        pipe = Pipeline([('scaler',StandardScaler()),('clf',modelo)])
        scores = cross_val_score(pipe,X,y,cv=cv,scoring='accuracy')
        pipelines[nome] = pipe
        resultados[nome] = float(scores.mean())
        print(f'{nome}: {scores.mean():.2f} (+/- {scores.std():.2f})')
    vencedor = max(resultados,key=resultados.get)
    print('Vencedor:',vencedor,'(empate: ordem RandomForest, SVM, KNN)')
    busca = GridSearchCV(pipelines[vencedor],grades[vencedor],cv=cv,scoring='accuracy')
    busca.fit(X,y)
    print('Melhores parâmetros:',busca.best_params_)
    print('Score CV após busca:',busca.best_score_)
    print('Resultados didáticos: 15 amostras; seleção e ajuste usam os mesmos folds, sem estimativa independente de generalização.')
    return busca.best_estimator_, resultados
