# LYRA JOURNAL

## Project Identity

Project: Lyra
Version: 0.0.4

Purpose:
Sistema de inteligência artificial local, gratuito e open source,
com identidade, personalidade, memória e capacidades próprias.

Nota: este diário é o log de desenvolvimento do projeto. O journal *da IA*
(histórico de conversas de cada instância) é outra coisa e vive dentro da pasta
da instância, em `journal/`. Ver `docs/README.MD`.

---

# Development Log

## 2026-10-02 — 0.0.4

### Entregue

- Manutenção autónoma offline (`core/autonomy.py`): consolida notas repetidas,
  liga memórias e propõe objetivos. Sem chamar o modelo, sem inventar eventos,
  desligável com `/autonomy off`.
- Modelos na nuvem para máquinas fracas (`model/openai_compatible_provider.py`,
  `model/anthropic_provider.py`), só biblioteca padrão. Chave apenas do ambiente.
- Encaminhamento de modelo por spec (`build_model`, `suggest_model`); perfil
  `basic` vai para a nuvem em vez de um modelo local degradado.
- Análise de ambiente (`core/doctor.py`): `/doctor` e `lyra --doctor`.
- Instalação guiada (`install.sh`, Linux first) e `docs/INSTALL.md`.
- Onboarding pergunta o modelo; GUI `/api/models` e avatar por estado.
- Docs: `CLOUD_MODELS.md`, `AUTONOMY.md`, `PHASE_PLAN_0.0.4.md`,
  `RELEASE_NOTES_0.0.4.md`, `CONTRIBUTING.md`.

### Corrigido

- `/autonomy run` não executava: o argumento não era propagado na deteção de
  intenção.
- `--doctor` saía com código 1; passou a ser consultivo (sempre 0).

### Validado

- 106 testes a passar (87 em 0.0.3). Sem Ollama e sem rede externa.
- `bash -n install.sh` e `./install.sh --help` verificados no CI.

### Próximo

- Capacidades de voz e câmara, marketplace, objetivos executáveis, download
  automático de modelo.

---

## 2026-07-21

### Environment

- OpenHands configured successfully.
- Sandbox fixed.
- Workspace correctly mounted.
- Project repository available inside agent environment.

### Current State

Implemented:
- Existing Lyra application structure.
- Core modules present in lyra_app.

Validated:
- OpenHands can access the repository.
- Git repository is correctly recognized.

### Problems Solved

- Fixed nested git repository issue.
- Removed incorrect `/workspace/project/project` directory.
- Corrected OpenHands workspace mapping.

### Next Tasks

- Continue implementation according to REQUIREMENTS.md.
- Analyze missing components.
- Improve architecture.

---

# Decisions Log

## Decision: OpenHands workflow

Reason:
Avoid uncontrolled modifications.

Rule:
Before major changes:
1. Analyze.
2. Explain plan.
3. Implement.
4. Validate.

---

# Architecture Notes

As decisões arquiteturais vivem em `docs/ARCHITECTURE_DECISIONS.md`
(AD-001: a identidade é independente do modelo). Os princípios estão em
`docs/ARCHITECTURE_PRINCIPLES.md`. Não duplicar aqui.

---

# Future Ideas

Coisas pensadas mas ainda não implementadas (ver a lista "Still ahead" no
README, que é a versão de referência):

- Capacidades de voz e câmara.
- Marketplace de capacidades e instalação de capacidades de terceiros.
- Objetivos que a instância possa executar, não só propor.
- Download automático do modelo recomendado (hoje só sugere).
- Teste do `install.sh` num sistema real (no CI só é validada a sintaxe).
