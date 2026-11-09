# Relatório de ingestão

Gerado em 09/11/2026 09:41 por `ingerir.py`.

Configuração: `embedding_provider=ollama`, `embedding_model=bge-m3`, `llm_model=llama3.1:8b`, `chunk_size=1000`, `chunk_overlap=150`, `top_k=6`, `fetch_k=30`, `max_por_fonte=3`, `limiar_similaridade=0.35`, `collection=financas_mulheres__ollama__bge_m3`

**Total no banco vetorial: 2302 chunks de 20 documentos-fonte.**

| # | Fonte (id) | Formato | Idioma | Foco mulheres | Unid. | Chunks no banco | Chunk médio (car.) | Status desta execução |
|---:|---|:---:|:---:|:---:|---:|---:|---:|---|
| 1 | `bcb_caderno_educacao_financeira` | pdf | pt |  | 97 | 235 | 734 | indexado |
| 2 | `bcb_gfp_orcamento` | pdf | pt |  |  | 0 |  | ausente |
| 3 | `bcb_gfp_consumo` | pdf | pt |  |  | 0 |  | ausente |
| 4 | `bcb_gfp_credito` | pdf | pt |  |  | 0 |  | ausente |
| 5 | `bcb_gfp_investimentos` | pdf | pt |  |  | 0 |  | ausente |
| 6 | `bcb_gfp_relacao_dinheiro` | pdf | pt |  |  | 0 |  | ausente |
| 7 | `caixa_fundamentos_educacao_financeira` | pdf | pt |  | 20 | 26 | 654 | indexado |
| 8 | `bcb_relatorio_cidadania_financeira_2025` | pdf | pt | ✔ | 165 | 638 | 697 | indexado |
| 9 | `bcb_serie_cidadania_7_findex` | pdf | pt |  | 42 | 116 | 685 | indexado |
| 10 | `ibge_estatisticas_genero_3ed` | pdf | pt | ✔ | 15 | 97 | 692 | indexado |
| 11 | `anbima_raiox9_mulheres_investem` | html | pt | ✔ | 1 | 6 | 653 | indexado |
| 12 | `anbima_raiox9_poupanca_mulheres` | html | pt | ✔ | 1 | 6 | 745 | indexado |
| 13 | `anbima_raiox7_relatorio` | pdf | pt |  | 77 | 141 | 685 | indexado |
| 14 | `sebrae_empreendedorismo_feminino_2023` | pdf | pt | ✔ | 55 | 93 | 616 | indexado |
| 15 | `sebrae_infografico_empreendedorismo_feminino_2024` | pdf | pt | ✔ | 1 | 10 | 883 | indexado |
| 16 | `sebrae_credito_empreendedoras` | html | pt | ✔ | 7 | 5 | 519 | indexado |
| 17 | `worldbank_findex_2025_women` | html | en | ✔ | 8 | 10 | 598 | indexado |
| 18 | `bcb_relatorio_cidadania_financeira_2021` | pdf | pt |  | 139 | 467 | 695 | indexado |
| 19 | `cvm_quiz_educacao_financeira_mulheres` | pdf | pt | ✔ |  | 0 |  | ausente |
| 20 | `bcb_conceito_cidadania_financeira` | pdf | pt |  | 47 | 212 | 708 | indexado |
| 21 | `lei_maria_da_penha` | pdf | pt | ✔ | 2 | 5 | 747 | indexado |
| 22 | `tjsp_cartilha_rompa` | pdf | pt | ✔ | 9 | 8 | 706 | indexado |
| 23 | `mpmg_cartilha_sempre_vivas` | pdf | pt | ✔ | 24 | 56 | 633 | indexado |
| 24 | `lei_14181_superendividamento` | html | pt |  | 6 | 24 | 782 | indexado |
| 25 | `procon_rio_cartilha_superendividamento` | pdf | pt |  | 11 | 11 | 274 | indexado |
| 26 | `senacon_cenario_superendividamento` | pdf | pt |  | 60 | 136 | 694 | indexado |

Legenda: *Unid.* = páginas (PDF) ou seções (HTML) com texto após a limpeza. *inalterado* = arquivo com o mesmo SHA-256 da última ingestão (não foi reprocessado).
