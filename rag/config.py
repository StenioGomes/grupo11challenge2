"""
Configuração central do projeto.

Tudo que é "parâmetro de experimento" (modelo de embedding, tamanho do
chunk, k da busca...) fica aqui. Cada valor pode ser sobrescrito por uma
variável de ambiente ou pelo arquivo .env, o que facilita comparar
configurações sem mexer no código.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from dotenv import load_dotenv

# --------------------------------------------------------------------------
# Caminhos
# --------------------------------------------------------------------------
RAIZ = Path(__file__).resolve().parent.parent
load_dotenv(RAIZ / ".env")

CATALOGO = RAIZ / "fontes" / "catalogo.yaml"
DIR_BRUTOS = RAIZ / "data" / "raw"            # documentos baixados (PDF/HTML)
DIR_PROCESSADOS = RAIZ / "data" / "processed"  # chunks em JSONL, para inspeção
DIR_CHROMA = RAIZ / "chroma_db"               # banco vetorial persistente
DIR_SAIDAS = RAIZ / "saidas"                  # relatórios, demonstrações, avaliação


def _env(nome: str, padrao):
    """Lê uma variável de ambiente convertendo para o tipo do valor padrão."""
    valor = os.getenv(nome)
    if valor is None or valor == "":
        return padrao
    if isinstance(padrao, bool):
        return valor.strip().lower() in {"1", "true", "sim", "yes"}
    if isinstance(padrao, int):
        return int(valor)
    if isinstance(padrao, float):
        return float(valor)
    return valor


# --------------------------------------------------------------------------
# Modelos (Ollama local)
# --------------------------------------------------------------------------
OLLAMA_BASE_URL = _env("OLLAMA_BASE_URL", "http://localhost:11434")

# "ollama" = modelo semântico real; "hash" = baseline lexical offline (testes/comparação)
EMBEDDING_PROVIDER = _env("EMBEDDING_PROVIDER", "ollama")

# bge-m3 é multilíngue (bom para português) e aceita textos longos.
# Alternativas: "nomic-embed-text" (inglês, usa prefixos), "nomic-embed-text-v2-moe".
EMBEDDING_MODEL = _env("EMBEDDING_MODEL", "bge-m3" if EMBEDDING_PROVIDER == "ollama" else "lexical-1024")

# Modelo gerador. llama3.1:8b funciona; qwen2.5:7b costuma ir melhor em PT-BR.
LLM_MODEL = _env("LLM_MODEL", "llama3.1:8b")
LLM_TEMPERATURE = _env("LLM_TEMPERATURE", 0.0)
LLM_NUM_CTX = _env("LLM_NUM_CTX", 8192)        # janela de contexto (tokens) no Ollama
LLM_MAX_TOKENS = _env("LLM_MAX_TOKENS", 600)   # tamanho máximo da resposta

# --------------------------------------------------------------------------
# Chunking (ver docs/estrategia_chunking.md)
# --------------------------------------------------------------------------
CHUNK_SIZE = _env("CHUNK_SIZE", 1000)        # caracteres (~200-250 tokens em PT)
CHUNK_OVERLAP = _env("CHUNK_OVERLAP", 150)   # 15% de sobreposição
CHUNK_MINIMO = _env("CHUNK_MINIMO", 80)      # descarta fragmentos curtos demais (ruído)

# --------------------------------------------------------------------------
# Recuperação (ver docs/arquitetura.md)
# --------------------------------------------------------------------------
TOP_K = _env("TOP_K", 6)                     # trechos que vão para o LLM
FETCH_K = _env("FETCH_K", 30)                # candidatos buscados antes de filtrar
MAX_POR_FONTE = _env("MAX_POR_FONTE", 3)     # diversidade: no máx. N trechos do mesmo doc
# Abaixo do limiar, o trecho é descartado. O valor depende do modelo (cada um
# tem sua "escala" de cosseno): calibre olhando as similaridades em avaliar.py.
LIMIAR_SIMILARIDADE = _env("LIMIAR_SIMILARIDADE", 0.35 if EMBEDDING_PROVIDER == "ollama" else 0.05)


def slug(texto: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", texto.lower()).strip("_")


# O nome da coleção inclui o modelo de embedding: vetores de modelos
# diferentes NÃO são comparáveis (dimensões e espaços diferentes), então
# cada modelo ganha sua própria coleção.
COLLECTION_NAME = _env(
    "COLLECTION_NAME",
    f"financas_mulheres__{slug(EMBEDDING_PROVIDER)}__{slug(EMBEDDING_MODEL)}",
)


def resumo() -> dict:
    """Configuração atual, para registrar nos relatórios (reprodutibilidade)."""
    return {
        "embedding_provider": EMBEDDING_PROVIDER,
        "embedding_model": EMBEDDING_MODEL,
        "llm_model": LLM_MODEL,
        "chunk_size": CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP,
        "top_k": TOP_K,
        "fetch_k": FETCH_K,
        "max_por_fonte": MAX_POR_FONTE,
        "limiar_similaridade": LIMIAR_SIMILARIDADE,
        "collection": COLLECTION_NAME,
    }
