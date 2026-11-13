import chromadb
import ollama
from sentence_transformers import SentenceTransformer
from config import (PASTA_BANCO, NOME_COLECAO, MODELO_EMB, MODELO_LLM, TOP_K,
                    LIMIAR_DISTANCIA)

emb = SentenceTransformer(MODELO_EMB)
colecao = chromadb.PersistentClient(path=PASTA_BANCO).get_collection(NOME_COLECAO)

RECUSA = "Não encontrei essa informação nos documentos."

INSTRUCOES = (
    "Você é um assistente que responde em português do Brasil.\n"
    "Use APENAS o CONTEXTO fornecido para responder. Não use conhecimento externo.\n"
    f"Se a resposta não estiver no contexto, responda exatamente: {RECUSA}\n"
    "Seja objetivo, não invente informações e indique entre colchetes "
    "o(s) documento(s) que usou, por exemplo [arquivo.pdf]."
)


def recuperar(pergunta, k=TOP_K):
    vetor = emb.encode([pergunta], normalize_embeddings=True).tolist()
    busca = colecao.query(query_embeddings=vetor, n_results=k)
    docs = busca["documents"][0]
    metas = busca["metadatas"][0]
    dists = busca["distances"][0]
    return [
        {"texto": t, "fonte": m["fonte"], "distancia": d}
        for t, m, d in zip(docs, metas, dists)
    ]


def montar_contexto(trechos):
    return "\n---\n".join(f"[{t['fonte']}]\n{t['texto']}" for t in trechos)


def gerar(pergunta, trechos):
    r = ollama.chat(
        model=MODELO_LLM,
        messages=[
            {"role": "system", "content": INSTRUCOES},
            {"role": "user", "content": (
                f"CONTEXTO:\n{montar_contexto(trechos)}\n\n"
                f"PERGUNTA: {pergunta}"
            )},
        ],
        options={"temperature": 0},
    )
    return r["message"]["content"].strip()


def perguntar(pergunta, k=TOP_K, limiar=LIMIAR_DISTANCIA):
    trechos = [t for t in recuperar(pergunta, k) if t["distancia"] <= limiar]
    if not trechos:
        return RECUSA, []
    resposta = gerar(pergunta, trechos)
    # o modelo às vezes varia a frase ("...nos documentos fornecidos.")
    if resposta.lower().startswith("não encontrei"):
        return RECUSA, []
    return resposta, trechos
