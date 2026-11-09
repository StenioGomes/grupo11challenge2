"""
DEMONSTRAÇÃO: consulta -> recuperação -> resposta fundamentada -> evidências.

    python consultar.py "O que é violência patrimonial?"
    python consultar.py "Mulheres pagam juros maiores?" --k 5
    python consultar.py "Como montar um orçamento?" --sem-llm     # só a recuperação
    python consultar.py "..." --fonte lei_maria_da_penha          # restringe a um documento
    python consultar.py --demo                                     # roda as perguntas de demonstração

Cada consulta é salva em saidas/demonstracoes/consulta_<data>.md (+ .json),
com os trechos recuperados, a resposta e a tabela de fontes citadas.
"""

from __future__ import annotations

import argparse
import sys

from rag import banco_vetorial, config, evidencias
from rag.geracao import Resposta, gerar
from rag.recuperacao import recuperar

PERGUNTAS_DEMO = [
    "O que é violência patrimonial e como ela afeta a autonomia financeira das mulheres?",
    "As mulheres pagam juros mais altos que os homens no crédito? O que os dados mostram?",
    "Quais passos são recomendados para montar um orçamento pessoal ou familiar?",
    "O que caracteriza o superendividamento e quais direitos a lei garante ao consumidor?",
    "Qual o investimento mais usado pelas mulheres investidoras no Brasil?",
    # Pergunta FORA do escopo: o sistema deve admitir que não sabe.
    "Qual é a melhor criptomoeda para comprar este mês?",
]


def consultar(db, pergunta: str, k: int, sem_llm: bool, fonte: str | None, salvar: bool = True) -> Resposta:
    import time
    filtro = {"fonte_id": fonte} if fonte else None
    print("\n" + "=" * 78 + f"\nPERGUNTA: {pergunta}\n" + "=" * 78)
    t0 = time.time()
    print("🔎 Buscando trechos relevantes...", flush=True)
    trechos, candidatos = recuperar(db, pergunta, k=k, filtro=filtro)
    print(f"   {len(trechos)} trechos selecionados de {len(candidatos)} candidatos ({time.time() - t0:.1f}s)")
    evidencias.imprimir_trechos(trechos)
    if sem_llm:
        resposta = Resposta(pergunta=pergunta, texto="(geração desativada com --sem-llm)", trechos=trechos, modelo="(nenhum)")
    else:
        resposta = gerar(pergunta, trechos, ao_vivo=True)
        if not trechos:
            print("\n" + resposta.texto)
    evidencias.imprimir_fontes(resposta)
    if salvar:
        md, _ = evidencias.salvar(resposta, candidatos)
        print(f"Registro salvo em: {md.relative_to(config.RAIZ)}")
    return resposta


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pergunta", nargs="?", help="pergunta em linguagem natural")
    parser.add_argument("--k", type=int, default=config.TOP_K, help="nº de trechos enviados ao LLM")
    parser.add_argument("--sem-llm", action="store_true", help="mostra só a recuperação")
    parser.add_argument("--fonte", help="restringe a busca a um fonte_id do catálogo")
    parser.add_argument("--demo", action="store_true", help="roda as perguntas de demonstração")
    parser.add_argument("--nao-salvar", action="store_true")
    args = parser.parse_args()

    db = banco_vetorial.abrir()
    if banco_vetorial.total(db) == 0:
        print("O banco vetorial está vazio. Rode antes: python baixar_fontes.py && python ingerir.py")
        return 1

    perguntas = PERGUNTAS_DEMO if args.demo else [args.pergunta]
    if not perguntas[0]:
        parser.print_help()
        return 1
    for p in perguntas:
        consultar(db, p, args.k, args.sem_llm, args.fonte, salvar=not args.nao_salvar)
    return 0


if __name__ == "__main__":
    sys.exit(main())
