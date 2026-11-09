"""
ETAPA 5 DA INGESTÃO: armazenamento no banco vetorial (ChromaDB).

O banco vetorial guarda, para cada chunk: o ID, o vetor (embedding), o
texto e os metadados. Na consulta, ele encontra os vetores mais próximos
do vetor da pergunta usando um índice HNSW (busca aproximada de vizinhos,
muito mais rápida que comparar com todos os vetores).

Decisões:
- Persistente em disco (chroma_db/): indexa uma vez, consulta várias.
- Métrica de COSSENO pedida na criação (o padrão do Chroma é L2). Como
  algumas versões ignoram essa opção, a recuperação NÃO depende dela: o
  banco só encontra os candidatos e a similaridade de cosseno é calculada
  em recuperacao.py a partir dos vetores. Para vetores normalizados (caso
  do bge-m3 via Ollama e do baseline hash), a ordem dos vizinhos é a mesma
  em L2 e em cosseno, então a busca continua correta.
- Metadados ricos em cada chunk (fonte_id, título, instituição, URL,
  página/seção, hash do documento): é o que permite filtrar por fonte,
  atualizar documentos alterados e CITAR a origem de cada trecho.
"""

from __future__ import annotations

from collections import Counter

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from . import config
from .chunking import Chunk
from .embeddings import criar_embeddings


def abrir(embeddings: Embeddings | None = None, nome: str = config.COLLECTION_NAME) -> Chroma:
    config.DIR_CHROMA.mkdir(parents=True, exist_ok=True)
    return Chroma(
        collection_name=nome,
        embedding_function=embeddings or criar_embeddings(),
        persist_directory=str(config.DIR_CHROMA),
        collection_metadata={"hnsw:space": "cosine"},
    )


def hash_indexado(db: Chroma, fonte_id: str) -> str | None:
    """Hash do arquivo que gerou os chunks atuais desta fonte (None se não indexada)."""
    res = db.get(where={"fonte_id": fonte_id}, limit=1, include=["metadatas"])
    if res["metadatas"]:
        return res["metadatas"][0].get("doc_hash")
    return None


def remover_fonte(db: Chroma, fonte_id: str) -> None:
    db.delete(where={"fonte_id": fonte_id})


def adicionar(db: Chroma, chunks: list[Chunk], lote: int = 32, progresso: bool = False) -> None:
    """Gera embeddings e grava em lotes (evita estourar memória/timeout do Ollama)."""
    import time
    inicio = time.time()
    for i in range(0, len(chunks), lote):
        parte = chunks[i : i + lote]
        db.add_documents(
            documents=[Document(page_content=c.texto, metadata=c.metadados) for c in parte],
            ids=[c.id for c in parte],
        )
        if progresso:
            feitos = min(i + lote, len(chunks))
            decorrido = time.time() - inicio
            restante = decorrido / feitos * (len(chunks) - feitos)
            print(f"\r      embeddings {feitos:5d}/{len(chunks)}  "
                  f"({decorrido:5.1f}s, faltam ~{restante:4.0f}s)", end="", flush=True)
    if progresso:
        print("\r" + " " * 60 + "\r", end="", flush=True)


def contagem_por_fonte(db: Chroma) -> Counter:
    res = db.get(include=["metadatas"])
    return Counter(m.get("fonte_id", "?") for m in res["metadatas"])


def metrica(db: Chroma) -> str:
    """Métrica com que a coleção foi realmente criada (cosine, l2 ou ip)."""
    try:
        cfg = db._collection.configuration or {}
        hnsw = cfg.get("hnsw") or {}
        if hnsw.get("space"):
            return str(hnsw["space"])
    except Exception:
        pass
    return str((db._collection.metadata or {}).get("hnsw:space", "l2 (padrão)"))


def total(db: Chroma) -> int:
    return db._collection.count()


def resetar(nome: str = config.COLLECTION_NAME) -> None:
    """Apaga a coleção inteira (usado por `ingerir.py --reindexar`)."""
    db = abrir(nome=nome)
    db.delete_collection()
