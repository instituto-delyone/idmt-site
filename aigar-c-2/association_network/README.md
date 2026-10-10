# AIGAR CORE — Fundação de reconstrução

Esta pasta é a camada de integração futura do AIGAR dentro de `aigar-c-2/`.

## Objetivo

Preservar a separação entre:

- **Linguagem materna** — leitura da entrada, intenção, escopo, profundidade e incerteza;
- **Memória** — continuidade e contexto;
- **Bibliotecas** — conhecimento documental;
- **CSI / roteamento** — preparação semântica e escolha de fontes/módulos;
- **Reasoning** — estruturação do raciocínio;
- **Diagnosis** — motor clínico especializado;
- **Aurora** — organização da experiência conversacional e modulação da resposta.

A regra arquitetural é:

```
ENTRADA
  ↓
LINGUAGEM MATERNA
  ↓
ESTADO DA CONVERSA
  ├── MEMÓRIA
  ├── BIBLIOTECA
  └── DIAGNOSIS
  ↓
RACIOCÍNIO
  ↓
PLANEJAMENTO / MODULAÇÃO
  ↓
AURORA
  ↓
RESPOSTA
```

## O que esta pasta não faz

Ela não substitui os motores históricos que já existem no repositório e não declara como fato aquilo que ainda não foi recuperado.

Em especial, ainda não está demonstrado:

- o algoritmo histórico exato da unidade mínima de fragmento;
- o algoritmo histórico exato de recombinação;
- uso histórico de embeddings ou vector DB;
- o conteúdo literal completo do antigo Grammar Card;
- o modelo local exato utilizado em cada versão.

Essas lacunas ficam registradas em `AIGAR_EVIDENCE_MAP_v1.md`.

## Fonte da verdade

Quando houver conflito entre uma cópia de integração e o artefato histórico, o artefato histórico deve ser preservado e a diferença deve ser documentada.

A integração moderna deve apontar para os artefatos existentes antes de criar duplicações desnecessárias.

## Ordem de reconstrução

1. Linguagem materna.
2. Estado/continuidade da conversa.
3. Recall e memória.
4. CSI / roteamento.
5. Biblioteca e recuperação.
6. Reasoning.
7. Adapter para Diagnosis.
8. Modulação Aurora.
9. Testes de integração.

## Princípio

**Não tentar transformar o Diagnosis em AIGAR. Colocar uma arquitetura AIGAR/Aurora ao redor do Diagnosis.**

O Diagnosis continua especializado; a camada conversacional organiza a interação.
