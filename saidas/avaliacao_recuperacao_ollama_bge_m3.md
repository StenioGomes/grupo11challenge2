# Avaliação da recuperação

Gerado em 09/11/2026 09:47. Perguntas avaliadas: 16.

Configuração: `embedding_provider=ollama`, `embedding_model=bge-m3`, `llm_model=llama3.1:8b`, `chunk_size=1000`, `chunk_overlap=150`, `top_k=6`, `fetch_k=30`, `max_por_fonte=3`, `limiar_similaridade=0.35`, `collection=financas_mulheres__ollama__bge_m3`

| Métrica | Valor |
|---|---:|
| Hit@6 | 1.000 |
| MRR | 0.896 |
| Precisão@6 | 0.719 |
| Recall de fontes@6 | 0.823 |

| Pergunta | 1º relevante na posição | Precisão | Recall | Sim. top-1 | Fontes recuperadas |
|---|:---:|---:|---:|---:|---|
| O que é violência patrimonial? | 1 | 1.00 | 0.67 | 0.677 | tjsp_cartilha_rompa, mpmg_cartilha_sempre_vivas, mpmg_cartilha_sempre_vivas, mpmg_cartilha_sempre_vivas, tjsp_cartilha_rompa, tjsp_cartilha_rompa |
| Por que a independência financeira é importante para mulheres em situação de violência? | 2 | 0.17 | 0.50 | 0.565 | bcb_relatorio_cidadania_financeira_2025, tjsp_cartilha_rompa, bcb_relatorio_cidadania_financeira_2025, bcb_relatorio_cidadania_financeira_2021, bcb_relatorio_cidadania_financeira_2021, worldbank_findex_2025_women |
| Como o custo do crédito varia entre homens e mulheres no Brasil? | 3 | 0.33 | 0.33 | 0.717 | bcb_relatorio_cidadania_financeira_2021, bcb_relatorio_cidadania_financeira_2021, bcb_relatorio_cidadania_financeira_2025, bcb_relatorio_cidadania_financeira_2025, bcb_serie_cidadania_7_findex, bcb_relatorio_cidadania_financeira_2021 |
| Quais as dificuldades das empreendedoras para conseguir empréstimo? | 1 | 1.00 | 0.67 | 0.708 | sebrae_credito_empreendedoras, bcb_relatorio_cidadania_financeira_2025, bcb_relatorio_cidadania_financeira_2025, sebrae_credito_empreendedoras, bcb_relatorio_cidadania_financeira_2025, sebrae_credito_empreendedoras |
| Como fazer um orçamento doméstico? | 1 | 0.67 | 1.00 | 0.734 | bcb_caderno_educacao_financeira, bcb_caderno_educacao_financeira, bcb_caderno_educacao_financeira, caixa_fundamentos_educacao_financeira, bcb_relatorio_cidadania_financeira_2025, bcb_relatorio_cidadania_financeira_2025 |
| Para que serve uma reserva de emergência e quanto guardar? | 1 | 0.67 | 1.00 | 0.682 | caixa_fundamentos_educacao_financeira, bcb_caderno_educacao_financeira, bcb_caderno_educacao_financeira, anbima_raiox9_poupanca_mulheres, bcb_caderno_educacao_financeira, bcb_relatorio_cidadania_financeira_2021 |
| O que é superendividamento segundo a lei? | 1 | 0.83 | 1.00 | 0.747 | senacon_cenario_superendividamento, procon_rio_cartilha_superendividamento, senacon_cenario_superendividamento, lei_14181_superendividamento, procon_rio_cartilha_superendividamento, bcb_relatorio_cidadania_financeira_2025 |
| O que é o mínimo existencial na renegociação de dívidas? | 2 | 0.50 | 0.33 | 0.625 | bcb_relatorio_cidadania_financeira_2025, senacon_cenario_superendividamento, senacon_cenario_superendividamento, senacon_cenario_superendividamento, bcb_caderno_educacao_financeira, bcb_relatorio_cidadania_financeira_2025 |
| Qual a porcentagem de mulheres brasileiras que investem? | 1 | 1.00 | 1.00 | 0.755 | anbima_raiox9_mulheres_investem, anbima_raiox9_mulheres_investem, anbima_raiox9_mulheres_investem, anbima_raiox9_poupanca_mulheres, anbima_raiox7_relatorio, anbima_raiox7_relatorio |
| Quais produtos de investimento as mulheres mais usam? | 1 | 1.00 | 1.00 | 0.732 | anbima_raiox9_mulheres_investem, anbima_raiox7_relatorio, anbima_raiox9_poupanca_mulheres, anbima_raiox7_relatorio, anbima_raiox7_relatorio, anbima_raiox9_mulheres_investem |
| Qual é a diferença entre homens e mulheres na posse de contas bancárias no mundo? | 1 | 1.00 | 1.00 | 0.746 | bcb_serie_cidadania_7_findex, bcb_serie_cidadania_7_findex, worldbank_findex_2025_women, worldbank_findex_2025_women, bcb_serie_cidadania_7_findex, worldbank_findex_2025_women |
| Quantas mulheres são donas de negócio no Brasil e qual o perfil delas? | 1 | 1.00 | 1.00 | 0.745 | sebrae_empreendedorismo_feminino_2023, sebrae_empreendedorismo_feminino_2023, sebrae_infografico_empreendedorismo_feminino_2024, sebrae_empreendedorismo_feminino_2023, sebrae_infografico_empreendedorismo_feminino_2024, sebrae_infografico_empreendedorismo_feminino_2024 |
| O que é cidadania financeira e quais são seus pilares? | 1 | 0.83 | 0.67 | 0.756 | bcb_relatorio_cidadania_financeira_2025, bcb_conceito_cidadania_financeira, bcb_conceito_cidadania_financeira, bcb_serie_cidadania_7_findex, bcb_conceito_cidadania_financeira, bcb_relatorio_cidadania_financeira_2025 |
| Como as mulheres dividem o tempo entre trabalho remunerado e afazeres domésticos e cuidados? | 1 | 0.50 | 1.00 | 0.700 | ibge_estatisticas_genero_3ed, bcb_relatorio_cidadania_financeira_2025, sebrae_empreendedorismo_feminino_2023, ibge_estatisticas_genero_3ed, ibge_estatisticas_genero_3ed, sebrae_empreendedorismo_feminino_2023 |
| Como se preparar financeiramente para a aposentadoria? | 1 | 0.50 | 1.00 | 0.760 | bcb_caderno_educacao_financeira, bcb_caderno_educacao_financeira, bcb_caderno_educacao_financeira, bcb_relatorio_cidadania_financeira_2025, caixa_fundamentos_educacao_financeira, bcb_relatorio_cidadania_financeira_2021 |
| Como evitar compras por impulso? | 1 | 0.50 | 1.00 | 0.630 | bcb_caderno_educacao_financeira, bcb_caderno_educacao_financeira, bcb_caderno_educacao_financeira, bcb_relatorio_cidadania_financeira_2025, procon_rio_cartilha_superendividamento, bcb_relatorio_cidadania_financeira_2025 |
