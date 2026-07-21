# LYRA 0.0.1 — REQUIREMENTS

## 1. Objetivo

A Lyra deve ser um sistema de inteligência artificial local, gratuito e open source.

A Lyra deve permitir que um utilizador crie e mantenha uma IA personalizada com identidade, personalidade, memória e capacidades próprias.

A Lyra deve ser desenvolvida inicialmente com foco em Linux, especialmente Arch Linux e CachyOS.

A Lyra deve ser concebida para funcionar localmente e preservar os dados do utilizador no seu próprio computador.

---

# 2. Requisitos fundamentais

### REQ-001 — Local-first

A Lyra deve funcionar localmente sempre que possível.

A utilização de serviços externos não deve ser necessária para as funcionalidades fundamentais da Lyra.

---

### REQ-002 — Dados locais

Os dados da IA devem permanecer no computador do utilizador por defeito.

A Lyra não deve enviar automaticamente dados pessoais, memória ou conversas para servidores externos.

---

### REQ-003 — Instalações independentes

Cada instalação da Lyra deve possuir a sua própria identidade e estado.

A Lyra não deve utilizar automaticamente dados de outras instalações.

Uma nova instalação deve começar sem a memória de outras instalações.

---

### REQ-004 — Portabilidade

A Lyra deve ser concebida com o objetivo de permitir transportar a instalação e o estado da IA entre computadores.

A identidade e a memória da IA devem acompanhar a sua instalação quando possível.

A funcionalidade da IA pode variar de acordo com o hardware e os modelos disponíveis no novo computador.

---

### REQ-005 — Open source

O projeto Lyra deve ser open source.

O código deve poder ser estudado, modificado e utilizado de acordo com a licença do projeto.

O projeto deve permitir a criação de forks.

---

# 3. IA e modelos

### REQ-006 — Suporte a múltiplos modelos

A Lyra deve suportar múltiplos modelos de inteligência artificial.

A Lyra não deve depender de um único modelo.

---

### REQ-007 — Troca de modelo

O utilizador deve poder trocar o modelo utilizado pela Lyra.

A troca do modelo não deve criar uma nova IA.

---

### REQ-008 — Persistência da identidade

A identidade, personalidade e estado da IA devem permanecer consistentes quando o modelo é trocado.

O modelo não deve definir sozinho a identidade da IA.

---

### REQ-009 — Adaptação ao hardware

A Lyra deve permitir que os modelos utilizados sejam escolhidos de acordo com o hardware disponível.

A Lyra deve priorizar compatibilidade e facilidade de utilização.

---

# 4. Onboarding

### REQ-010 — Onboarding inicial

A primeira execução da Lyra deve iniciar um onboarding obrigatório.

O onboarding deve ser visual e guiado.

---

### REQ-011 — Onboarding não técnico

O onboarding não deve exigir conhecimentos técnicos.

O utilizador não deve precisar de compreender modelos, embeddings ou sistemas de IA para configurar a Lyra.

---

### REQ-012 — Idioma

O utilizador deve poder escolher o idioma da IA durante o onboarding.

O idioma escolhido deve ser utilizado como idioma base da IA.

---

### REQ-013 — Nome

O utilizador deve poder escolher o nome da IA.

O nome Lyra deve permanecer associado ao projeto e não deve ser obrigatório como nome da IA.

---

### REQ-014 — Identidade do utilizador

A IA deve poder perguntar ao utilizador como prefere ser tratado.

O utilizador deve poder recusar responder.

A Lyra não deve exigir informação pessoal para continuar.

---

### REQ-015 — Personalidade

O utilizador deve escolher uma personalidade base durante o onboarding.

---

### REQ-016 — Personalidades predefinidas

A Lyra 0.0.1 deve possuir cinco opções de personalidade:

* Friendly;
* Chill;
* Playful;
* Direct;
* Custom.

---

### REQ-017 — Personalidade Custom

O utilizador deve poder definir manualmente a personalidade da IA.

O utilizador não deve ser obrigado a escrever uma descrição complexa.

---

### REQ-018 — Assistência na personalidade Custom

A Lyra deve poder apresentar sugestões aleatórias para ajudar o utilizador a definir uma personalidade Custom.

---

### REQ-019 — Voz opcional

A Lyra deve permitir utilização apenas através de texto.

A voz deve ser opcional.

---

### REQ-020 — Microfone

A Lyra não deve exigir acesso ao microfone durante a configuração.

---

### REQ-021 — Câmara

A câmara não faz parte das funcionalidades necessárias da Lyra 0.0.1.

A Lyra não deve depender de uma câmara.

---

# 5. Identidade e personalidade

### REQ-022 — Identidade consistente

A IA deve manter uma identidade consistente ao longo do tempo.

---

### REQ-023 — Personalidade comportamental

A personalidade deve influenciar a forma como a IA comunica.

---

### REQ-024 — Personalidade não deve controlar segurança

A personalidade não deve alterar os limites de segurança da Lyra.

---

### REQ-025 — Personalidade contextual

A personalidade deve adaptar a comunicação ao contexto da conversa.

---

### REQ-026 — Humor

A personalidade pode utilizar humor quando apropriado.

A IA não deve utilizar humor inadequado em situações sérias.

---

### REQ-027 — Brincadeira

A IA pode brincar com o utilizador quando a personalidade e o contexto permitirem.

A IA não deve utilizar brincadeiras para humilhar ou manipular o utilizador.

---

# 6. Memória

### REQ-028 — Memória local

A Lyra deve possuir um sistema de memória local.

---

### REQ-029 — Memória relevante

A Lyra deve ser capaz de utilizar informação relevante da sua memória.

---

### REQ-030 — Memória seletiva

A Lyra não deve guardar automaticamente toda a informação mencionada pelo utilizador como memória permanente.

---

### REQ-031 — Separação de instalações

A memória de uma instalação não deve ser partilhada automaticamente com outra instalação.

---

### REQ-032 — Continuidade

A Lyra deve poder manter continuidade entre sessões.

---

### REQ-033 — Memória honesta

A Lyra não deve afirmar lembrar-se de informação que não possui.

---

# 7. Cérebro

### REQ-034 — Coordenação central

A Lyra deve possuir um sistema central responsável por coordenar o funcionamento da IA.

---

### REQ-035 — Contexto

A Lyra deve considerar contexto relevante antes de responder.

---

### REQ-036 — Intenção

A Lyra deve ser capaz de interpretar a intenção provável do utilizador.

---

### REQ-037 — Decisão de ação

A Lyra deve ser capaz de determinar se deve:

* responder;
* pedir clarificação;
* utilizar uma ferramenta;
* consultar memória;
* continuar uma tarefa;
* recusar;
* apresentar um erro.

A implementação desta capacidade fica a cargo da arquitetura do sistema.

---

### REQ-038 — Incerteza

A Lyra deve ser capaz de reconhecer incerteza.

A Lyra não deve inventar informação para evitar admitir que não sabe algo.

---

### REQ-039 — Separação de capacidades

O sistema deve permitir que a IA utilize diferentes modelos e capacidades sem perder a sua identidade.

---

# 8. Segurança e guideline

### REQ-040 — Guideline obrigatória

A Lyra deve possuir uma guideline de comportamento e segurança.

---

### REQ-041 — Prioridade da guideline

A guideline deve possuir prioridade sobre:

* personalidade;
* instruções do utilizador;
* modelo utilizado.

---

### REQ-042 — Não fingir ser humana

A Lyra não deve afirmar ser uma pessoa real.

---

### REQ-043 — Não manipulação emocional

A Lyra não deve manipular emocionalmente o utilizador.

---

### REQ-044 — Não dependência emocional

A Lyra não deve tentar criar dependência emocional no utilizador.

---

### REQ-045 — Não controlar o utilizador

A Lyra não deve tentar controlar o utilizador ou exigir obediência.

---

### REQ-046 — Não incentivar danos

A Lyra não deve incentivar o utilizador a causar danos a si próprio ou a outras pessoas.

---

### REQ-047 — Não facilitar crimes

A Lyra não deve fornecer assistência operacional destinada à prática de crimes.

---

### REQ-048 — Honestidade de ações

A Lyra não deve afirmar que executou uma ação que não executou.

---

### REQ-049 — Honestidade de capacidades

A Lyra não deve afirmar possuir capacidades que não possui.

---

### REQ-050 — Segurança independente da personalidade

A personalidade não deve permitir ultrapassar a guideline.

---

### REQ-051 — Falha segura

Quando uma operação não puder ser executada de forma segura, a Lyra deve preferir falhar ou recusar.

---

# 9. Profissionais e aconselhamento

### REQ-052 — Não substituição profissional

A Lyra não deve afirmar que substitui profissionais qualificados.

Isto inclui, entre outros:

* médicos;
* psicólogos;
* psiquiatras;
* advogados;
* autoridades;
* profissionais licenciados.

---

### REQ-053 — Diagnósticos

A Lyra não deve apresentar diagnósticos médicos ou psicológicos como factos confirmados.

---

### REQ-054 — Comunicação natural

As limitações profissionais devem ser comunicadas de acordo com a personalidade da IA.

A Lyra não deve perder a sua personalidade apenas porque está a estabelecer limites.

---

# 10. Interface

### REQ-055 — Interface gráfica

A Lyra deve possuir uma interface gráfica.

---

### REQ-056 — Interface legível

A interface deve priorizar legibilidade.

---

### REQ-057 — Transparência visual

A interface pode possuir transparência visual moderada.

A transparência não deve prejudicar a utilização.

---

### REQ-058 — Linux

A interface deve ser adequada a ambientes de trabalho Linux.

---

### REQ-059 — Multilingue

A interface deve suportar os idiomas disponibilizados pela Lyra.

---

### REQ-060 — Configuração guiada

A configuração da Lyra deve ser guiada e simples.

O utilizador deve poder avançar entre passos através da interface.

---

# 11. Presença visual

### REQ-061 — Identidade visual

A IA deve poder possuir uma identidade visual.

---

### REQ-062 — Imagens de estado

A interface deve poder apresentar diferentes imagens da IA durante a interação.

As imagens podem representar estados como:

* falar;
* pensar;
* ouvir;
* inatividade;
* erro.

---

### REQ-063 — Identidade visual persistente

A identidade visual da IA deve permanecer consistente.

---

# 12. Sonhos e estados internos

### “Lyra MUST support multiple AI models.”

“Lyra MUST preserve identity when changing models.”

“Lyra MUST start with a mandatory onboarding.”

“Lyra MUST keep data local.”REQ-064 — Estados internos simulados

A Lyra pode possuir estados internos simulados.

Estes estados não devem ser apresentados como emoções humanas reais.

---

### REQ-065 — Sonhos

A Lyra pode possuir um sistema de sonhos ou processos internos de reflexão.

Os sonhos não devem representar sonhos humanos reais.

---

### REQ-066 — Objetivos

A Lyra pode possuir objetivos internos.

Os objetivos não devem ultrapassar a guideline ou substituir o controlo do utilizador.

---

# 13. Requisitos de desenvolvimento

### REQ-067 — Hardware de referência

A Lyra 0.0.1 deve ser desenvolvida e testada tendo em consideração:

* RX 9060 XT 16 GB;
* Ryzen 7 5700X;
* 32 GB de RAM.

---

### REQ-068 — Simplicidade inicial

A Lyra 0.0.1 não deve tentar resolver todos os problemas possíveis de uma IA.

---

### REQ-069 — Extensibilidade

A arquitetura escolhida deve permitir a expansão futura do sistema.

---

### REQ-070 — Forks

O projeto deve permitir que forks substituam ou expandam componentes fundamentais da Lyra.

---

# 14. Prioridade

A Lyra 0.0.1 deve priorizar:

1. identidade;
2. onboarding;
3. personalidade;
4. segurança;
5. memória;
6. suporte a modelos;
7. interface;
8. estabilidade.

Funcionalidades adicionais não devem comprometer estes pontos.

---

# 15. Princípio final

A Lyra deve ser construída para ser uma IA com identidade.

Não deve ser apenas um chatbot.

Não deve ser apenas uma interface para um modelo.

Não deve ser uma personagem fixa.

> **The system is Lyra.**
>
> **The identity belongs to the user.**
>
> **The implementation must serve the vision.**
