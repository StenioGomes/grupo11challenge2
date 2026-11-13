# Comparação: respostas do RAG × resposta esperada

- Modelo: `llama3.2` | top_k=4 | limiar=0.5 | 50 perguntas (`testar_perguntas.py`)
- **Gabarito:** o PDF de perguntas não traz respostas. A resposta esperada de cada pergunta foi tirada do trecho do documento-fonte que a responde (indicado na coluna "Fonte").
- Respostas completas do RAG: [resultados.md](resultados.md)

## Resumo

| Resultado | Qtde | % | Perguntas |
|---|---|---|---|
| ✅ Correta | 18 | 36% | 1, 4, 6, 16, 17, 19, 20, 21, 23, 24, 25, 29, 30, 31, 32, 42, 45, 47 |
| 🟡 Parcial (incompleta, genérica ou misturando fontes) | 16 | 32% | 5, 8, 9, 15, 28, 33, 34, 35, 36, 37, 41, 43, 44, 46, 49, 50 |
| ❌ Incorreta | 2 | 4% | 27, 40 |
| ⛔ Recusou, mas a resposta está nos documentos | 9 | 18% | 2, 3, 7, 18, 22, 26, 38, 39, 48 |
| 📄 Documento-fonte não está indexado | 5 | 10% | 10, 13 e 14 (inventou resposta); 11 e 12 (recusou, correto) |

Na prática: **18 de 50 corretas, 34 de 50 com pelo menos parte certa** e **3 alucinações** (10, 13, 14), todas em perguntas cujo documento não está em `docs/`.

## Pergunta a pergunta

Fontes: **Caderno** = caderno_cidadania_financeira.pdf · **UNITINS** = A EDUCAÇÃO FINANCEIRA PARA A GESTÃO DO ORÇAMENTO… · **Ferreira** = afcsanto…formatados.pdf · **Susesp** = Orçamento (Susesp).pdf · **Pink** = O preço invisível de ser mulher.pdf

| # | Resposta esperada (resumo) | Fonte | O que o RAG respondeu | Resultado |
|---|---|---|---|---|
| 1 | Passivo: dívidas por fatos alheios à vontade (doença, desemprego…); ativo: dívidas por escolhas equivocadas (Tolotti) | UNITINS | Igual ao esperado | ✅ |
| 2 | Quem anota os gastos costuma reduzi-los em **cerca de 12%** (Macedo Jr.) | UNITINS | Recusou | ⛔ |
| 3 | **Ao menos 20%** da renda (CVM, 2019) | UNITINS | Recusou | ⛔ |
| 4 | Controle seu orçamento; conheça suas dívidas; realize seus sonhos; aprenda a investir | Ferreira | Igual ao esperado | ✅ |
| 5 | Mobilização multissetorial criada pelo Decreto 7.397/2010, política de Estado permanente, para melhorar o acesso à educação financeira | Ferreira | Decreto e objetivo certos; "política de Estado permanente" saiu truncado ("política de financeiro") | 🟡 |
| 6 | Orçamento discrimina receitas e despesas previstas, permite simular e acompanhar as contas | FINANÇAS PESSOAIS / UNITINS | Correto (citando a cartilha da Caixa) | ✅ |
| 7 | Passo 1: balanço (ativos − passivos = patrimônio líquido); Passo 2: registrar receitas e despesas por um mês; depois formar a reserva | GUIA | Recusou | ⛔ |
| 8 | Achados do estudo com colaboradores da instituição de ensino | CONTABILIDADE MENTAL | Resposta genérica sobre consumo e crédito, sem os resultados do estudo | 🟡 |
| 9 | Fluxo de caixa em dia permite avaliar custos, reposicionar objetivos e consumo, com disciplina | FLUXODECAIXA | Genérica, mas coerente com o artigo | 🟡 |
| 10 | — | Educação financeira nas Escolas (não indexado) | Inventou resposta atribuída ao UNITINS | 📄 alucinou |
| 11 | — | De dispositivo de prescrição… (não indexado) | Recusou | 📄 correto |
| 12 | — | Estudo UNIPAM (não indexado) | Recusou | 📄 correto |
| 13 | — | Ferramentas contábeis práticas (não indexado) | Inventou explicação dos 3 instrumentos | 📄 alucinou |
| 14 | — | Estudo UESPI Picos (não indexado) | Disse que não havia informação e depois inferiu | 📄 alucinou |
| 15 | — | Planejamento financeiro no orçamento familiar (não indexado) | Respondeu com trechos do UNITINS/GUIA, coerentes | 🟡 |
| 16 | Preço (financeiro ou não) de uma escolha, a oportunidade perdida; exemplo de tempo e dinheiro | Caderno | Correto, com exemplo | ✅ |
| 17 | Educação financeira; inclusão financeira; proteção ao consumidor; participação cidadã | Caderno | Igual ao esperado | ✅ |
| 18 | Estado em que a pessoa paga as contas, tem reserva para imprevistos, guarda para projetos e se sente satisfeita e segura | Caderno | Recusou (a busca trouxe a bibliografia) | ⛔ |
| 19 | Deficitário, neutro/equilibrado, superavitário | Caderno | Igual ao esperado | ✅ |
| 20 | Liquidez, risco (segurança), rentabilidade | Caderno | Igual ao esperado | ✅ |
| 21 | Conversão em dinheiro a valor justo; expressa por "D + número" (D+1, D+5) | Caderno | Correto | ✅ |
| 22 | VGBL é tecnicamente um seguro; a principal diferença é a forma de cobrança dos impostos | Caderno | Recusou | ⛔ |
| 23 | Franquia: parte do prejuízo paga pelo segurado no sinistro; prêmio: valor pago à seguradora | Caderno | Correto | ✅ |
| 24 | Não são emitidos nem garantidos pelo BC; não são moeda; volatilidade e risco de perda | Caderno | Correto (frase final contraditória) | ✅ |
| 25 | Repensar, reduzir, reutilizar, reciclar, recusar | Caderno | Igual ao esperado | ✅ |
| 26 | Grampear, amassar, rabiscar, retirar o fio de segurança, remendar com fita, sujar, rasgar | Caderno | Recusou | ⛔ |
| 27 | Renda fixa: remuneração definida na aplicação, menor risco; variável: não dimensionável, maior risco (ex.: ações) | Caderno | Confundiu com receitas fixas/variáveis (salário, aluguel) | ❌ |
| 28 | Trabalhadores CLT da iniciativa privada **e também domésticos e autônomos** | Caderno | Só citou CLT | 🟡 |
| 29 | Sonho: desejo, aspiração; projeto: o sonho "no papel" com o caminho para alcançá-lo | Caderno | Igual ao esperado | ✅ |
| 30 | Liquidez, risco, rentabilidade | Caderno | Igual ao esperado | ✅ |
| 31 | Custo total do empréstimo (juros, tarifas, impostos, encargos); permite comparar instituições | Caderno | Correto | ✅ |
| 32 | Ferramenta de planejamento financeiro que contribui para realizar sonhos e projetos | Caderno | Definição correta, mas do UNITINS/Caixa | ✅ |
| 33 | 4 etapas: planejamento, registro, agrupamento, avaliação | Caderno | Misturou os passos do Susesp e inventou "prazo de 5, 10, 30 anos" | 🟡 |
| 34 | Conhecer seu perfil de investidor, os objetivos do investimento, e equilibrar liquidez, risco e rentabilidade | Caderno | Só o perfil; o resto é uma lista confusa | 🟡 |
| 35 | Promove comportamentos de cidadania e bem-estar financeiro; instrumento de desenvolvimento econômico | Caderno | Definição de educação financeira (OCDE) em vez do porquê | 🟡 |
| 36 | Pagar contas, ter reserva, guardar para projetos (definição de bem-estar) | Caderno | Lista genérica de boas práticas | 🟡 |
| 37 | Registro das receitas e despesas previstas e realizadas; começar anotando ganhos e gastos de um período | Susesp | Primeiro passo certo; definição diferente | 🟡 |
| 38 | Receitas fixas e variáveis; despesas fixas, variáveis e eventuais, com exemplos | Susesp | Recusou | ⛔ |
| 39 | Poupar **10% a 20%** das receitas; "pague-se primeiro" = reservar a poupança assim que receber | Susesp | Recusou | ⛔ |
| 40 | Ao menos **2 meses** de gastos; renda estável → menos (servidor: 3 meses), autônomo: 6 meses a 1 ano | Susesp | Disse que o documento não dá valor | ❌ |
| 41 | Reconhecer a situação, envolver a família, cortar gastos, negociar com credores (juros/prazos), buscar renda extra | Susesp | Passos parecidos, mas do Caderno; faltou negociar e buscar renda extra | 🟡 |
| 42 | Prática de mercado (não oficial) de cobrar mais por produtos voltados a mulheres | Pink | Correto | ✅ |
| 43 | Suposição de que mulheres aceitam pagar mais; publicidade segmentada; pressão estética; ideia de "gastonas" | Pink | Os 3 primeiros certos + 3 itens de outro documento | 🟡 |
| 44 | Comparar preços; ignorar o "glitter" e focar na função; investir a diferença | Pink | Só a 1ª dica | 🟡 |
| 45–50 | Repetições das perguntas 4–9 | — | Respostas idênticas às de 4–9 (temperatura 0) | ✅ ✅/🟡 ✅ ⛔ 🟡 🟡 |

## Principais problemas encontrados

1. **Recusas indevidas (9):** a resposta estava nos documentos, mas a busca trouxe outros trechos (exercícios, bibliografia, sumário), ou a resposta ficou dividida entre dois chunks (ex.: 22). Aumentar o `TOP_K` e remover sumário e bibliografia na indexação deve reduzir esse problema.
2. **Documentos faltando (10–15):** os artigos dessas perguntas não estão em `docs/`. Nesses casos o modelo inventou respostas em 3 de 5 perguntas.
3. **Mistura de fontes (33, 37, 41, 43):** o RAG respondeu com trechos parecidos de outro documento em vez do documento de origem da pergunta.
4. **Modelo pequeno:** o `llama3.2` (3B) às vezes resume mal (27, 40) e muda a frase de recusa.

> Os itens 8, 9, 36, 49 e 50 foram marcados como parciais por serem genéricos. Não houve uma conferência frase a frase contra os artigos.
