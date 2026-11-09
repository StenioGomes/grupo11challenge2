# Base de conhecimento curada

A base tem **26 documentos-fonte públicos** (o mínimo exigido é 20). **12** deles tratam especificamente de mulheres ou de gênero; os demais dão a base conceitual (orçamento, crédito, investimento, direitos do consumidor) de que essas mulheres precisam.

A definição oficial da base está em [`fontes/catalogo.yaml`](../fontes/catalogo.yaml). Esta página explica os critérios e lista as fontes.

## Critérios de curadoria

1. **Fonte pública e de acesso livre.** Órgãos públicos (BCB, IBGE, CVM, Senacon, Planalto, tribunais, Ministério Público), organismos internacionais (Banco Mundial) e entidades de referência do setor (ANBIMA, Sebrae).
2. **Autoridade.** Prioridade à instituição que produz o dado ou a norma (o BCB para crédito, o IBGE para estatísticas de gênero, a lei no texto oficial do Planalto), e não a reportagens sobre ela.
3. **Foco em mulheres, sempre que possível.** Dados de gênero, barreiras específicas (crédito mais caro, violência patrimonial, dupla jornada) e orientações voltadas às mulheres.
4. **Complementaridade.** Cada eixo temático tem mais de uma fonte. Isso permite cruzar informações e reduz a dependência de um único documento.
5. **Texto extraível.** PDFs com camada de texto e páginas HTML (sem necessidade de OCR).
6. **Atualidade, com contexto.** Dados recentes (RCF 2025, Raio X 9ª edição, Findex 2025) convivem com materiais conceituais mais antigos (Caderno do BC, 2013), cujos conceitos não envelhecem. O ano fica nos metadados e aparece em toda citação.

## Composição por eixo

| Eixo | Nº de fontes |
|---|---:|
| Fundamentos de educação financeira | 5 |
| Crédito, dívidas e superendividamento | 5 |
| Investimentos e aposentadoria | 2 |
| Mulheres e finanças: dados e diagnóstico | 9 |
| Educação e proteção financeira das mulheres | 5 |

Idiomas: PT = 25, EN = 1. A fonte em inglês é recuperada por perguntas em português graças ao modelo de embedding multilíngue.

## Lista de fontes

| # | id | Documento | Instituição | Ano | Formato | Foco mulheres | Por que está na base |
|---:|---|---|---|---:|:---:|:---:|---|
| 1 | `bcb_caderno_educacao_financeira` | [Caderno de Educação Financeira – Gestão de Finanças Pessoais](https://www.bcb.gov.br/content/cidadaniafinanceira/documentos_cidadania/Cuidando_do_seu_dinheiro_Gestao_de_Financas_Pessoais/caderno_cidadania_financeira.pdf) | Banco Central do Brasil | 2013 | pdf |  | Material de referência do BCB: orçamento, consumo, crédito, poupança, investimento e prevenção de riscos. |
| 2 | `bcb_gfp_orcamento` | [Gestão de Finanças Pessoais – Orçamento Pessoal e Familiar (Caderno do Aluno)](https://www.5rm.eb.mil.br/images/5rm/esc_pes/sas/CaPRA/modulo3/ORAMENTO.pdf) | Banco Central do Brasil / Sescoop (cópia hospedada pelo Exército Brasileiro) | 2015 | pdf |  | Módulo prático sobre montar e acompanhar o orçamento doméstico. |
| 3 | `bcb_gfp_consumo` | [Gestão de Finanças Pessoais – Consumo](https://www.5rm.eb.mil.br/images/5rm/esc_pes/sas/CaPRA/modulo3/CONSUMO.pdf) | Banco Central do Brasil / Sescoop (cópia hospedada pelo Exército Brasileiro) | 2015 | pdf |  | Consumo consciente, decisões de compra e armadilhas comportamentais. |
| 4 | `bcb_gfp_credito` | [Gestão de Finanças Pessoais – Crédito e Endividamento](https://www.5rm.eb.mil.br/images/5rm/esc_pes/sas/CaPRA/modulo3/CRDITO-ENDIVIDAMENTO.pdf) | Banco Central do Brasil / Sescoop (cópia hospedada pelo Exército Brasileiro) | 2015 | pdf |  | Uso responsável do crédito, juros e como sair do endividamento. |
| 5 | `bcb_gfp_investimentos` | [Gestão de Finanças Pessoais – Investimentos e Aposentadoria](https://www.5rm.eb.mil.br/images/5rm/esc_pes/sas/CaPRA/modulo3/INVESTIMENTOS-APOSENTADORIA.pdf) | Banco Central do Brasil / Sescoop (cópia hospedada pelo Exército Brasileiro) | 2015 | pdf |  | Poupança, reserva de emergência, tipos de investimento e planejamento da aposentadoria. |
| 6 | `bcb_gfp_relacao_dinheiro` | [Gestão de Finanças Pessoais – Nossa Relação com o Dinheiro](https://www.5rm.eb.mil.br/images/5rm/esc_pes/sas/CaPRA/modulo3/RELAO-COM-DINHEIRO.pdf) | Banco Central do Brasil / Sescoop (cópia hospedada pelo Exército Brasileiro) | 2015 | pdf |  | Aspectos comportamentais e emocionais na relação com o dinheiro. |
| 7 | `caixa_fundamentos_educacao_financeira` | [Fundamentos de Educação Financeira (Cartilha 1)](https://www.caixa.gov.br/Downloads/educacao-financeira-cartilhas/CARTILHA1_EDUCACAO_FINANCEIRA.pdf) | Caixa Econômica Federal | 2009 | pdf |  | Segunda fonte institucional sobre conceitos básicos (redundância ajuda a validar respostas). |
| 8 | `bcb_relatorio_cidadania_financeira_2025` | [Relatório de Cidadania Financeira 2025](https://www.bcb.gov.br/content/cidadaniafinanceira/documentos_cidadania/RIF/relatorio_de_cidadania_financeira_2025.pdf) | Banco Central do Brasil | 2025 | pdf | ✔ | Primeira edição com recorte de crédito por gênero e raça (custo do crédito, endividamento de risco). |
| 9 | `bcb_serie_cidadania_7_findex` | [Série Cidadania Financeira nº 7 – Global Findex: o Brasil na comparação internacional](https://www.bcb.gov.br/content/cidadaniafinanceira/documentos_cidadania/serie_cidadania/serie_cidadania_financeira_7_Global_Findex.pdf) | Banco Central do Brasil | 2023 | pdf |  | Inclusão financeira do Brasil comparada a outros países, com indicadores por sexo. |
| 10 | `ibge_estatisticas_genero_3ed` | [Estatísticas de Gênero – Indicadores sociais das mulheres no Brasil (3ª edição, informativo)](https://biblioteca.ibge.gov.br/visualizacao/livros/liv102066_informativo.pdf) | IBGE | 2024 | pdf | ✔ | Contexto socioeconômico: renda, trabalho de cuidado e participação econômica das mulheres. |
| 11 | `anbima_raiox9_mulheres_investem` | [Trinta e um por cento das mulheres brasileiras já investem, aponta Raio X do Investidor Brasileiro](https://www.anbima.com.br/pt_br/noticias/trinta-e-um-por-cento-das-mulheres-brasileiras-ja-investem-aponta-raio-x-do-investidor-brasileiro.htm) | ANBIMA | 2026 | html | ✔ | Dados recentes sobre o comportamento de investimento das mulheres (9ª edição do Raio X). |
| 12 | `anbima_raiox9_poupanca_mulheres` | [Poupança perde espaço entre mulheres investidoras, mas ainda concentra 69% do público](https://www.anbima.com.br/pt_br/imprensa/poupanca-perde-espaco-entre-mulheres-investidoras-mas-ainda-concentra-69-do-publico-revela-raio-x-do-investidor-brasileiro.htm) | ANBIMA | 2026 | html | ✔ | Produtos usados pelas investidoras e prioridades (retorno x segurança). |
| 13 | `anbima_raiox7_relatorio` | [Raio X do Investidor Brasileiro – 7ª edição (relatório)](https://www.anbima.com.br/data/files/9D/52/B3/C7/38C0091004DA0EF8EA2BA2A8/Relatorio-Raio-X-do-Investidor-7.pdf) | ANBIMA / Datafolha | 2024 | pdf |  | Relatório completo com metodologia, perfil de quem investe e de quem não investe. |
| 14 | `sebrae_empreendedorismo_feminino_2023` | [Relatório Técnico – Empreendedorismo Feminino (4º trimestre de 2023)](https://datasebrae.com.br/wp-content/uploads/2024/04/2024-04-02-relatorio_empreendedorismo_feminino_202304.pdf) (+ URL alternativa) | Sebrae / Data Sebrae | 2024 | pdf | ✔ | Perfil das donas de negócio (escolaridade, formalização, renda, chefia de domicílio) com série histórica. |
| 15 | `sebrae_infografico_empreendedorismo_feminino_2024` | [Empreendedorismo Feminino no Brasil – Infográfico (4º trimestre de 2024)](https://datasebrae.com.br/wp-content/uploads/2025/05/Empreendedorismo_FemininoVF2.0.pdf) | Sebrae / Data Sebrae | 2025 | pdf | ✔ | Dados mais recentes: setores, formalização e contribuição previdenciária das donas de negócio. |
| 16 | `sebrae_credito_empreendedoras` | [Crédito negado: Sebrae expõe dificuldades de empreendedoras no acesso a financiamentos](https://agenciasebrae.com.br/economia-e-politica/credito-negado-sebrae-expoe-dificuldades-de-empreendedoras-no-acesso-a-financiamentos/) | Agência Sebrae | 2026 | html | ✔ | Barreiras específicas das mulheres ao crédito (garantias, juros, histórico). |
| 17 | `worldbank_findex_2025_women` | [More women have financial accounts, yet equal access and use remain elusive](https://blogs.worldbank.org/en/opendata/more-women-have-financial-accounts--yet-equal-access-and-use-rem) | World Bank (Data Blog) | 2025 | html | ✔ | Visão global (Findex 2025) da diferença de gênero na posse e no uso de contas. |
| 18 | `bcb_relatorio_cidadania_financeira_2021` | [Relatório de Cidadania Financeira 2021](https://www.bcb.gov.br/content/cidadaniafinanceira/documentos_cidadania/RIF/Relatorio_de_Cidadania_Financeira_2021.pdf) | Banco Central do Brasil | 2021 | pdf |  | Edição anterior do RCF: permite comparar a evolução da inclusão e da educação financeira. |
| 19 | `cvm_quiz_educacao_financeira_mulheres` | [Quiz de Finanças Sustentáveis – Educação Financeira para Mulheres](https://www.gov.br/investidor/pt-br/educacional/publicacoes-educacionais/cvm-sustentavel/quiz-de-financas-sustentaveis-educacao-financeira-para-mulheres/) | Comissão de Valores Mobiliários (CVM) | 2024 | pdf | ✔ | Independência financeira, violência patrimonial e proteção da mulher investidora. |
| 20 | `bcb_conceito_cidadania_financeira` | [O conceito de cidadania financeira](https://www.bcb.gov.br/content/cidadaniafinanceira/documentos_cidadania/Informacoes_gerais/conceito_cidadania_financeira.pdf) | Banco Central do Brasil | 2018 | pdf |  | Define os pilares da cidadania financeira (inclusão, educação, proteção e participação) usados pela política pública. |
| 21 | `lei_maria_da_penha` | [Lei nº 11.340/2006 (Lei Maria da Penha) – texto consolidado](https://static.poder360.com.br/2024/05/Lei-Maria-da-Penha.pdf) (+ URL alternativa) | Câmara dos Deputados – Legislação Informatizada | 2006 | pdf | ✔ | Define legalmente a violência patrimonial (art. 7º, IV) e medidas de proteção patrimonial. |
| 22 | `tjsp_cartilha_rompa` | [Cartilha Rompa – Relacionamentos abusivos e violência contra a mulher](https://www.tjsp.jus.br/Download/Rompa/Cartilha.pdf) | Tribunal de Justiça de São Paulo | 2023 | pdf | ✔ | Linguagem acessível sobre formas de violência, incluindo a patrimonial, e onde buscar ajuda. |
| 23 | `mpmg_cartilha_sempre_vivas` | [Cartilha Sempre Vivas – Entenda a Lei Maria da Penha](https://www.mpmg.mp.br/data/files/98/27/D9/F2/46E5B8100ACB4BA8760849A8/cartilha-sempre-vivas-abril-2021%20_1_.pdf) | Ministério Público de Minas Gerais / ALMG | 2021 | pdf | ✔ | Exemplos práticos de violência patrimonial e rede de atendimento. |
| 24 | `lei_14181_superendividamento` | [Lei nº 14.181/2021 (Lei do Superendividamento)](https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/L14181.htm) (+ URL alternativa) | Presidência da República – Planalto | 2021 | html |  | Definição legal de superendividamento, mínimo existencial e repactuação de dívidas. |
| 25 | `procon_rio_cartilha_superendividamento` | [Cartilha Superendividamento](https://proconcarioca.prefeitura.rio/wp-content/uploads/sites/46/2026/07/CARTILHA-superendividamento.pdf) | Procon Carioca – Prefeitura do Rio de Janeiro | 2026 | pdf |  | Versão didática dos direitos do consumidor superendividado. |
| 26 | `senacon_cenario_superendividamento` | [Cenário do Superendividamento no Brasil e no Mundo (Produto 2)](https://www.gov.br/mj/pt-br/assuntos/seus-direitos/consumidor/defesadoconsumidor/Biblioteca/editais/produto_2__cenario_do_superendividamento.pdf) | Secretaria Nacional do Consumidor (Senacon/MJSP) | 2021 | pdf |  | Diagnóstico técnico do superendividamento, perfis e causas. |

## Observações

- **Direitos autorais.** O projeto não redistribui os documentos: o script `baixar_fontes.py` baixa cada um da fonte oficial. Ao entregar o trabalho, envie o catálogo e o manifesto, e não a pasta `data/raw/`.
- **Cópias hospedadas.** Os módulos do curso *Gestão de Finanças Pessoais* (BCB/Sescoop) estão hospedados em um site do Exército Brasileiro. O conteúdo é do BCB e isso está registrado no campo `instituicao`.
- **URLs alternativas.** Fontes cujo site principal é instável têm `alternativas` no catálogo (ex.: a Lei Maria da Penha vem da Câmara, com o Planalto como reserva). O `manifesto.json` registra qual URL foi efetivamente usada.
- **Substituições feitas na curadoria.** A diretriz OCDE/G20 (o site bloqueia downloads automáticos, erro 403), o Plano Diretor da ENEF (o link devolvia uma página, não o PDF) e o relatório Sebrae 2019 (link removido) foram trocados por fontes equivalentes de domínios estáveis. É uma decisão de curadoria: uma fonte que não pode ser coletada de forma reprodutível enfraquece a rastreabilidade.
- **Links podem mudar.** Se uma URL deixar de funcionar, atualize o catálogo ou salve o arquivo manualmente em `data/raw/<id>.<formato>`. O `manifesto.json` registra a URL e a data efetivas de cada download.
- **Datas aproximadas.** Quando o documento não informa o ano com clareza, o ano no catálogo é o da publicação identificada na busca. Confira ao abrir o arquivo.
- **Para ampliar a base**, basta adicionar um item ao catálogo e rodar `baixar_fontes.py` e `ingerir.py`. Sugestões de próximas fontes: Tesouro Direto (guias), regras de aposentadoria da mulher no INSS, materiais do Ministério das Mulheres sobre autonomia econômica e o Relatório de Cidadania Financeira 2021 (série histórica).
