"""
PIPELINE DE INGESTÃO: data/raw/  ->  chroma_db/

Para cada fonte do catálogo:
  1. carregar   (PDF por página / HTML por seção)
  2. limpar     (hifenização, cabeçalhos repetidos, espaços)
  3. dividir    (chunks de ~1000 caracteres com sobreposição de 150)
  4. embedar    (bge-m3 via Ollama, ou baseline "hash")
  5. armazenar  (ChromaDB com metadados de rastreabilidade)

É IDEMPOTENTE: guarda o SHA-256 do arquivo em cada chunk. Se o arquivo não
mudou, a fonte é pulada; se mudou, os chunks antigos são apagados e a
fonte é reindexada; se saiu do catálogo, seus chunks são removidos.

    python ingerir.py                 # ingestão incremental
    python ingerir.py --reindexar     # apaga a coleção e refaz tudo
    python ingerir.py --apenas bcb_caderno_educacao_financeira

Saídas para inspeção:
  data/processed/<id>.jsonl         cada chunk com texto e metadados
  saidas/relatorio_ingestao.md      estatísticas por fonte (artefato de entrega)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime
from statistics import mean

from rag import banco_vetorial, config
from rag.carregadores import carregar, detectar_formato
from rag.catalogo import carregar_catalogo
from rag.chunking import dividir
from rag.limpeza import limpar_unidades


def sha256_arquivo(caminho) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--reindexar", action="store_true", help="apaga a coleção e indexa tudo de novo")
    parser.add_argument("--apenas", nargs="*", help="ids específicos do catálogo")
    args = parser.parse_args()

    print("Configuração:", json.dumps(config.resumo(), ensure_ascii=False))
    if args.reindexar:
        print("Apagando coleção existente...")
        banco_vetorial.resetar()

    fontes = carregar_catalogo()
    ids_catalogo = {f.id for f in fontes}
    if args.apenas:
        fontes = [f for f in fontes if f.id in set(args.apenas)]

    db = banco_vetorial.abrir()
    config.DIR_PROCESSADOS.mkdir(parents=True, exist_ok=True)

    # Sincronização: remove do banco fontes que saíram do catálogo
    for fonte_id in list(banco_vetorial.contagem_por_fonte(db)):
        if fonte_id not in ids_catalogo:
            print(f"  - removendo '{fonte_id}' (não está mais no catálogo)")
            banco_vetorial.remover_fonte(db, fonte_id)

    estatisticas = []
    inicio_total = time.time()
    for f in fontes:
        linha = {"id": f.id, "titulo": f.titulo, "instituicao": f.instituicao,
                 "formato": detectar_formato(f.caminho_bruto) if f.caminho_bruto.exists() else f.formato,
                 "idioma": f.idioma, "eixo": f.eixo, "foco_mulheres": f.foco_mulheres}
        if not f.caminho_bruto.exists():
            print(f"  ✗ {f.id:45s} arquivo ausente (rode baixar_fontes.py)")
            estatisticas.append({**linha, "status": "ausente"})
            continue

        doc_hash = sha256_arquivo(f.caminho_bruto)
        if banco_vetorial.hash_indexado(db, f.id) == doc_hash:
            print(f"  = {f.id:45s} sem alterações, pulando")
            estatisticas.append({**linha, "status": "inalterado"})
            continue

        t0 = time.time()
        print(f"  … {f.id}: lendo {f.caminho_bruto.name}", flush=True)
        banco_vetorial.remover_fonte(db, f.id)  # remove versão antiga, se houver

        unidades = carregar(f.caminho_bruto)                 # 1. carregar
        chars_brutos = sum(len(u.texto) for u in unidades)
        unidades = limpar_unidades(unidades)                             # 2. limpar
        chars_limpos = sum(len(u.texto) for u in unidades)
        chunks = dividir(f, unidades, doc_hash)                          # 3. dividir

        if not chunks:
            print(f"  ✗ {f.id:45s} nenhum texto extraível (PDF escaneado? precisa de OCR)")
            estatisticas.append({**linha, "status": "sem texto"})
            continue

        print(f"\r      {len(unidades)} unidades -> {len(chunks)} chunks; gerando embeddings...", flush=True)
        banco_vetorial.adicionar(db, chunks, progresso=True)             # 4+5. embedar e armazenar

        with open(config.DIR_PROCESSADOS / f"{f.id}.jsonl", "w", encoding="utf-8") as saida:
            for c in chunks:
                saida.write(json.dumps({"id": c.id, "texto": c.texto, **c.metadados}, ensure_ascii=False) + "\n")

        tamanhos = [c.metadados["n_caracteres"] for c in chunks]
        reg = {
            **linha,
            "status": "indexado",
            "unidades": len(unidades),
            "chars_brutos": chars_brutos,
            "chars_limpos": chars_limpos,
            "chunks": len(chunks),
            "chunk_medio": round(mean(tamanhos)),
            "segundos": round(time.time() - t0, 1),
        }
        estatisticas.append(reg)
        print(f"  ✓ {f.id:45s} {reg['unidades']:4d} unid. -> {reg['chunks']:4d} chunks "
              f"(média {reg['chunk_medio']} car.)  {reg['segundos']}s")

    contagem = banco_vetorial.contagem_por_fonte(db)
    total = sum(contagem.values())
    print(f"\nBanco: {total} chunks de {len(contagem)} fontes  ({time.time() - inicio_total:.0f}s)"
          f"  | métrica do índice: {banco_vetorial.metrica(db)}")
    escrever_relatorio(estatisticas, contagem)
    if len(contagem) < 20:
        print("⚠️  Menos de 20 fontes indexadas: requisito mínimo não atingido.")
    return 0


def escrever_relatorio(estatisticas: list[dict], contagem) -> None:
    config.DIR_SAIDAS.mkdir(parents=True, exist_ok=True)
    total = sum(contagem.values())
    linhas = [
        "# Relatório de ingestão",
        "",
        f"Gerado em {datetime.now():%d/%m/%Y %H:%M} por `ingerir.py`.",
        "",
        "Configuração: " + ", ".join(f"`{k}={v}`" for k, v in config.resumo().items()),
        "",
        f"**Total no banco vetorial: {total} chunks de {len(contagem)} documentos-fonte.**",
        "",
        "| # | Fonte (id) | Formato | Idioma | Foco mulheres | Unid. | Chunks no banco | Chunk médio (car.) | Status desta execução |",
        "|---:|---|:---:|:---:|:---:|---:|---:|---:|---|",
    ]
    for i, e in enumerate(estatisticas, start=1):
        linhas.append(
            f"| {i} | `{e['id']}` | {e['formato']} | {e['idioma']} | {'✔' if e['foco_mulheres'] else ''} | "
            f"{e.get('unidades', '')} | {contagem.get(e['id'], 0)} | {e.get('chunk_medio', '')} | {e['status']} |"
        )
    linhas += [
        "",
        "Legenda: *Unid.* = páginas (PDF) ou seções (HTML) com texto após a limpeza. "
        "*inalterado* = arquivo com o mesmo SHA-256 da última ingestão (não foi reprocessado).",
    ]
    caminho = config.DIR_SAIDAS / "relatorio_ingestao.md"
    caminho.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"Relatório: {caminho.relative_to(config.RAIZ)}")


if __name__ == "__main__":
    sys.exit(main())
