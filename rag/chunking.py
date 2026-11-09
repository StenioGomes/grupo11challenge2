"""
ETAPA 3 DA INGESTÃO: chunking (divisão em trechos).

Por que dividir? Porque o embedding de um documento inteiro "dilui" o
significado: um PDF de 70 páginas vira um vetor genérico que não é muito
parecido com nenhuma pergunta específica. Trechos de ~1 parágrafo geram
vetores focados, e o LLM recebe só o que interessa.

Estratégia adotada (detalhada em docs/estrategia_chunking.md):

1. Divisão RECURSIVA por separadores naturais, do maior para o menor:
   parágrafo -> linha -> frase -> ponto-e-vírgula -> vírgula -> palavra.
   O splitter só desce de nível quando o pedaço ainda é grande demais,
   então ele tenta cortar sempre na fronteira mais "semântica" possível.
2. Tamanho alvo de 1000 caracteres (~200-250 tokens em português) com
   150 de sobreposição, para que uma ideia cortada no fim de um chunk
   apareça também no início do próximo.
3. Chunking DENTRO de cada página/seção: assim cada chunk tem um único
   localizador (p. 12 ou "Art. 7º") e a citação fica exata.
4. Cabeçalho contextual: cada chunk começa com "[Título – Instituição]".
   Isso entra no embedding e ajuda trechos genéricos ("conforme a tabela
   abaixo...") a serem associados ao assunto do documento.
5. Filtros: descarta chunks muito curtos e duplicados exatos.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

from langchain_text_splitters import RecursiveCharacterTextSplitter

from . import config
from .carregadores import Unidade
from .catalogo import Fonte

SEPARADORES_PT = ["\n\n", "\n", ". ", "? ", "! ", "; ", ": ", ", ", " ", ""]


@dataclass
class Chunk:
    id: str
    texto: str                      # o que é embedado e mostrado ao LLM
    metadados: dict = field(default_factory=dict)


def criar_splitter(tamanho: int = config.CHUNK_SIZE, sobreposicao: int = config.CHUNK_OVERLAP):
    return RecursiveCharacterTextSplitter(
        chunk_size=tamanho,
        chunk_overlap=sobreposicao,
        separators=SEPARADORES_PT,
        keep_separator="end",   # mantém o ponto final no fim do chunk (frases inteiras)
        length_function=len,
        strip_whitespace=True,
    )


def cabecalho(fonte: Fonte, unidade: Unidade) -> str:
    local = f"p. {unidade.pagina}" if unidade.pagina else (unidade.secao or "")
    partes = [fonte.titulo, fonte.instituicao, str(fonte.ano)]
    texto = " – ".join(partes)
    return f"[{texto}{' | ' + local if local else ''}]"


def gerar_id(fonte_id: str, doc_hash: str, indice: int, texto: str) -> str:
    """
    ID determinístico: o mesmo documento, com o mesmo conteúdo, sempre gera
    os mesmos IDs. Isso torna a ingestão idempotente (rodar 2x não duplica).
    """
    base = f"{fonte_id}|{doc_hash}|{indice}|{texto}".encode("utf-8")
    return hashlib.sha256(base).hexdigest()[:32]


def dividir(fonte: Fonte, unidades: list[Unidade], doc_hash: str) -> list[Chunk]:
    splitter = criar_splitter()
    chunks: list[Chunk] = []
    vistos: set[str] = set()
    indice = 0

    for unidade in unidades:
        for pedaco in splitter.split_text(unidade.texto):
            pedaco = pedaco.strip()
            if len(pedaco) < config.CHUNK_MINIMO:
                continue
            impressao = hashlib.md5(pedaco.lower().encode()).hexdigest()
            if impressao in vistos:          # duplicata exata dentro do documento
                continue
            vistos.add(impressao)

            texto = f"{cabecalho(fonte, unidade)}\n{pedaco}"
            meta = fonte.metadados()
            meta.update(
                {
                    "doc_hash": doc_hash,
                    "chunk_indice": indice,
                    "pagina": unidade.pagina if unidade.pagina is not None else -1,
                    "secao": unidade.secao or "",
                    "n_caracteres": len(pedaco),
                }
            )
            chunks.append(Chunk(id=gerar_id(fonte.id, doc_hash, indice, pedaco), texto=texto, metadados=meta))
            indice += 1
    return chunks
