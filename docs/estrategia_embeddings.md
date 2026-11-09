# Estratégia de embeddings

## O que é um embedding

Um modelo de embedding transforma um texto em um vetor de números. No `bge-m3`, são 1024 números. O modelo foi treinado para que textos com **significado** parecido fiquem **próximos** nesse espaço, mesmo quando usam palavras diferentes:

```
"reserva de emergência"                         ─┐
"dinheiro guardado para imprevistos"             ├─ vetores próximos
"colchão financeiro para emergências"           ─┘

"violência patrimonial"                          ── vetor distante dos três acima
```

É isso que diferencia a busca semântica da busca por palavra-chave. A pergunta "posso perder meus bens numa relação abusiva?" acha o artigo que define violência patrimonial, mesmo sem nenhuma palavra em comum.

## Como medimos a proximidade: similaridade de cosseno

A similaridade de cosseno mede o **ângulo** entre dois vetores, sem levar em conta o tamanho deles:

```
cos(a, b) = (a · b) / (|a| · |b|)
```

- 1 = mesma direção (mesmo significado)
- 0 = sem relação
- valores negativos são raros em modelos de texto

O Chroma devolve a **distância** de cosseno (`1 − cos`). O código converte de volta para similaridade (`1 − distância`), que é mais fácil de ler e de usar como limiar. Por isso a coleção é criada com `hnsw:space = cosine`; o padrão do Chroma seria a distância L2.

## Modelo escolhido: `bge-m3`

| Critério | `bge-m3` | `nomic-embed-text` (usado na versão anterior) |
|---|---|---|
| Idiomas | **multilíngue** (100+), inclui português | treinado majoritariamente em inglês |
| Dimensões | 1024 | 768 |
| Contexto máximo | 8192 tokens | 8192 tokens |
| Prefixo de tarefa | não precisa | **obrigatório** (`search_document:` / `search_query:`) |
| Execução | local, via `ollama pull bge-m3` | local |

O motivo principal é o idioma. A base tem 25 documentos em português e 1 em inglês (Banco Mundial), e as perguntas serão em português. Um modelo multilíngue coloca "gender gap in account ownership" perto de "diferença entre homens e mulheres na posse de contas". Ele faz uma busca **entre idiomas**, sem precisar traduzir nada.

Quanto ao contexto: os chunks têm ≈ 250 tokens, bem abaixo dos 8192 suportados, então nenhum trecho é truncado em silêncio.

## Prefixos de tarefa (cuidado comum)

Alguns modelos foram treinados com um prefixo diferente para documentos e para perguntas, porque perguntas e respostas têm formas diferentes. No `nomic-embed-text`:

```
documento: "search_document: A reserva de emergência deve cobrir..."
pergunta:  "search_query: quanto guardar para emergências?"
```

Esquecer o prefixo **não dá erro**. A recuperação simplesmente fica pior, e é difícil perceber por quê. A versão original do projeto tinha esse problema. A classe `EmbeddingsComPrefixo` (em `rag/embeddings.py`) aplica o prefixo certo automaticamente conforme o modelo configurado, a partir da tabela `PREFIXOS`. O `bge-m3` não usa prefixo.

## Regras que o sistema garante

1. **Mesmo modelo na ingestão e na consulta.** Vetores de modelos diferentes vivem em espaços diferentes, às vezes até com dimensões diferentes, e compará-los não faz sentido. Por isso o nome da coleção inclui o modelo (`financas_mulheres__ollama__bge_m3`). Trocar o modelo cria uma coleção nova, em vez de corromper a antiga.
2. **O que é embedado é o chunk com o cabeçalho contextual** (título + instituição + ano + página). Ver [estrategia_chunking.md](estrategia_chunking.md).
3. **Envio em lotes de 32**, para não sobrecarregar o Ollama.

## Baseline lexical (`EMBEDDING_PROVIDER=hash`)

Para testar sem Ollama e para ter uma **base de comparação**, existe um embedding lexical simples. Cada palavra (e par de palavras) é mapeada por hash para uma posição do vetor. A similaridade passa a medir quantas palavras os textos têm em comum.

Ele não entende sinônimos nem outros idiomas, e é exatamente isso que o torna útil na avaliação. Se o `bge-m3` não for claramente melhor que ele nas métricas, há algo errado (prefixo, limpeza, chunk).

```bash
EMBEDDING_PROVIDER=hash python ingerir.py
EMBEDDING_PROVIDER=hash python avaliar.py
python avaliar.py                          # bge-m3
# compare os dois arquivos em saidas/avaliacao_recuperacao_*.md
```

## Limiar de similaridade

Cada modelo tem sua própria "escala" de cosseno. No `bge-m3`, trechos relevantes em português costumam ficar acima de ~0,5, e trechos sem relação ficam mais baixos. O limiar padrão é **0,35**, propositalmente permissivo; quem filtra o que não serve é o LLM, com a regra de dizer quando as fontes não respondem.

Para calibrar: rode `python avaliar.py` e veja a coluna "Sim. top-1". Depois rode uma pergunta fora do escopo com `consultar.py --sem-llm` e veja a similaridade dela. O limiar ideal fica entre as duas.

## Alternativas para experimentar

| Modelo (Ollama) | Observação |
|---|---|
| `bge-m3` | padrão; multilíngue |
| `nomic-embed-text-v2-moe` | multilíngue, usa prefixos (já tratados) |
| `nomic-embed-text` | inglês; bom para comparar o efeito do idioma |
| `mxbai-embed-large` | inglês; prefixo só na pergunta (já tratado) |

Para trocar, basta mudar o `.env`, por exemplo `EMBEDDING_MODEL=nomic-embed-text-v2-moe`, e rodar `ollama pull <modelo>`, `python ingerir.py` e `python avaliar.py`.
