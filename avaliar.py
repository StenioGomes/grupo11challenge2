"""
AVALIAÇÃO DA RECUPERAÇÃO (o foco desta etapa do projeto).

Roda só a parte de recuperação (sem LLM) para cada pergunta de
avaliacao/perguntas.yaml e compara as fontes recuperadas com o gabarito.

Métricas (calculadas por FONTE, porque o que importa para a
rastreabilidade é trazer o documento certo):

  Hit@k     a pergunta teve pelo menos 1 fonte relevante entre os k trechos?
  MRR       média de 1/posição do 1º trecho relevante (1.0 = sempre em 1º lugar)
  Precisão  fração dos k trechos que vêm de fontes relevantes
  Recall    fração das fontes relevantes que apareceram nos k trechos

    python avaliar.py
    python avaliar.py --k 3
    EMBEDDING_PROVIDER=hash python avaliar.py   # compara com o baseline lexical
    (para o baseline, rode antes: EMBEDDING_PROVIDER=hash python ingerir.py)

Resultado salvo em saidas/avaliacao_recuperacao_<modelo>.md
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from statistics import mean

import yaml

from rag import banco_vetorial, config
from rag.recuperacao import recuperar


def avaliar_pergunta(db, pergunta: str, relevantes: set[str], k: int) -> dict:
    trechos, _ = recuperar(db, pergunta, k=k)
    fontes = [t.fonte_id for t in trechos]
    pos_primeiro = next((i for i, f in enumerate(fontes, start=1) if f in relevantes), None)
    return {
        "pergunta": pergunta,
        "recuperadas": fontes,
        "hit": 1.0 if pos_primeiro else 0.0,
        "rr": 1.0 / pos_primeiro if pos_primeiro else 0.0,
        "precisao": (sum(f in relevantes for f in fontes) / len(fontes)) if fontes else 0.0,
        "recall": len(relevantes & set(fontes)) / len(relevantes),
        "sim_top1": trechos[0].similaridade if trechos else 0.0,
        "pos": pos_primeiro,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--k", type=int, default=config.TOP_K)
    parser.add_argument("--arquivo", default=str(config.RAIZ / "avaliacao" / "perguntas.yaml"))
    args = parser.parse_args()

    db = banco_vetorial.abrir()
    if banco_vetorial.total(db) == 0:
        print("Banco vazio para esta configuração. Rode ingerir.py com o mesmo EMBEDDING_PROVIDER/MODEL.")
        return 1
    indexadas = set(banco_vetorial.contagem_por_fonte(db))

    casos = yaml.safe_load(open(args.arquivo, encoding="utf-8"))["perguntas"]
    resultados = []
    for caso in casos:
        relevantes = set(caso["relevantes"]) & indexadas
        if not relevantes:
            print(f"  (pulando: nenhuma fonte relevante indexada) {caso['pergunta']}")
            continue
        r = avaliar_pergunta(db, caso["pergunta"], relevantes, args.k)
        resultados.append(r)
        marca = "✓" if r["hit"] else "✗"
        print(f"  {marca} pos={str(r['pos'] or '-'):>2}  P={r['precisao']:.2f}  R={r['recall']:.2f}  "
              f"sim1={r['sim_top1']:.3f}  {r['pergunta'][:70]}")

    if not resultados:
        return 1
    agregado = {
        f"Hit@{args.k}": mean(r["hit"] for r in resultados),
        "MRR": mean(r["rr"] for r in resultados),
        f"Precisão@{args.k}": mean(r["precisao"] for r in resultados),
        f"Recall de fontes@{args.k}": mean(r["recall"] for r in resultados),
    }
    print("\nMÉDIAS:", "  ".join(f"{k}={v:.3f}" for k, v in agregado.items()))

    linhas = [
        "# Avaliação da recuperação",
        "",
        f"Gerado em {datetime.now():%d/%m/%Y %H:%M}. Perguntas avaliadas: {len(resultados)}.",
        "",
        "Configuração: " + ", ".join(f"`{k}={v}`" for k, v in config.resumo().items()),
        "",
        "| Métrica | Valor |",
        "|---|---:|",
        *[f"| {k} | {v:.3f} |" for k, v in agregado.items()],
        "",
        "| Pergunta | 1º relevante na posição | Precisão | Recall | Sim. top-1 | Fontes recuperadas |",
        "|---|:---:|---:|---:|---:|---|",
    ]
    for r in resultados:
        linhas.append(
            f"| {r['pergunta']} | {r['pos'] or '—'} | {r['precisao']:.2f} | {r['recall']:.2f} | "
            f"{r['sim_top1']:.3f} | {', '.join(r['recuperadas'])} |"
        )
    config.DIR_SAIDAS.mkdir(parents=True, exist_ok=True)
    nome = f"avaliacao_recuperacao_{config.slug(config.EMBEDDING_PROVIDER)}_{config.slug(config.EMBEDDING_MODEL)}.md"
    (config.DIR_SAIDAS / nome).write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"Relatório: saidas/{nome}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
