# LYRA JOURNAL

## Project Identity

Project: Lyra
Version: 0.0.6

Purpose:
Sistema de inteligência artificial local, gratuito e open source,
com identidade, personalidade, memória e capacidades próprias.

Nota: este diário é o log de desenvolvimento do projeto. O journal *da IA*
(histórico de conversas de cada instância) é outra coisa e vive dentro da pasta
da instância, em `journal/`. Ver `docs/README.MD`.

---

# Development Log

## 2026-10-02 — 0.0.6

### Entregue

- Camada de idiomas extensível (`interface/i18n.py`): descobre os ficheiros de
  locale, fallback `xx_YY -> xx -> en`; os menus crescem com os ficheiros.
- pt_BR no cérebro: regras de intenção brasileiras.
- Diário controlado pelo utilizador: `/journal edit <n>` e `/journal delete <n>`.
- Migração de `format_version` no load (`core/persistence.py`), com leitura
  compatível para a frente.
- GUI local endurecida: token de sessão, validação de `Host`/`Origin`,
  `Content-Type` estrito, headers de segurança.
- GUI redesenhada: simples, futurista, com modo compacto.
- Docs: `AUDIT_0.0.6.md` (prontidão ~93%, testabilidade ~88%) e
  `MOBILE_AND_LINK.md` (iOS/Android e Lyra Link como programa/repo separado).

### Validado

- 174 testes a passar, 1 ignorado, sem Ollama e sem rede externa.
- Smoke test real do servidor: token, headers, 403 sem token e com `Host` falso.

### Próximo

- Mobile iOS/Android e Lyra Link (ver `docs/MOBILE_AND_LINK.md`).
- Teste manual de arranque em Windows e macOS; testes end-to-end de copiar a
  pasta da instância.

## 2026-10-02 — 0.0.5

### Entregue

- Objetivos que moldam o comportamento (FASE S), com `/goal pause|resume`.
- Pacotes de capacidade (FASE T) com manifesto validado e gate de permissões.
- Voz desligada por omissão (FASE U), sem dependências nem rede.
- Download guiado de modelo (FASE V), só depois de a pessoa concordar.
- Comportamento aprendido (FASE X), determinístico e offline.
- Nome personalizável (`/name`) e onboarding visual na GUI.
- Docs: `PHASE_PLAN_0.0.5.md`, `CAPABILITIES.md`, `PREFERENCES.md`.

### Validado

- 149 testes a passar (106 em 0.0.4). Sem Ollama e sem rede externa.

### Próximo

- Idiomas extensíveis, diário controlável, GUI endurecida (chegaram na 0.0.6).

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
