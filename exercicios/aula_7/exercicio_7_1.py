import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from incidentes_api import criar_app
app = criar_app()
if __name__ == '__main__':
    app.run(debug=False)
