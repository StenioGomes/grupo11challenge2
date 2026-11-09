"""
ETAPA 4 DA INGESTÃO: embeddings (texto -> vetor).

Um modelo de embedding transforma um texto em um vetor de números (ex.:
1024 dimensões no bge-m3). Textos com significado parecido ficam próximos
nesse espaço, mesmo usando palavras diferentes: "reserva de emergência" e
"dinheiro guardado para imprevistos" ficam perto um do outro.

Decisões (detalhadas em docs/estrategia_embeddings.md):

- Modelo padrão: bge-m3 (via Ollama). É multilíngue, então funciona bem
  com a base em português + alguns documentos em inglês, e aceita textos
  longos (8192 tokens), folgado para chunks de ~250 tokens.
- Prefixos de tarefa: alguns modelos (família nomic, e5, mxbai) foram
  treinados para receber um prefixo diferente para DOCUMENTO e para
  PERGUNTA. Esquecer o prefixo piora a recuperação silenciosamente. O
  wrapper abaixo aplica o prefixo certo automaticamente.
- Mesmo modelo na ingestão e na consulta: obrigatório. Por isso o nome
  da coleção no Chroma inclui o nome do modelo.
- Baseline "hash": embedding lexical (bag-of-words com hashing) que roda
  sem Ollama. Não entende sinônimos; serve para testes automatizados e
  para COMPARAR com o modelo semântico na avaliação.
"""

from __future__ import annotations

import hashlib
import math
import re
import unicodedata

from langchain_core.embeddings import Embeddings

from . import config

# (prefixo_documento, prefixo_pergunta) por modelo
PREFIXOS: dict[str, tuple[str, str]] = {
    "nomic-embed-text": ("search_document: ", "search_query: "),
    "nomic-embed-text-v2-moe": ("search_document: ", "search_query: "),
    "mxbai-embed-large": ("", "Represent this sentence for searching relevant passages: "),
    "snowflake-arctic-embed": ("", "Represent this sentence for searching relevant passages: "),
    "bge-m3": ("", ""),
}


def _prefixos_do_modelo(modelo: str) -> tuple[str, str]:
    base = modelo.split(":")[0]  # "nomic-embed-text:latest" -> "nomic-embed-text"
    return PREFIXOS.get(base, ("", ""))


class EmbeddingsComPrefixo(Embeddings):
    """Envolve qualquer Embeddings do LangChain adicionando prefixos de tarefa."""

    def __init__(self, base: Embeddings, prefixo_doc: str, prefixo_query: str):
        self.base = base
        self.prefixo_doc = prefixo_doc
        self.prefixo_query = prefixo_query

    def embed_documents(self, textos: list[str]) -> list[list[float]]:
        return self.base.embed_documents([self.prefixo_doc + t for t in textos])

    def embed_query(self, texto: str) -> list[float]:
        return self.base.embed_query(self.prefixo_query + texto)


class EmbeddingsHash(Embeddings):
    """
    Baseline lexical offline: cada palavra (e bigrama) é mapeada por hash
    para uma das `dim` posições do vetor; o vetor é normalizado (norma 1).
    Similaridade de cosseno aqui ~ sobreposição de vocabulário.
    """

    def __init__(self, dim: int = 1024):
        self.dim = dim

    @staticmethod
    def _tokens(texto: str) -> list[str]:
        texto = unicodedata.normalize("NFKD", texto.lower())
        texto = "".join(c for c in texto if not unicodedata.combining(c))
        palavras = [p for p in re.findall(r"[a-z0-9]+", texto) if len(p) > 2]
        bigramas = [f"{a}_{b}" for a, b in zip(palavras, palavras[1:])]
        return palavras + bigramas

    def _vetor(self, texto: str) -> list[float]:
        v = [0.0] * self.dim
        for tok in self._tokens(texto):
            h = int(hashlib.md5(tok.encode()).hexdigest(), 16)
            v[h % self.dim] += 1.0 if (h >> 64) % 2 else -1.0
        norma = math.sqrt(sum(x * x for x in v)) or 1.0
        return [x / norma for x in v]

    def embed_documents(self, textos: list[str]) -> list[list[float]]:
        return [self._vetor(t) for t in textos]

    def embed_query(self, texto: str) -> list[float]:
        return self._vetor(texto)


def criar_embeddings(provedor: str = config.EMBEDDING_PROVIDER, modelo: str = config.EMBEDDING_MODEL) -> Embeddings:
    if provedor == "hash":
        return EmbeddingsHash()
    if provedor == "ollama":
        from langchain_ollama import OllamaEmbeddings

        base = OllamaEmbeddings(model=modelo, base_url=config.OLLAMA_BASE_URL)
        prefixo_doc, prefixo_query = _prefixos_do_modelo(modelo)
        if prefixo_doc or prefixo_query:
            return EmbeddingsComPrefixo(base, prefixo_doc, prefixo_query)
        return base
    raise ValueError(f"EMBEDDING_PROVIDER desconhecido: {provedor}")


def cosseno(a: list[float], b: list[float]) -> float:
    """Similaridade de cosseno: 1 = mesma direção, 0 = sem relação."""
    produto = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return produto / (na * nb) if na and nb else 0.0
