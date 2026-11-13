PASTA_DOCS = "docs"
PASTA_BANCO = "banco"
NOME_COLECAO = "docs"

MODELO_EMB = "paraphrase-multilingual-MiniLM-L12-v2"
MODELO_LLM = "llama3.2"
MODELO_JUIZ = "qwen2.5:7b"

# O modelo de embeddings lê no máximo 128 tokens; ~400 caracteres cabem com folga.
TAMANHO_CHUNK = 400
SOBREPOSICAO = 80
TOP_K = 4

# Distância cosseno máxima (0 = idêntico, 2 = oposto) para um trecho ser usado.
# Se nenhum trecho passar, o RAG recusa sem chamar o LLM. Calibre com debug.py.
LIMIAR_DISTANCIA = 0.5
