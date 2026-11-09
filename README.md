# RAG de Educação Financeira para Mulheres

Sistema de **Retrieval-Augmented Generation (RAG)** que responde perguntas sobre educação financeira usando **apenas** documentos públicos curados. A base dá ênfase a materiais voltados para mulheres, e toda resposta vem com as fontes citadas (documento, instituição, página e link).

Tudo roda localmente: modelos via **Ollama**, banco vetorial **ChromaDB** e orquestração com **LangChain**. Nenhuma chave de API é necessária.

> Esta etapa do projeto prioriza **qualidade da recuperação, fundamentação das respostas e rastreabilidade das fontes**, não a interface.

---

## Sumário

1. [O que é RAG (e por que usar)](#1-o-que-é-rag-e-por-que-usar)
2. [Mapa dos entregáveis](#2-mapa-dos-entregáveis)
3. [Instalação](#3-instalação)
4. [Rodando do zero, passo a passo](#4-rodando-do-zero-passo-a-passo)
5. [Entendendo cada etapa](#5-entendendo-cada-etapa)
6. [Estrutura do projeto](#6-estrutura-do-projeto)
7. [Experimentos sugeridos](#7-experimentos-sugeridos)
8. [Problemas comuns](#8-problemas-comuns)
9. [O que mudou em relação à versão anterior](#9-o-que-mudou-em-relação-à-versão-anterior)

---

## 1. O que é RAG (e por que usar)

Um LLM sozinho responde com base no que "decorou" no treinamento. Isso traz três problemas para um tema como finanças:

- ele pode **inventar** (alucinar) números, leis e instituições com total confiança;
- ele **não sabe** de dados recentes, como o Relatório de Cidadania Financeira 2025 do BC;
- ele **não diz de onde** tirou a informação, e não há como verificar.

O RAG resolve isso separando o trabalho em duas partes:

```
           ┌─────────────── RECUPERAÇÃO ───────────────┐   ┌──── GERAÇÃO ────┐
pergunta → │ acha os trechos mais relevantes numa base │ → │ LLM responde    │ → resposta
           │ de documentos confiáveis (busca semântica)│   │ USANDO só esses │   + fontes
           └───────────────────────────────────────────┘   │ trechos e cita  │
                                                           └─────────────────┘
```

O LLM deixa de ser a "fonte do conhecimento" e passa a ser um **redator** que lê os trechos certos e responde com base neles. A qualidade da resposta passa a depender principalmente da **qualidade da recuperação**, e por isso ela é o foco desta etapa.

---

## 2. Mapa dos entregáveis

| Requisito | Onde está |
|---|---|
| **Artefatos** | |
| Base de conhecimento curada | [`fontes/catalogo.yaml`](fontes/catalogo.yaml) + [`docs/base_conhecimento.md`](docs/base_conhecimento.md) |
| Mínimo de 20 documentos-fonte | **26 fontes** no catálogo; comprovação em `saidas/relatorio_ingestao.md` (gerado pela ingestão) |
| Descrição da estratégia de chunking | [`docs/estrategia_chunking.md`](docs/estrategia_chunking.md) · código em `rag/chunking.py` |
| Descrição da estratégia de embeddings | [`docs/estrategia_embeddings.md`](docs/estrategia_embeddings.md) · código em `rag/embeddings.py` |
| Implementação de um banco vetorial | ChromaDB persistente em `chroma_db/` · código em `rag/banco_vetorial.py` |
| **Demonstração** | [`docs/demonstracao.md`](docs/demonstracao.md) · registros em `saidas/demonstracoes/` |
| Consulta submetida | `python consultar.py "pergunta"` → seção 1 do registro |
| Recuperação dos chunks | seção 2 do registro (ranking + similaridade + trechos) |
| Resposta fundamentada | seção 3 do registro (citações `[n]`) |
| Evidência das fontes | seção 4 do registro (tabela de fontes + verificação automática) |
| **Documentação** | |
| Diagrama de arquitetura | [`docs/arquitetura.md`](docs/arquitetura.md) |
| Pipeline de ingestão de dados | [`docs/pipeline_ingestao.md`](docs/pipeline_ingestao.md) |
| **Extra** | |
| Avaliação quantitativa da recuperação | `python avaliar.py` → `saidas/avaliacao_recuperacao_*.md` |
| Notebook didático | [`rag_notebook.ipynb`](rag_notebook.ipynb) |
| Teste automatizado | `python tests/teste_fumaca.py` |

Os diagramas estão em **Mermaid**, que o GitHub e o VS Code (com extensão) renderizam. Para exportar imagem, cole o bloco em <https://mermaid.live>.

---

## 3. Instalação

**Pré-requisitos:** Python 3.10+ e [Ollama](https://ollama.com) instalado.

```bash
# 1. ambiente virtual
python -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. modelos locais
ollama pull bge-m3                  # embeddings (multilíngue, ~1,2 GB)
ollama pull llama3.1:8b             # gerador (~4,7 GB)
# opcional, costuma escrever melhor em PT-BR:  ollama pull qwen2.5:7b

# 3. configuração (opcional: os padrões já funcionam)
cp .env.example .env
```

Para confirmar que a instalação está correta **sem** Ollama e sem internet:

```bash
python tests/teste_fumaca.py        # deve terminar com "OK – todas as verificações passaram."
```

---

## 4. Rodando do zero, passo a passo

```bash
python baixar_fontes.py     # 0. coleta: baixa as 26 fontes para data/raw/
python ingerir.py           # 1-5. carrega, limpa, divide, embeda e grava no Chroma
python consultar.py --demo  # demonstração com 6 perguntas (inclui uma fora do escopo)
python avaliar.py           # métricas de recuperação
```

Tempos de referência num MacBook (Apple Silicon): download de 1 a 3 min; ingestão de ~3 a 5 min (o relatório do BC sozinho leva ~40 s); cada consulta leva ~1 s de busca + 20 a 60 s de geração. Todos os scripts mostram o progresso na tela; a resposta aparece em streaming, palavra por palavra.

Outros usos:

```bash
python consultar.py "Mulheres pagam juros mais altos?"
python consultar.py "O que é mínimo existencial?" --sem-llm        # só recuperação
python consultar.py "O que diz o art. 7º?" --fonte lei_maria_da_penha
python ingerir.py --reindexar                                     # refaz tudo
```

---

## 5. Entendendo cada etapa

Esta seção acompanha o caminho de um documento até virar parte de uma resposta. Cada etapa indica o arquivo de código correspondente. Vale ler o código junto, porque todo módulo começa com um comentário explicando o porquê das decisões.

### Fase 1: Ingestão (preparar a base)

#### Etapa 0: Curadoria e coleta · `fontes/catalogo.yaml`, `baixar_fontes.py`

Tudo começa no **catálogo**: uma lista de 26 documentos com título, instituição, ano, URL, eixo temático e o motivo da inclusão. O catálogo é o "contrato" da base. Só entra no RAG o que está ali, e esses metadados acompanham cada pedaço de texto até a resposta final. **A rastreabilidade nasce aqui.**

O `baixar_fontes.py` baixa cada URL e registra num `manifesto.json` a URL efetiva, a data e o **SHA-256** do arquivo (uma "impressão digital" do conteúdo). Com isso, sempre dá para provar qual versão de qual documento estava na base.

> 💡 **Por que curar em vez de jogar qualquer coisa na base?** Num RAG, "lixo entra, lixo sai". Se a base tiver um blog com informação errada, o sistema vai citá-lo com a mesma confiança que cita o Banco Central.

#### Etapa 1: Carregar · `rag/carregadores.py`

O texto é extraído de cada arquivo. PDFs são lidos **página por página** (o número da página é guardado). HTMLs são lidos **seção por seção**, e nas leis **artigo por artigo**. É isso que permite citar "p. 48" ou "Art. 7º", e não só "o documento X".

Um detalhe importante: nas leis do Planalto, o texto riscado é texto **revogado**. Ele é descartado, para que o sistema não cite uma regra que não vale mais.

#### Etapa 2: Limpar · `rag/limpeza.py`

Texto extraído de PDF vem com ruído: palavras quebradas (`finan-ças`), o mesmo cabeçalho em todas as páginas, números de página soltos. A limpeza remove esse ruído **sem reescrever** o conteúdo. Se o cabeçalho "Banco Central do Brasil – Cidadania Financeira" ficasse em todo trecho, todos os vetores ficariam parecidos entre si, e a busca perderia precisão.

#### Etapa 3: Chunking · `rag/chunking.py` · [detalhes](docs/estrategia_chunking.md)

Os textos são divididos em **chunks** de ~1000 caracteres (1 a 2 parágrafos), com 150 caracteres de sobreposição.

- **Por que dividir?** Um vetor representa o texto inteiro. Um PDF de 70 páginas vira um vetor "médio", que não se parece muito com pergunta nenhuma. Trechos pequenos geram vetores focados.
- **Por que não dividir demais?** Frases soltas perdem o contexto ("isso", "a tabela acima").
- **Como?** Corte recursivo: primeiro em parágrafos, depois linhas, depois frases. Assim o corte cai sempre na fronteira mais natural.
- **Cabeçalho contextual:** cada chunk começa com `[Título – Instituição – Ano | p. X]`. Isso ajuda a busca e mostra ao LLM de onde vem cada trecho.

#### Etapa 4: Embeddings · `rag/embeddings.py` · [detalhes](docs/estrategia_embeddings.md)

Cada chunk vira um **vetor** de 1024 números, gerado pelo modelo `bge-m3`. Textos de significado parecido geram vetores próximos, mesmo com palavras diferentes ou em idiomas diferentes. "Reserva de emergência" fica perto de "dinheiro guardado para imprevistos". A proximidade é medida pela **similaridade de cosseno** (1 = mesmo sentido, 0 = sem relação).

Duas regras de ouro: (1) usar **o mesmo modelo** para os documentos e para a pergunta; (2) respeitar os **prefixos** que alguns modelos exigem (o código faz isso sozinho).

#### Etapa 5: Banco vetorial · `rag/banco_vetorial.py`

O **ChromaDB** guarda cada chunk com ID, vetor, texto e metadados (fonte, página, URL, hash...). Ele cria um índice (HNSW) que acha os vizinhos mais próximos de um vetor sem comparar com todos os outros.

A ingestão é **idempotente**: o hash de cada arquivo fica gravado. Rodar de novo pula o que não mudou e reprocessa só o que foi alterado.

### Fase 2: Consulta (responder perguntas)

#### Etapa 6: Recuperação · `rag/recuperacao.py`

1. A pergunta vira um vetor (mesmo modelo, prefixo de *query*).
2. O Chroma devolve os **30** chunks mais próximos.
3. Os que estão abaixo do **limiar** de similaridade (0,35) são descartados.
4. Cada documento pode contribuir com **no máximo 3** trechos (diversidade).
5. Os **6** melhores seguem para o LLM.

> 💡 O passo 4 existe porque documentos longos dominam o topo da busca com trechos quase iguais. Limitar por fonte faz o LLM ver o que o BC, o Sebrae e a ANBIMA dizem, e não 6 páginas do mesmo relatório.

#### Etapa 7: Geração fundamentada · `rag/geracao.py`

O LLM recebe os trechos numerados `[1]..[6]` e regras explícitas: usar só os trechos, citar `[n]` após cada afirmação e dizer quando as fontes não respondem. A temperatura é 0, para respostas estáveis.

Se nenhum trecho passou do limiar, **o LLM nem é chamado**, e o sistema responde que não encontrou informação na base. É melhor admitir que não sabe do que inventar.

#### Etapa 8: Evidências · `rag/evidencias.py`

O código **não confia** no LLM: ele extrai as citações da resposta e confere se cada `[n]` corresponde a um trecho realmente enviado. O registro salvo (`.md` e `.json`) contém a pergunta, a configuração, o ranking de todos os candidatos, a resposta e uma tabela **citação → documento → página → link**. Com ele, qualquer pessoa pode conferir a resposta no documento original.

### Avaliação · `avaliar.py`

Para medir a recuperação com números, `avaliacao/perguntas.yaml` tem 15 perguntas, cada uma com as fontes que *deveriam* ser encontradas (o gabarito):

| Métrica | Pergunta que responde |
|---|---|
| **Hit@k** | Em quantas perguntas pelo menos uma fonte certa apareceu entre os k trechos? |
| **MRR** | Em média, em que posição aparece a primeira fonte certa? (1,0 = sempre em 1º) |
| **Precisão@k** | Dos k trechos, que fração veio de fontes certas? |
| **Recall de fontes@k** | Das fontes certas, quantas foram encontradas? |

> ⚠️ O gabarito foi escrito a partir do tema de cada documento. Depois da primeira ingestão, confira se o conteúdo está mesmo lá (`data/processed/<id>.jsonl`) e ajuste. Validar o gabarito também faz parte do trabalho.

---

## 6. Estrutura do projeto

```
rag_financas_mulheres/
├── README.md                  ← você está aqui
├── requirements.txt
├── .env.example               ← parâmetros (modelos, chunk, k, limiar)
├── baixar_fontes.py           ← etapa 0: coleta
├── ingerir.py                 ← etapas 1-5: pipeline de ingestão
├── consultar.py               ← etapas 6-8: demonstração
├── avaliar.py                 ← métricas de recuperação
├── rag_notebook.ipynb         ← o pipeline célula por célula, para estudar
├── fontes/catalogo.yaml       ← BASE DE CONHECIMENTO CURADA (26 fontes)
├── avaliacao/perguntas.yaml   ← gabarito da avaliação
├── rag/                       ← código do pipeline (um módulo por etapa)
│   ├── config.py   catalogo.py   carregadores.py   limpeza.py   chunking.py
│   └── embeddings.py   banco_vetorial.py   recuperacao.py   geracao.py   evidencias.py
├── docs/                      ← documentação dos entregáveis
│   ├── arquitetura.md         ← diagramas
│   ├── pipeline_ingestao.md
│   ├── estrategia_chunking.md
│   ├── estrategia_embeddings.md
│   ├── base_conhecimento.md
│   └── demonstracao.md
├── tests/teste_fumaca.py      ← testa tudo sem Ollama/internet
├── data/raw/                  ← (gerado) documentos baixados + manifesto
├── data/processed/            ← (gerado) chunks em JSONL, para inspeção
├── chroma_db/                 ← (gerado) banco vetorial
└── saidas/                    ← (gerado) relatório de ingestão, demonstrações, avaliação
```

---

## 7. Experimentos sugeridos

Mudar um parâmetro por vez e comparar no `avaliar.py` é a melhor forma de entender o efeito de cada decisão, e dá ótimo material para o relatório.

| Experimento | Como | O que observar |
|---|---|---|
| Semântico × lexical | `EMBEDDING_PROVIDER=hash python ingerir.py` e `... avaliar.py` | Quanto o embedding semântico ganha, sobretudo em perguntas com sinônimos e na fonte em inglês |
| Modelo de embedding | `EMBEDDING_MODEL=nomic-embed-text` (pull antes) | Efeito de um modelo focado em inglês sobre uma base em português |
| Tamanho do chunk | `CHUNK_SIZE=500` ou `2000` + `COLLECTION_NAME=teste` + `--reindexar` | Trade-off entre precisão e contexto |
| Diversidade | `MAX_POR_FONTE=6` (sem limite efetivo) | Quantas instituições diferentes aparecem nas respostas |
| Limiar | `LIMIAR_SIMILARIDADE=0.5` | Perguntas fora do escopo passam a ser recusadas sem chamar o LLM? |
| Gerador | `LLM_MODEL=qwen2.5:7b` | Qualidade do português e disciplina nas citações |

---

## 8. Problemas comuns

| Sintoma | Causa provável | Solução |
|---|---|---|
| Consulta "parada" depois de mostrar os trechos | o LLM está gerando (1ª consulta também carrega o modelo, ~30 s) | aguarde: o texto aparece em streaming; consultas seguintes são mais rápidas. Para ir mais rápido: `LLM_MODEL=llama3.2:3b` |
| Download parado numa fonte | servidor lento | o script desiste sozinho após `--prazo` (120 s) e tenta a URL alternativa |
| Muitas linhas "fontTools is required..." | aviso inofensivo do pypdf | já silenciado nesta versão; o texto é extraído normalmente |
| `Connection refused` em `localhost:11434` | Ollama não está rodando | `ollama serve` (ou abra o app do Ollama) |
| `model "bge-m3" not found` | modelo não baixado | `ollama pull bge-m3` |
| Aviso "SSL não verificado" no download | sites .gov.br/.mil.br com cadeia ICP-Brasil | o script refaz sem verificação e registra no manifesto; a integridade fica no SHA-256 |
| Download salvou HTML no lugar do PDF / erro "não devolveu um PDF" | link mudou ou página intermediária | atualize a URL no catálogo ou salve manualmente em `data/raw/<id>.pdf` |
| "nenhum texto extraível" | PDF escaneado (imagem) | troque a fonte ou aplique OCR antes |
| Banco vazio em `consultar.py` | ingestão não rodou **com o mesmo modelo** | `python ingerir.py` com o mesmo `.env` |
| Resposta sem citações | LLM desobedeceu ao prompt | troque para `qwen2.5:7b` ou reduza `TOP_K` |
| Mudou `CHUNK_SIZE` e nada mudou | arquivos iguais → ingestão pulou | `python ingerir.py --reindexar` |

---

## 9. O que mudou em relação à versão anterior

| Antes | Agora | Por quê |
|---|---|---|
| 1 PDF fora do tema (`tools_rag.pdf`) | 26 fontes públicas curadas sobre finanças e mulheres | requisito de base curada com ≥ 20 documentos |
| `nomic-embed-text` sem prefixos | `bge-m3` multilíngue (prefixos tratados para qualquer modelo) | base em português; prefixo ausente degrada a busca silenciosamente |
| Distância L2 (padrão do Chroma) | Cosseno | similaridade interpretável e limiar consistente |
| Só a página como metadado | título, instituição, ano, URL, página/seção, eixo, hash | rastreabilidade |
| Sem limpeza | hífens, cabeçalhos repetidos, texto revogado | menos ruído nos vetores |
| Top-5 direto ao LLM | busca 30 → limiar → máx. 3 por fonte → top-6 | qualidade e diversidade da recuperação |
| Resposta sem citações | citações `[n]` validadas pelo código + registro de evidências | fundamentação e rastreabilidade |
| Prompt em inglês | prompt em português com regra de recusa | respostas em PT-BR e sem invenção |
| Sem avaliação | Hit@k, MRR, precisão e recall com gabarito | medir a qualidade da recuperação |
| Chave da OpenAI no `.env` | nenhuma chave; tudo local | **revogue a chave antiga**, que estava no zip enviado |
