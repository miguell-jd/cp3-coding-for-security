import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

"""GET /api/incidentes: pagina>=1; tamanho=1..100 (padrão 10).
Filtros combináveis: severidade=baixa|media|alta|critica;
status=aberto|em_analise|resolvido. Ordenação: criado_em descendente.
Execute com --popular para inserir 15 incidentes de laboratório e sair.
"""
from incidentes_api import criar_app, popular
app = criar_app(paginada=True)
if __name__ == '__main__':
    if '--popular' in sys.argv: popular()
    else: app.run(debug=False)
