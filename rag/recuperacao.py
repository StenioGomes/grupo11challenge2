"""
CONSULTA – PASSO 1: recuperação (retrieval).

Fluxo:
  pergunta --embed_query--> vetor q
  Chroma devolve os FETCH_K chunks mais próximos de q (com a distância)
  -> converte distância de cosseno em similaridade (1 - d)
  -> descarta o que está abaixo do LIMIAR (trecho "pouco relacionado")
  -> limita a MAX_POR_FONTE trechos por documento (diversidade de fontes)
  -> fica com os TOP_K melhores

Robustez: a similaridade é calculada AQUI, pelo cosseno entre o vetor da
pergunta e o vetor de cada chunk, em vez de ser deduzida da "distância"
que o banco devolve. Assim o resultado não depende da métrica com que a
coleção foi criada (algumas versões do Chroma ignoram a opção de cosseno
e usam L2, o que tornaria a conversão 1 - distância incorreta).

Por que buscar mais (FETCH_K) e depois filtrar? Porque documentos longos
tendem a dominar o topo com vários chunks quase iguais. Buscar uma lista
maior e aplicar o limite por fonte dá ao LLM visões de instituições
diferentes, e isso melhora a fundamentação e a rastreabilidade.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict

from langchain_chroma import Chroma

from . import config
from .embeddings import cosseno


@dataclass
class Trecho:
    rank: int
    chunk_id: str
    fonte_id: str
    titulo: str
    instituicao: str
    ano: int
    url: str
    pagina: int | None
    secao: str
    similaridade: float
    texto: str

    @property
    def localizador(self) -> str:
        if self.pagina:
            return f"p. {self.pagina}"
        return self.secao or "documento"

    def referencia(self) -> str:
        return f"{self.titulo} – {self.instituicao} ({self.ano}), {self.localizador}"

    def to_dict(self) -> dict:
        d = asdict(self)
        d["localizador"] = self.localizador
        return d


def recuperar(
    db: Chroma,
    pergunta: str,
    k: int = config.TOP_K,
    fetch_k: int = config.FETCH_K,
    limiar: float = config.LIMIAR_SIMILARIDADE,
    max_por_fonte: int = config.MAX_POR_FONTE,
    filtro: dict | None = None,
) -> tuple[list[Trecho], list[Trecho]]:
    """
    Retorna (selecionados, candidatos).
    `candidatos` = lista completa antes dos filtros, útil para depurar
    e para mostrar na demonstração por que um trecho ficou de fora.
    """
    vetor_q = db.embeddings.embed_query(pergunta)
    n = min(fetch_k, db._collection.count())
    if n == 0:
        return [], []
    res = db._collection.query(
        query_embeddings=[vetor_q],
        n_results=n,
        where=filtro,
        include=["documents", "metadatas", "embeddings"],
    )

    candidatos: list[Trecho] = []
    for chunk_id, texto, m, vetor in zip(res["ids"][0], res["documents"][0], res["metadatas"][0], res["embeddings"][0]):
        candidatos.append(
            Trecho(
                rank=0,
                chunk_id=chunk_id,
                fonte_id=m.get("fonte_id", "?"),
                titulo=m.get("titulo", "?"),
                instituicao=m.get("instituicao", "?"),
                ano=int(m.get("ano", 0)),
                url=m.get("url", ""),
                pagina=m.get("pagina") if m.get("pagina", -1) > 0 else None,
                secao=m.get("secao", ""),
                similaridade=round(cosseno(vetor_q, [float(x) for x in vetor]), 4),
                texto=texto,
            )
        )
    candidatos.sort(key=lambda t: t.similaridade, reverse=True)
    for i, t in enumerate(candidatos, start=1):
        t.rank = i

    selecionados: list[Trecho] = []
    por_fonte: dict[str, int] = {}
    for t in candidatos:
        if t.similaridade < limiar:
            continue
        if por_fonte.get(t.fonte_id, 0) >= max_por_fonte:
            continue
        por_fonte[t.fonte_id] = por_fonte.get(t.fonte_id, 0) + 1
        selecionados.append(t)
        if len(selecionados) >= k:
            break
    return selecionados, candidatos
