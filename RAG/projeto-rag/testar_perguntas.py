"""Roda as perguntas de teste pelo RAG e salva as respostas.

Uso:
    python3 testar_perguntas.py            # todas as perguntas
    python3 testar_perguntas.py 1 5 12     # só as perguntas com esses ids

Saídas (na pasta avaliacao/):
    resultados.json  -> dados completos (resposta, fontes, distâncias, tempo)
    resultados.md    -> relatório legível
"""
import json
import sys
import time
from datetime import datetime
from pathlib import Path

from config import MODELO_LLM, LIMIAR_DISTANCIA, TOP_K
from rag import perguntar, recuperar, RECUSA

PASTA = Path(__file__).parent / "avaliacao"

perguntas = [
    {"id": 1, "texto": "Qual é a diferença conceitual entre endividamento ativo e endividamento passivo?"},
    {"id": 2, "texto": "Qual é o impacto estimado na redução de custos quando o indivíduo passa a anotar seus gastos mensais?"},
    {"id": 3, "texto": "Quanto da renda mensal a Comissão de Valores Mobiliários (CVM) recomenda destinar a reservas de emergência ou projetos futuros?"},
    {"id": 4, "texto": "Quais são os 4 pilares da educação financeira?"},
    {"id": 5, "texto": "O que é a Estratégia Nacional de Educação Financeira (ENEF) e por que ela foi instituída pelo governo brasileiro?"},
    {"id": 6, "texto": "De que forma o orçamento pessoal ou familiar atua no planejamento financeiro?"},
    {"id": 7, "texto": "Quais são as etapas práticas recomendadas para calcular o patrimônio líquido, estruturar um fluxo de caixa equilibrado e formar uma reserva de emergência familiar?"},
    {"id": 8, "texto": "De que maneira a contabilidade mental e a facilidade de acesso ao crédito influenciam o comportamento de consumo e a propensão ao endividamento de trabalhadores?"},
    {"id": 9, "texto": "Como o monitoramento sistemático do fluxo de caixa e a categorização de receitas e despesas contribuem para a disciplina financeira e a realização de metas de longo prazo?"},
    {"id": 10, "texto": "De que forma a educação financeira nas escolas pode capacitar jovens a distinguir desejos de necessidades, evitar armadilhas de consumo e planejar seus sonhos prioritários?"},
    {"id": 11, "texto": "Como a sociologia econômica desconstruiu o orçamento doméstico como mero modelo estatístico para revelar o impacto dos arranjos sociais, culturais e de gênero no dia a dia das famílias?"},
    {"id": 12, "texto": "Em que medida estudantes universitários sem formação técnica em gestão ou contabilidade aplicam métodos informais de registro e controle para gerenciar suas receitas e despesas?"},
    {"id": 13, "texto": "De que maneira instrumentos contábeis práticos — como o acompanhamento do fluxo de caixa diário, a planilha de orçamento e a matriz de organização de dívidas — ajudam a identificar e conter os \"pequenos gastos\" cotidianos?"},
    {"id": 14, "texto": "Como o planejamento e o uso da tecnologia podem ajudar as famílias a organizarem o orçamento doméstico?"},
    {"id": 15, "texto": "Qual é o impacto de manter um orçamento familiar sobre o endividamento e a capacidade de poupar?"},
    {"id": 16, "texto": "O que é o custo de oportunidade e como ele se aplica a uma escolha financeira que envolva tempo e dinheiro?"},
    {"id": 17, "texto": "Quais são as quatro dimensões nas quais a cidadania financeira se divide?"},
    {"id": 18, "texto": "O que define o estado de bem-estar financeiro de acordo com a adaptação da G20 Policy Note on Financial Well-Being?"},
    {"id": 19, "texto": "Quais são as três possíveis situações que um orçamento pode apresentar em sua gestão?"},
    {"id": 20, "texto": "Quais são as três características fundamentais que devem ser conhecidas ao analisar um investimento?"},
    {"id": 21, "texto": "O que significa a liquidez em um investimento e como ela geralmente é expresso nos fundos de aplicação sem resgate imediato?"},
    {"id": 22, "texto": "Qual é a principal diferença conceitual e de tributação entre os planos de previdência complementar aberta conhecidos como PGBL e VGBL?"},
    {"id": 23, "texto": "O que representam a franquia e o prêmio em um contrato de seguro?"},
    {"id": 24, "texto": "O que são e quais são os riscos associados aos ativos virtuais (criptomoedas) em relação à sua emissão e garantia?"},
    {"id": 25, "texto": "O que preconizam os chamados \"5 Rs\" na relação de consumo consciente?"},
    {"id": 26, "texto": "Quais são os principais hábitos que prejudicam e estragam as cédulas de dinheiro, gerando custos para a sociedade?"},
    {"id": 27, "texto": "O que caracteriza os investimentos de renda fixa e de renda variável, respectivamente?"},
    {"id": 28, "texto": "O que estabelece o Regime Geral da Previdência Social (RGPS) gerido pelo INSS em termos de abrangência de trabalhadores?"},
    {"id": 29, "texto": "Qual é a diferença conceitual entre \"Sonho\" e \"Projeto\"?"},
    {"id": 30, "texto": "Quais são os três componentes fundamentais a serem analisados antes de realizar qualquer investimento?"},
    {"id": 31, "texto": "O que é o Custo Efetivo Total (CET) nas operações de crédito e por que ele deve ser comparado?"},
    {"id": 32, "texto": "O que é orçamento?"},
    {"id": 33, "texto": "Como elaborar um orçamento?"},
    {"id": 34, "texto": "O que eu preciso saber antes de investir?"},
    {"id": 35, "texto": "Por que a educação financeira é importante?"},
    {"id": 36, "texto": "Quais são os passos fundamentais para alcançar a estabilidade e o bem-estar financeiro?"},
    {"id": 37, "texto": "O que é o orçamento pessoal ou familiar e qual o primeiro passo para elaborá-lo?"},
    {"id": 38, "texto": "Quais as diferenças entre receitas e despesas em fixas, variáveis e eventuais?"},
    {"id": 39, "texto": "Qual é a porcentagem mensal recomendada para poupar e o que significa a regra do \"pague-se primeiro\"?"},
    {"id": 40, "texto": "Qual é a função da reserva de emergência e como o valor sugerido varia conforme a estabilidade da renda?"},
    {"id": 41, "texto": "Quais são os passos recomendados para quem está com o orçamento no vermelho (resultado negativo) e precisa quitar dívidas?"},
    {"id": 42, "texto": "O que é a \"Pink Tax\" (taxa rosa)?"},
    {"id": 43, "texto": "Quais são os principais fatores que levam o mercado a praticar preços mais altos para o público feminino?"},
    {"id": 44, "texto": "Como escapar da Pink Tax?"},
    {"id": 45, "texto": "Quais são os 4 pilares da educação financeira?"},
    {"id": 46, "texto": "O que é a Estratégia Nacional de Educação Financeira (ENEF) e por que ela foi instituída pelo governo brasileiro?"},
    {"id": 47, "texto": "De que forma o orçamento pessoal ou familiar atua no planejamento financeiro?"},
    {"id": 48, "texto": "Quais são as etapas práticas recomendadas para calcular o patrimônio líquido, estruturar um fluxo de caixa equilibrado e formar uma reserva de emergência familiar?"},
    {"id": 49, "texto": "De que maneira a contabilidade mental e a facilidade de acesso ao crédito influenciam o comportamento de consumo e a propensão ao endividamento de trabalhadores?"},
    {"id": 50, "texto": "Como o monitoramento sistemático do fluxo de caixa e a categorização de receitas e despesas contribuem para a disciplina financeira e a realização de metas de longo prazo?"},
]


def main():
    ids = {int(a) for a in sys.argv[1:]}
    selecionadas = [p for p in perguntas if not ids or p["id"] in ids]

    resultados = []
    inicio_total = time.time()
    for p in selecionadas:
        print(f"[{p['id']}/{len(perguntas)}] {p['texto']}")
        inicio = time.time()
        resposta, usados = perguntar(p["texto"])
        tempo = time.time() - inicio
        # top-k completo (inclusive trechos descartados pelo limiar)
        recuperados = recuperar(p["texto"])
        resultados.append({
            "id": p["id"],
            "pergunta": p["texto"],
            "resposta": resposta,
            "recusou": resposta == RECUSA,
            "fontes": sorted({t["fonte"] for t in usados}),
            "melhor_distancia": round(recuperados[0]["distancia"], 3) if recuperados else None,
            "recuperados": [
                {"fonte": t["fonte"], "distancia": round(t["distancia"], 3), "texto": t["texto"]}
                for t in recuperados
            ],
            "tempo_s": round(tempo, 1),
        })
        status = "RECUSOU" if resposta == RECUSA else "ok"
        print(f"    -> {status} ({tempo:.1f}s, dist={resultados[-1]['melhor_distancia']})")

    recusas = sum(r["recusou"] for r in resultados)
    resumo = {
        "data": datetime.now().isoformat(timespec="seconds"),
        "modelo": MODELO_LLM,
        "top_k": TOP_K,
        "limiar_distancia": LIMIAR_DISTANCIA,
        "total": len(resultados),
        "respondidas": len(resultados) - recusas,
        "recusadas": recusas,
        "tempo_total_s": round(time.time() - inicio_total, 1),
    }

    PASTA.mkdir(exist_ok=True)
    (PASTA / "resultados.json").write_text(
        json.dumps({"resumo": resumo, "resultados": resultados}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    md = [
        "# Resultados do teste do RAG",
        "",
        f"- Data: {resumo['data']}",
        f"- Modelo: `{resumo['modelo']}` | top_k={TOP_K} | limiar={LIMIAR_DISTANCIA}",
        f"- Respondidas: **{resumo['respondidas']}/{resumo['total']}** "
        f"| Recusadas: **{recusas}** | Tempo total: {resumo['tempo_total_s']}s",
        "",
    ]
    for r in resultados:
        md += [
            f"## {r['id']}. {r['pergunta']}",
            "",
            r["resposta"],
            "",
            f"*Fontes:* {', '.join(r['fontes']) or '—'} "
            f"| *melhor distância:* {r['melhor_distancia']} | *tempo:* {r['tempo_s']}s",
            "",
        ]
    (PASTA / "resultados.md").write_text("\n".join(md), encoding="utf-8")

    print(f"\nRespondidas {resumo['respondidas']}/{resumo['total']}, recusadas {recusas}. "
          f"Resultados em {PASTA}/resultados.md e .json")


if __name__ == "__main__":
    main()
