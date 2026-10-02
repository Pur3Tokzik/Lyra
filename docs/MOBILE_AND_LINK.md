# Mobile (iOS e Android) e Lyra Link

Plano, não código. O núcleo da 0.0.6 fica exatamente como está; isto descreve o
que vem depois e porque a arquitetura já o permite.

## 1. Porque o mobile é possível sem reescrever o cérebro

O alinhamento diz duas coisas que tornam o mobile uma extensão e não um fork:

- A identidade pertence à instância e não ao modelo (AD-001). Trocar de modelo
  não cria outra IA.
- O LLM é uma capacidade, chamada só quando o cérebro decide gerar texto livre.

Num telefone, o cérebro, a guideline, a memória e o journal continuam locais e
determinísticos. O que muda é a capacidade do modelo: em vez de Ollama, usa-se um
modelo cloud (`cloud:...`), porque um telefone não corre um modelo local decente.
Como a escolha do modelo já vive em `settings/` e nunca toca em `identity/`,
`personality/` ou `memory/`, a mesma companheira atravessa telemóvel e computador.

## 2. O que viaja e o que não viaja

| Camada | No telefone | Nota |
| --- | --- | --- |
| Cérebro, guideline, intenção, decisão | Local | Mesmo código, corre em Python ou é portado |
| Identidade, personalidade, memória, journal, settings | Local, pasta da instância | Copiada ou sincronizada, nunca fundida entre pessoas |
| Modelo | Cloud, escolhido pelo utilizador | Só entra quando o cérebro decide; nunca sozinho |
| Voz, câmara | Capacidades opcionais | Voz já existe na CLI; a câmara continua fora |

## 3. Opções de implementação, por ordem de honestidade

1. **Cliente fino (recomendado para começar).** A app móvel fala com uma
   instância Lyra que corre no computador da pessoa, através do Lyra Link. A app
   não guarda o cérebro; é uma janela segura para a companheira que já existe.
   Menos código, uma só memória, zero sincronização de dados sensíveis.
2. **Instância móvel própria.** A pasta da instância é copiada para o telefone e
   o cérebro corre lá, com um modelo cloud. Dá independência do computador, mas
   cria duas cópias da memória e obriga a decidir conflitos.
3. **Núcleo portado para um runtime móvel.** O mesmo desenho de regras em Dart,
   Kotlin e Swift. Mais trabalho e três lugares para manter a guideline em dia.
   Só se justifica se o cliente fino se tornar limitador.

O caminho 1 primeiro, o 2 a seguir, o 3 só com razão forte.

## 4. iOS e Android: restrições reais

- Uma app iOS não pode abrir um servidor HTTP à escuta como o `gui.py` faz no
  computador. O cliente fino evita isto: é o telefone que liga ao computador.
- Sem rede, o cérebro local no telefone (opção 2) continua a responder a
  comandos, memória e identidade; só a conversa livre precisa de rede.
- Chaves de modelos cloud ficam no keychain do sistema, nunca em ficheiros da
  instância (a regra atual mantém-se: chaves vêm do ambiente, nunca para o disco).
- Permissões (voz, ficheiros) seguem o mesmo princípio dos pacotes de
  capacidade: explícitas e concedidas pela pessoa, nunca implícitas.

## 5. Lyra Link — programa separado, repositório separado

O Lyra Link não é uma capacidade do núcleo e não deve viver dentro dele. É um
programa à parte, com o seu próprio repositório, que liga dois computadores (e
mais tarde o telefone) para que a mesma companheira esteja acessível em vários
sítios.

Regras de desenho:

- **O núcleo não depende do Link.** Remover o Link deixa a Lyra a funcionar. Isto
  respeita a Regra 2.
- **A identidade viaja, o modelo não.** O Link transporta pedidos e respostas,
  não guarda a instância.
- **Cifrado ponta a ponta.** A ligação é entre máquinas da mesma pessoa, com um
  emparelhamento explícito (código ou chave), nunca aberta na rede local por
  omissão.
- **A guideline não se desliga no caminho.** O computador que responde continua a
  aplicar a guideline de entrada e de saída; o Link só transporta.
- **Sem nuvem da Lyra.** O Link liga máquinas, não passa por um serviço central.

### Fases propostas do Link

| Fase | Entregável | Critério |
| --- | --- | --- |
| L1 | Emparelhamento explícito entre dois computadores | Só o par combinado se liga; tudo o resto recusado |
| L2 | Transporte cifrado de um turno (pergunta e resposta) | A companheira responde de outra máquina; a guideline aplica-se lá |
| L3 | Cliente móvel fino sobre o Link | A app iOS/Android usa a instância do computador |
| L4 | Várias máquinas em simultâneo | Uma pessoa, uma companheira, várias janelas |

## 6. O que fica de fora por agora

- Correr o modelo local no telefone.
- Sincronizar memória entre instâncias diferentes (duas pessoas não partilham
  memória — REQ-003, REQ-031).
- Um serviço central da Lyra. Não existe e não é preciso.
