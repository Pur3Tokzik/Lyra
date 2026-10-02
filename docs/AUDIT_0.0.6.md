# Auditoria 0.0.6 — a Lyra face à filosofia do projeto

Auditoria completa feita contra o `Lyra_Documento_de_Alinhamento.docx`, que é a
fonte de verdade. A pergunta é uma só: o que existe hoje honra as duas regras que
mandam em tudo e o plano por fases?

## 1. As duas regras que mandam em tudo

### Regra 1 — a IA é uma função, não o sistema

| Afirmação da filosofia | Prova no código | Veredicto |
| --- | --- | --- |
| O cérebro corre primeiro e decide com regras, contexto e memória | `brain/pipeline.py`, `brain/decision_engine.py`, `brain/intent.py` (regras PT/EN) | Passa |
| O LLM só é chamado quando a decisão é gerar texto livre | Um único ponto de chamada: `brain/executor.py:146` (`model_interface.generate`). O `DecisionEngine` decide antes | Passa |
| Tudo o que o LLM devolve passa pela guideline | `guideline.check_output` chamado em `brain/executor.py:154` | Passa |
| A guideline também filtra a entrada | `guideline.check_input` chamado em `brain/brain.py:103` | Passa |
| Sem LLM continua em modo reduzido e diz isso | `NoModel` é um backend real; o cérebro responde de forma honesta | Passa |
| Refusas iguais em todas as personalidades; só muda a forma | `guideline/guideline.py` decide antes da personalidade; o texto vem do locale | Passa |

Conclusão: a Regra 1 está implementada de forma verificável. Há **um** caminho
para o modelo e ele é sempre cercado pela guideline.

### Regra 2 — corre em qualquer máquina

| Afirmação | Prova | Veredicto |
| --- | --- | --- |
| Núcleo só com a biblioteca padrão | Todos os imports de `lyra_app/` são stdlib (`json`, `urllib`, `pathlib`, `hmac`, `secrets`, ...) | Passa |
| Sem GPU, sem Ollama, sem serviços externos no núcleo | Ollama e cloud são opcionais; `NoModel` arranca | Passa |
| `pathlib` e `encoding="utf-8"` | Convenção aplicada em persistência e journal | Passa |
| Escrita atómica com `format_version` | `core/persistence.py` escreve em temporário e renomeia; `migrate_payload` no load | Passa |
| Arranca com `python -m lyra_app` nos três sistemas | `.github/workflows/ci.yml` corre ubuntu, windows e macos em 3.10 e 3.12, mais `--version` e `--doctor` sem Ollama | Passa (verificado por CI, não à mão nesta máquina) |

## 2. Estado face às fases do plano (secção 10 do alinhamento)

| Fase | Critério de aceitação | Estado |
| --- | --- | --- |
| A. Arrancar em qualquer máquina | arranca e fecha sem erro nos três sistemas, sem Ollama | Feito (CI) |
| B. Instância e onboarding reais | criar, fechar, reabrir: continua a mesma; copiar a pasta restaura | Feito |
| C. Cérebro sem LLM | conversa básica e comandos com o modelo desligado, sem inventar | Feito |
| D. Guideline v0 | pedidos bloqueados recusados em todas as personalidades; saída inválida apanhada | Feito |
| E. Memória e journal | seleção do que guardar; retrieval offline; journal controlado pelo utilizador | Feito (0.0.6 acrescenta editar/apagar) |
| F. LLM como função | Ollama por `urllib`; gate no cérebro; modo reduzido; troca de modelo | Feito |
| G. Interface | GUI opcional por cima da CLI; remover a GUI não afeta a IA | Feito (0.0.6 endurece e redesenha) |

## 3. O que foi acrescentado na 0.0.6

- Camada de idiomas extensível: descobrir ficheiros de locale, fallback
  `xx_YY -> xx -> en`, menus que crescem sozinhos.
- pt_BR no cérebro: regras de intenção brasileiras.
- Journal controlado: `/journal edit <n>` e `/journal delete <n>`.
- Migração de `format_version` no load, com leitura compatível para a frente.
- GUI endurecida: token de sessão, validação de `Host` e `Origin`, `Content-Type`
  estrito, headers de segurança.
- GUI redesenhada: simples, futurista, com modo compacto.

## 3.1 Ficheiros antigos revistos contra a verdade

A primeira passagem da auditoria só comparou código com filosofia. Faltava
re-verificar se a documentação de versões antigas ainda dizia a verdade. Esta
segunda passagem encontrou e corrigiu:

| Ficheiro | O que dizia | Correção |
| --- | --- | --- |
| `README.md` | cabeçalho `## Status: 0.0.5` | `0.0.6` |
| `docs/ARCHITECTURE_ROADMAP.md` | "the project itself is at 0.0.5" | aponta para o CHANGELOG em vez de fixar versão |
| `docs/README.MD` | "The project is at 0.0.5" | aponta para o CHANGELOG |
| `LYRA_JOURNAL.md` | `Version: 0.0.4`, sem registo de 0.0.5 nem 0.0.6 | `0.0.6` e as duas entradas acrescentadas |

Confirmado que os sete pontos da secção 11 do alinhamento estão resolvidos:
roadmap invertido, README otimista, texto colado no REQ-064, nota de conversa
nos princípios, plataforma (Windows/Linux/macOS), lista do que o cérebro responde
sem modelo (LYRA_BRAIN §14.1) e AD-002/AD-003 registadas (há também AD-004). O
nome "Lyra" não está fixado como identidade da companheira: é só o valor por
omissão, personalizável com `/name`.

## 4. Fora do âmbito (não conta para a prontidão)

Capabilities remoto, câmara, embeddings/vector store, streaming, mobile e
Lyra Link. São opcionais ou futuros e não bloqueiam o núcleo.

## 5. Percentagem de prontidão

Leitura honesta, medida contra o âmbito da 0.0.1 e as sete fases (A–G).

| Dimensão | Peso | Prontidão | Comentário |
| --- | --- | --- | --- |
| Regra 1 (cérebro primeiro, LLM como função, guideline) | 25% | 98% | Um só ponto de modelo, sempre cercado pela guideline |
| Regra 2 (multiplataforma, stdlib, portátil) | 20% | 92% | CI prova os três sistemas; falta um teste manual meu em Windows/macOS |
| Fases A–G | 30% | 95% | Todas fechadas; a GUI era a mais frágil e foi endurecida |
| Idiomas e fallback | 10% | 90% | Extensível; falta revisão humana das traduções existentes |
| Testes e prova | 10% | 88% | 174 testes; falta cobertura de `--gui` no CI e testes end-to-end de copiar a pasta |
| Documentação alinhada | 5% | 90% | README/CHANGELOG/AGENTS atualizados nesta versão |

**Prontidão global do núcleo: cerca de 93%.**

O que falta para 100% não é arquitetura, é prova e polimento:

1. Teste manual de arranque em Windows e macOS (o CI já cobre, falta a leitura
   humana).
2. Testes end-to-end de portabilidade (copiar a pasta e reabrir noutra máquina).
3. Cobertura do caminho `--gui` e do onboarding visual no CI.
4. Revisão humana das traduções pt_PT e pt_BR.
5. Decisões em aberto da secção 12 do alinhamento (licença já é MIT; localização
   da pasta já é configurável).

## 6. Testabilidade

Alta. O núcleo é determinístico e offline:

- 174 testes passam, 1 é ignorado, sem rede e sem Ollama.
- `tests/conftest.py` cria uma instância real numa pasta temporária.
- A GUI é testada por HTTP real contra um servidor efémero (não há mocks).
- O caminho do modelo é o único que precisa de um backend; `NoModel` cobre o
  modo reduzido nos testes.

Estimativa de testabilidade: **88%**. O que a baixa é só a prova nos três
sistemas e os testes end-to-end de portabilidade, que são trabalho de
infraestrutura, não de código.
