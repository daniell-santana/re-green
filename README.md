# Case re.green, apresentação com demonstração ao vivo

Apresentação HTML fluida do case de Product Owner com foco em IA, com uma
extração estruturada ao vivo no slide 10, rodando num backend Flask que
chama a API da Anthropic. A chave de API fica só no servidor, nunca no
navegador.

## Estrutura

- `app.py`, backend Flask, serve a página e o endpoint `/api/extract`
- `static/index.html`, a apresentação
- `requirements.txt`, dependências Python
- `render.yaml`, configuração opcional para deploy por blueprint no Render

## Rodar localmente

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sua-chave"
python app.py
```

Abrir http://localhost:5000

## Deploy no Render.com

1. Suba esta pasta para um repositório no GitHub, ou conecte a pasta do jeito que o seu plano do Render permitir.
2. No painel do Render, escolha New, Web Service, e aponte para o repositório.
3. Environment: Python 3.
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `gunicorn app:app`
6. Em Environment Variables, adicione `ANTHROPIC_API_KEY` com sua chave real. Nunca commitar a chave no repositório.
7. Deploy. A URL pública do Render já serve a apresentação inteira, e o slide 10 chama o backend normalmente.

Se preferir usar o arquivo `render.yaml`, o Render lê essa configuração automaticamente ao criar o serviço a partir do blueprint, e só vai pedir o valor de `ANTHROPIC_API_KEY` na hora do deploy.

## Trocar de provedor de LLM

A função `get_client()` em `app.py` usa o SDK da Anthropic. Para usar outro provedor, troque essa função e o corpo de `extract()` pelo client e pelo formato de resposta do provedor escolhido, mantendo o mesmo `PROMPT_TEMPLATE` e `SCHEMA_HINT`, já que é isso que preserva o schema e a citação de fonte usados no resto da apresentação.

## Segurança

- A chave de API nunca aparece no HTML nem é enviada ao navegador.
- O endpoint corta o texto de entrada em 6000 caracteres antes de enviar ao modelo.
- Erros do modelo ou de rede voltam como JSON com uma mensagem curta, sem expor detalhes internos ao navegador além do necessário para depuração.
