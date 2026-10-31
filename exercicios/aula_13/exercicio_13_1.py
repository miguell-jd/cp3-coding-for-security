import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from openai import OpenAIError
from llm_apoio import cliente, chamar

def main():
    client = cliente()
    historico = [{'role':'system','content':'Você é um assistente de segurança. Explique conceitos e medidas defensivas.'}]
    if client is None: print('Modo simulado por regras: OPENAI_API_KEY ausente. Nenhuma chamada externa.')
    while True:
        try: pergunta = input('Você: ')
        except (EOFError,KeyboardInterrupt): break
        if pergunta.strip() == '/sair': break
        if not pergunta.strip(): continue
        historico.append({'role':'user','content':pergunta[:4000]})
        try:
            if client is not None: resposta = chamar(client,historico)
            else:
                contexto = ' '.join(m['content'].lower() for m in historico if m['role']=='user')
                if 'xss' in contexto:
                    resposta = 'XSS injeta scripts em páginas. Para prevenir, escape a saída HTML com Jinja2 e valide as entradas.'
                elif 'sql' in contexto: resposta = 'SQL Injection altera consultas construídas por concatenação. Use parâmetros %s separados dos valores.'
                else: resposta = 'Simulação limitada: pergunte sobre XSS ou SQL Injection; configure OPENAI_API_KEY para o chatbot da API.'
            historico.append({'role':'assistant','content':resposta})
            print('Assistente:',resposta)
        except (OpenAIError,ValueError,IndexError,AttributeError):
            historico.pop()
            print('Assistente: API indisponível. Tente novamente.')
    print('Assistente: Até logo!')
    return historico

if __name__ == '__main__':
    main()
