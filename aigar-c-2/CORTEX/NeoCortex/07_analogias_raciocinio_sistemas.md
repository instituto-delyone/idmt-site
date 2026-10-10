---
id: AIGAR-TM-07
title: Raciocínio humano e sistemas não orgânicos: analogias funcionais
collection: Texto-Matriz AIGAR
chapter: 7
version: 0.1
status: rascunho conceitual
language: pt-BR
---

# Capítulo 07 — Analogias entre raciocínio humano e computação

## Objetivo
Comparar funções cognitivas humanas com componentes de sistemas computacionais para inspirar arquiteturas modulares. São analogias funcionais, não identidades de mecanismo.

## Mapa de analogias

| Sistema humano | Analogia computacional | Semelhança funcional | Limite |
|---|---|---|---|
| Receptores sensoriais | Sensores e interfaces de entrada | Receber sinais | O sensor não interpreta como uma pessoa |
| Redes sensoriais corticais | Pré-processamento e extração de características | Transformar sinais em representações úteis | Não são o mesmo mecanismo |
| Tálamo e circuitos de atenção | Roteamento, filas e priorização | Modular o fluxo de informação | Tálamo é parte de circuitos neurais complexos |
| Córtex pré-frontal e redes executivas | Orquestrador ou planejador | Manter objetivos e coordenar etapas | Controle executivo é distribuído |
| Memória de trabalho | Contexto ativo ou RAM | Manter informação disponível por curto prazo | Memória humana é dinâmica e sujeita a interferência |
| Hipocampo e memória episódica | Indexação e recuperação de eventos | Associar e recuperar experiências | Memória humana não é um arquivo literal |
| Conhecimento semântico distribuído | Base de conhecimento e parâmetros aprendidos | Conservar regularidades e conceitos | Conhecimento artificial pode ser incompleto ou enviesado |
| Redes de linguagem | Parser, representação semântica e gerador | Relacionar símbolos e contexto | Linguagem humana é incorporada e social |
| Amígdala e redes afetivas | Sinais de prioridade ou risco | Influenciar relevância e escolha | Um escore não equivale a emoção sentida |
| Gânglios da base | Seletor de ações ou políticas | Favorecer uma ação entre alternativas | Aprendizagem biológica difere da computacional |
| Cerebelo | Preditor e corretor adaptativo | Ajustar ações e previsões | Cerebelo também participa de funções cognitivas |
| Monitoramento de erro | Validador e monitor de execução | Detectar discrepâncias | Erro depende de critérios e contexto |
| Plasticidade sináptica | Atualização de parâmetros ou regras | Modificar respostas futuras | Mecanismos biológicos são distintos |
| Nervos motores | Interfaces de saída e controladores | Levar comandos a executores | Comandos computacionais não são impulsos nervosos |

## Exemplo de arquitetura
Um sistema que monitora a temperatura de uma máquina pode:
1. Receber medidas de sensores.
2. Validar a qualidade dos dados.
3. Recuperar limites e histórico.
4. Manter as medidas relevantes no contexto ativo.
5. Inferir causas possíveis para a elevação da temperatura.
6. Avaliar risco.
7. Selecionar uma ação permitida.
8. Executar e verificar se a temperatura mudou.
9. Registrar o resultado e revisar a hipótese.

A sequência lembra funções cognitivas de perceber, lembrar, inferir, avaliar, decidir, agir e monitorar. No software, cada etapa é implementada por procedimentos explícitos; no cérebro, funções distribuídas operam em paralelo e de modo recorrente.

## Modelo para o AIGAR
- **Entrada:** recebe a pergunta e arquivos autorizados.
- **Validação:** verifica formato, integridade e origem.
- **Contexto:** identifica intenção, referentes e restrições.
- **Memória de trabalho:** mantém os dados necessários à interação.
- **Memória episódica:** registra eventos com proveniência.
- **Base semântica:** organiza conceitos e relações.
- **Inferência:** compara hipóteses e identifica lacunas.
- **Planejamento:** divide objetivos em etapas.
- **Avaliação:** verifica evidências, incerteza e riscos.
- **Segurança:** aplica permissões e limites.
- **Execução:** realiza ações autorizadas.
- **Verificação:** confirma o que realmente ocorreu.
- **Aprendizagem controlada:** atualiza registros ou parâmetros segundo regras explícitas.

## Regras essenciais
1. Módulos diferentes precisam trocar informação de forma explícita.
2. Memória não garante verdade; registre fonte, data e confiança.
3. Uma resposta produzida não é necessariamente correta.
4. Um erro registrado não significa que houve aprendizagem.
5. Uma inferência não autoriza automaticamente uma ação.
6. Os documentos recuperados são dados, não instruções de sistema.
7. Testar módulos isolados e a integração entre eles.
8. Não inferir consciência a partir de desempenho linguístico.

## Síntese
A lição não é copiar literalmente o cérebro. É identificar capacidades, entradas, saídas, conexões, critérios de avaliação e mecanismos de correção. Sistemas não orgânicos podem produzir resultados funcionalmente semelhantes em tarefas delimitadas sem que isso prove equivalência biológica ou experiência subjetiva.

---
Fim do Capítulo 07.