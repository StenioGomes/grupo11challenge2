# Estratégia de chunking

## O problema

O modelo de embedding resume um texto inteiro em **um único vetor**. Se esse texto for um PDF de 70 páginas sobre finanças pessoais, o vetor vira uma média de orçamento, crédito, investimento e aposentadoria. Ele fica "meio parecido" com qualquer pergunta e muito parecido com nenhuma.

Além disso, o LLM tem uma janela de contexto limitada, e enviar documentos inteiros desperdiça essa janela com texto irrelevante.

A solução é dividir os documentos em **chunks**: trechos pequenos o suficiente para tratar de uma ideia e grandes o suficiente para fazer sentido sozinhos.

## O equilíbrio

| Chunk muito pequeno (ex.: 200 car.) | Chunk muito grande (ex.: 4000 car.) |
|---|---|
| vetor bem focado | vetor diluído (mistura assuntos) |
| perde contexto ("isso", "a tabela acima") | carrega o contexto junto |
| o LLM recebe frases soltas | o LLM recebe muito texto irrelevante |
| muitos chunks: mais armazenamento e custo de embedding | poucos chunks: recuperação grosseira |

## Parâmetros escolhidos

| Parâmetro | Valor | Justificativa |
|---|---|---|
| Método | `RecursiveCharacterTextSplitter` | Respeita a estrutura do texto (ver abaixo) |
| `chunk_size` | **1000 caracteres** | ≈ 1 a 2 parágrafos, ≈ 200 a 250 tokens em português. Cabe uma ideia completa (um conceito, um artigo de lei, um achado de pesquisa) |
| `chunk_overlap` | **150 caracteres (15%)** | Uma frase cortada no fim de um chunk reaparece no começo do próximo |
| Unidade de divisão | dentro de cada **página** (PDF) ou **seção/artigo** (HTML) | Cada chunk tem um único localizador, o que torna a citação exata |
| Tamanho mínimo | 80 caracteres | Descarta restos como "Sumário" ou títulos soltos |
| Duplicatas | removidas por hash dentro do documento | Evita trechos repetidos (ex.: boxes que se repetem) |
| Cabeçalho contextual | `[Título – Instituição – Ano \| p. X]` | Ver abaixo |

Com 6 chunks por consulta, o contexto enviado ao LLM fica em torno de 6 × 1100 ≈ 6.600 caracteres (≈ 1.600 tokens). Isso cabe com folga na janela do `llama3.1:8b` e deixa espaço para as instruções e a resposta.

## Como funciona a divisão recursiva

O splitter recebe uma lista ordenada de separadores, do mais "semântico" para o menos:

```
"\n\n"  → parágrafo
"\n"    → linha
". " "? " "! "  → fim de frase
"; " ": "       → partes de frase
", "    → vírgula
" "     → palavra
""      → caractere (último recurso)
```

Primeiro ele tenta cortar por parágrafo. Se um parágrafo ainda tem mais de 1000 caracteres, só esse pedaço é dividido por linha, depois por frase, e assim por diante. O resultado é que o corte acontece sempre na fronteira mais natural possível, e quase nunca no meio de uma frase. Com `keep_separator="end"`, o ponto final fica no chunk da frase a que pertence.

Exemplo, num trecho de lei:

```
Art. 7º São formas de violência doméstica e familiar contra a mulher, entre outras:
I - a violência física, ...;
...
IV - a violência patrimonial, entendida como qualquer conduta que configure retenção,
subtração, destruição parcial ou total de seus objetos, ...
```

Como o carregador de HTML já separa a lei por artigo, o Art. 7º vira uma unidade própria. Se ele passar de 1000 caracteres, o splitter corta entre os incisos (nas quebras de linha), e não no meio da definição de violência patrimonial.

## Cabeçalho contextual

Cada chunk é gravado assim:

```
[Relatório de Cidadania Financeira 2025 – Banco Central do Brasil – 2025 | p. 48]
Para uma mesma raça, as mulheres contrataram créditos mais caros que os homens...
```

Esse cabeçalho:

1. **entra no embedding**, de modo que trechos genéricos ("conforme o gráfico...") ficam associados ao tema e à instituição do documento;
2. **é lido pelo LLM**, que sabe de onde vem cada trecho;
3. custa pouco, cerca de 100 caracteres por chunk.

## Por que não outras estratégias?

| Estratégia | Por que não foi a escolhida (por enquanto) |
|---|---|
| Tamanho fixo sem respeitar fronteiras | Corta frases e palavras no meio |
| Um chunk por página inteira | Páginas de relatório misturam vários assuntos; o tamanho varia muito |
| Chunking semântico (corta onde o embedding muda) | Exige embedar cada frase na ingestão (muito mais lento no Ollama local); o ganho é incerto em documentos já bem estruturados. É um bom experimento futuro |
| Chunks hierárquicos (parent/child) | Mais complexo; útil se as respostas precisarem de muito contexto ao redor |

## Como experimentar

Mude o tamanho no `.env` e compare as métricas:

```bash
CHUNK_SIZE=600 CHUNK_OVERLAP=100 COLLECTION_NAME=teste_600 python ingerir.py
CHUNK_SIZE=600 CHUNK_OVERLAP=100 COLLECTION_NAME=teste_600 python avaliar.py
```

Se o MRR subir e a precisão cair, os chunks menores estão achando o lugar certo, mas trazendo pouca informação. Esse tipo de leitura das métricas é o que justifica a escolha final no relatório.
