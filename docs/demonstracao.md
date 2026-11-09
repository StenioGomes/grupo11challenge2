# Demonstração

A demonstração precisa mostrar quatro coisas. Cada uma corresponde a uma seção do registro gerado automaticamente em `saidas/demonstracoes/consulta_<data>.md`:

| Requisito | Onde aparece no registro |
|---|---|
| Consulta submetida ao sistema | Seção **1. Consulta submetida** (+ configuração usada) |
| Recuperação dos chunks mais relevantes | Seção **2. Recuperação**: ranking dos candidatos com similaridade, quais foram enviados ao LLM e o texto de cada trecho |
| Resposta fundamentada no conteúdo recuperado | Seção **3. Resposta fundamentada**: cada afirmação com citação `[n]` |
| Evidência das fontes utilizadas | Seção **4. Evidência das fontes**: tabela citação → documento, instituição, página/seção e link + verificação automática das citações |

## Como gerar

```bash
ollama serve                         # se o Ollama não estiver rodando
python consultar.py --demo           # 6 perguntas prontas
python consultar.py "sua pergunta"   # pergunta livre
python consultar.py "sua pergunta" --sem-llm   # só a recuperação
```

As perguntas de `--demo` foram escolhidas para cobrir casos diferentes:

| Pergunta | O que ela demonstra |
|---|---|
| Violência patrimonial e autonomia financeira | Cruza a lei (Planalto) com cartilhas e o material da CVM; citação por artigo |
| Juros para mulheres x homens | Dado quantitativo recente (RCF 2025 do BC, Sebrae) |
| Como montar um orçamento | Conteúdo conceitual, várias fontes concordando (BCB, Caixa) |
| Superendividamento e direitos | Texto legal + versão didática do Procon |
| Investimento mais usado pelas mulheres | Notícia de dados (ANBIMA) |
| **Melhor criptomoeda do mês** | **Pergunta fora do escopo:** o sistema deve dizer que as fontes não respondem, e não inventar |

A última pergunta é tão importante quanto as outras. Mostrar que o sistema **recusa** quando não tem base é uma prova de fundamentação.

## O que observar (e comentar na apresentação)

1. **Similaridade dos trechos.** Os primeiros trechos são claramente sobre o tema? Há uma queda nítida entre os relevantes e os demais?
2. **Diversidade.** Os 6 trechos vêm de instituições diferentes? (Efeito do limite de 3 por fonte.)
3. **Toda afirmação tem `[n]`?** Abra o trecho citado e confirme que a informação está lá. Essa é a checagem manual de fidelidade.
4. **Trechos enviados mas não citados.** São normais (o trecho era parecido, mas não necessário); só valem atenção se muitos.
5. **Avisos.** "Resposta não fundamentada" ou "citações inválidas" indicam que o LLM desobedeceu às regras. Teste trocar para `LLM_MODEL=qwen2.5:7b`.

## Complementando com métricas

A demonstração mostra casos individuais; a avaliação mostra o comportamento médio:

```bash
python avaliar.py                       # bge-m3
EMBEDDING_PROVIDER=hash python ingerir.py && EMBEDDING_PROVIDER=hash python avaliar.py   # baseline
```

Colocar as duas tabelas lado a lado (Hit@6, MRR, Precisão, Recall) é a forma mais direta de mostrar, com números, a **qualidade da recuperação**, que é o foco desta etapa.
