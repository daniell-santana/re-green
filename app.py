import json
import os

from flask import Flask, jsonify, request, send_from_directory

import anthropic

app = Flask(__name__, static_folder="static", static_url_path="")

SCHEMA_HINT = {
    "area_ha": "string",
    "cadeia_dominial": "string curta",
    "sobreposicao_gleba_publica": "string curta",
    "confianca": "alta | media | baixa",
    "fonte": "trecho exato do texto que sustenta a resposta",
    "classificacao": "convivivel | corrigivel | impeditivo",
    "justificativa": "uma frase curta",
}

PROMPT_TEMPLATE = """Voce e um assistente de apoio a diligencia fundiaria, em um caso ficticio
de restauracao florestal no Brasil.

Leia o trecho de matricula abaixo, dados ficticios criados apenas para demonstracao.
Devolva APENAS um objeto JSON, sem texto antes ou depois, no formato:
{schema}

Regras:
- Baseie cada campo apenas no texto abaixo.
- Se a informacao nao estiver no texto, escreva "nao informado".
- O campo fonte deve citar o trecho exato do texto que sustenta a resposta.
- confianca deve ser "baixa" sempre que houver ambiguidade ou informacao faltando.

Trecho da matricula:
\"\"\"
{texto}
\"\"\"
"""

MODEL = os.environ.get("EXTRACAO_MODEL", "claude-sonnet-4-6")
MAX_CHARS = 6000

_client = None


def get_client():
    global _client
    if _client is None:
        # Le ANTHROPIC_API_KEY do ambiente, nunca de um valor fixo no codigo.
        _client = anthropic.Anthropic()
    return _client


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/extract", methods=["POST"])
def extract():
    payload = request.get_json(silent=True) or {}
    texto = (payload.get("texto") or "").strip()
    if not texto:
        return jsonify({"error": "texto vazio"}), 400
    texto = texto[:MAX_CHARS]

    prompt = PROMPT_TEMPLATE.format(
        schema=json.dumps(SCHEMA_HINT, ensure_ascii=False, indent=2),
        texto=texto,
    )

    try:
        resposta = get_client().messages.create(
            model=MODEL,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as exc:  # falha de rede, chave invalida, limite de uso, etc.
        return jsonify({"error": "falha ao chamar o modelo", "detail": str(exc)}), 502

    bruto = "".join(
        bloco.text for bloco in resposta.content if getattr(bloco, "type", "") == "text"
    )
    inicio, fim = bruto.find("{"), bruto.rfind("}")
    if inicio == -1 or fim == -1:
        return jsonify({"error": "resposta sem JSON reconhecivel", "raw": bruto}), 502

    try:
        resultado = json.loads(bruto[inicio : fim + 1])
    except json.JSONDecodeError:
        return jsonify({"error": "JSON invalido na resposta", "raw": bruto}), 502

    return jsonify(resultado)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
