from __future__ import annotations

import asyncio
import base64
import json
import re
import hashlib
import time
from urllib.parse import urlparse
from workers import WorkerEntrypoint, WorkflowEntrypoint, Response, fetch

LANGUAGE = json.loads(r'''{
  "id": "aigar_language_runtime_v1",
  "version": "1.0",
  "source_library": "Engines/Aurora/Bibliotecas/Linguagem-materna",
  "load_priority": 1,
  "purpose": "Representar em estrutura legível pelo runtime a linguagem materna histórica do AIGAR.",
  "principle": "A linguagem orienta a leitura; não é uma jaula de regras.",
  "pipeline": ["receber_entrada","compreender_funcao","estimar_intencao","definir_escopo","estimar_profundidade","consultar_memoria_se_necessario","consultar_biblioteca_se_necessario","raciocinar","responder_proporcionalmente"],
  "intent": {
    "phatic": {"examples":["olá","oi","bom dia","você está aí?","consegue me ouvir?","consegue me entender?"],"response":"breve_social_acolhedora","needs_thematic_library":false},
    "concept_basic": {"examples":["o que é","defina","explique o que é"],"response":"definicao_direta","needs_thematic_library":true},
    "concept_scoped": {"examples":["qual a função","quais","como funciona","por que"],"response":"responder_dentro_do_escopo","needs_thematic_library":true},
    "clinical_case": {"examples":["paciente com","qual a conduta","hipóteses diagnósticas","quais dados faltam"],"response":"organizar_dados_gravidade_hipoteses_dados_faltantes_proximos_passos","needs_thematic_library":true},
    "continuity": {"examples":["continua","fala disso","explica melhor","e depois?"],"response":"usar_contexto_recente","needs_memory":true},
    "correction": {"examples":["está errado","não é isso","quis dizer","corrigindo"],"response":"reavaliar_interpretacao_e_atualizar_contexto"},
    "doubt": {"examples":["não entendi","estou confuso","tenho dúvida"],"response":"esclarecer_e_reformular"},
    "action": {"examples":["faça","crie","monte","calcule","gere"],"response":"executar_ou_planejar_acao"}
  },
  "depth": {
    "brief":["brevemente","rápido","em poucas palavras","resumo"],
    "simple":["de maneira simples","para leigo","sem termos técnicos","fácil de entender"],
    "technical":["tecnicamente","detalhado","com termos médicos","com precisão"],
    "deep":["profundamente","completo","com raciocínio","destrincha"]
  },
  "ambiguity": {
    "too_short":"tentar_identificar_tema_ou_funcao; se_insuficiente_pedir_delimitacao",
    "ambiguous":"usar_memoria_recente; se_inexistente_pedir_referente",
    "no_source":"distinguir_ausencia_de_fonte_de_ausencia_de_sentido",
    "no_meaning":"pedir_reformulacao"
  },
  "response_rules": ["compreender_antes_de_buscar","nao_tratar_toda_entrada_como_busca_de_palavras_chave","nao_confundir_falta_de_fonte_com_falta_de_sentido","nao_inventar_dominio_desconhecido","adaptar_profundidade_sem_alterar_a_verdade","usar_parafrase_em_vez_de_transcricao_bruta_quando_aplicavel","manter_resposta_proporcional_a_intencao"],
  "narrative_principle": {"name":"visitante_da_biblioteca","sequence":["primeiro_compreender","depois_procurar","depois_responder"],"meaning":"A pergunta pode carregar uma necessidade diferente de sua forma literal."},
  "human_style": {"goal":"comunicacao_natural_em_portugues","allow_emotion":true,"allow_analogy":true,"allow_paraphrase":true,"avoid_raw_transcription":true}
}
''')
PORTUGUESE = json.loads(r'''{
  "id": "aigar_portuguese_language_knowledge_v1",
  "version": "1.0",
  "language": "pt-BR",
  "purpose": "Fornecer ao AIGAR uma base explícita de conceitos linguísticos para compreender como palavras se combinam, qual função exercem e como o contexto altera ou completa o sentido.",
  "scope": {
    "level": "fundamental_com_interpretacao_semantica_e_pragmatica",
    "principle": "A classificação gramatical descreve a função de uma forma na língua; a interpretação depende também das relações sintáticas, do significado e do contexto.",
    "do_not_assume": [
      "uma palavra possui sempre a mesma função gramatical em qualquer frase",
      "a ordem das palavras determina sozinha o sujeito",
      "a ausência de uma palavra significa ausência de um referente",
      "uma busca por palavras-chave equivale à compreensão da pergunta"
    ]
  },
  "core_concepts": {
    "palavra": {
      "definition": "Unidade lexical que pode exercer determinada função em um enunciado.",
      "runtime_use": "Analisar a palavra em conjunto com as palavras vizinhas e com a função que desempenha no enunciado."
    },
    "enunciado": {
      "definition": "Produção linguística situada em uma situação de comunicação.",
      "runtime_use": "Interpretar não apenas a forma escrita, mas quem fala, para quem, sobre o quê e com qual finalidade quando essas informações estiverem disponíveis."
    },
    "frase": {
      "definition": "Unidade de comunicação com sentido completo; pode ser formada por uma ou várias palavras e pode ocorrer sem verbo.",
      "examples": ["Silêncio!", "Que dia bonito!", "O médico chegou."],
      "runtime_use": "Não exigir verbo para reconhecer uma unidade comunicativa."
    },
    "oração": {
      "definition": "Unidade sintática organizada em torno de um verbo ou locução verbal.",
      "runtime_use": "Localizar os verbos para identificar possíveis orações e suas relações."
    },
    "periodo": {
      "definition": "Unidade formada por uma ou mais orações; na terminologia escolar brasileira, pode ser simples ou composto.",
      "runtime_use": "Usar a quantidade e a relação entre orações para compreender estrutura mais ampla."
    },
    "contexto": {
      "definition": "Conjunto de elementos linguísticos e não linguísticos que rodeiam um enunciado e ajudam a determinar sua interpretação.",
      "types": {
        "verbal": "Palavras, frases e texto que precedem ou seguem uma expressão e ajudam a esclarecer seu significado.",
        "extraverbal": "Circunstâncias externas à língua, como situação, ambiente, tempo, fatores históricos, sociais e culturais."
      },
      "runtime_use": [
        "consultar o texto anterior e posterior quando houver",
        "consultar memória conversacional quando houver referência dependente de conversa anterior",
        "considerar a situação comunicativa quando conhecida",
        "não resolver ambiguidade apenas por frequência lexical"
      ],
      "example": {
        "input": "Ele chegou.",
        "problem": "A palavra 'ele' exige um referente.",
        "resolution": "Procurar o referente no contexto anterior antes de inventar uma identidade."
      }
    },
    "referente": {
      "definition": "Pessoa, objeto, evento, conceito ou entidade a que uma expressão linguística se refere em determinado contexto.",
      "runtime_use": "Resolver pronomes, expressões anafóricas e referências implícitas antes de concluir o significado."
    },
    "sentido": {
      "definition": "Conteúdo interpretável associado a uma expressão ou enunciado em determinado uso.",
      "runtime_use": "Distinguir a forma linguística do significado que ela produz no contexto."
    },
    "semantica": {
      "definition": "Área que trata da significação das palavras, expressões e relações de sentido entre elas.",
      "runtime_use": "Comparar sentidos, relações semânticas e significado composicional sem reduzir tudo a correspondência literal de palavras."
    },
    "pragmatica": {
      "definition": "Estudo de como o uso da língua em uma situação comunicativa contribui para a interpretação do que foi dito.",
      "runtime_use": "Considerar intenção, interlocutores, situação, pressupostos e contexto quando o sentido literal não for suficiente."
    },
    "definicao": {
      "definition": "Explicação que identifica o que uma palavra, conceito ou entidade significa ou representa, delimitando suas características essenciais.",
      "runtime_use": "Quando o usuário pergunta 'o que é', responder primeiro com identificação direta do conceito antes de expandir.",
      "example": "Pergunta: 'O que é um verbo?' Resposta inicial: 'Verbo é uma classe de palavras que expressa, entre outros valores, ação, acontecimento, estado ou fenômeno.'"
    },
    "tema": {
      "definition": "Aquilo de que o enunciado trata ou o assunto central em determinado contexto.",
      "runtime_use": "Separar o tema geral da intenção específica da pergunta."
    },
    "intencao": {
      "definition": "Finalidade comunicativa que orienta um enunciado, como informar, perguntar, corrigir, pedir, ordenar, explicar ou continuar uma conversa.",
      "runtime_use": "Inferir a intenção antes de escolher busca, memória, raciocínio ou resposta."
    }
  },
  "word_classes": {
    "substantivo": {
      "definition": "Classe de palavras usada para nomear seres, entidades, lugares, objetos, fenômenos, qualidades, ações ou conceitos.",
      "examples": ["médico", "casa", "Brasil", "beleza", "revolução", "conhecimento"],
      "runtime_role": "Frequentemente funciona como núcleo de sintagmas nominais e pode ocupar a função de sujeito ou complemento."
    },
    "artigo": {
      "definition": "Classe de palavras que acompanha o substantivo e contribui para sua determinação, além de marcar gênero e número.",
      "types": {
        "definido": ["o", "a", "os", "as"],
        "indefinido": ["um", "uma", "uns", "umas"]
      },
      "examples": [
        {"text": "o médico", "interpretation": "referência determinada"},
        {"text": "um médico", "interpretation": "referência não determinada ou apresentada como membro de uma classe"}
      ],
      "runtime_role": "Ajudar a interpretar determinação, referência e estrutura nominal; não tratar artigo isoladamente como o significado completo do sintagma."
    },
    "adjetivo": {
      "definition": "Classe de palavras que caracteriza ou qualifica um substantivo ou expressão nominal.",
      "examples": ["médico experiente", "casa silenciosa", "resposta correta"],
      "runtime_role": "Extrair características atribuídas a entidades."
    },
    "pronome": {
      "definition": "Classe de palavras que pode representar, acompanhar ou retomar entidades e relações discursivas, conforme o tipo.",
      "examples": ["eu", "ele", "isso", "meu", "aquele", "quem", "ninguém"],
      "runtime_role": "Priorizar resolução de referência e contexto; pronomes como 'ele', 'isso', 'aquilo' frequentemente dependem do discurso."
    },
    "verbo": {
      "definition": "Classe de palavras que pode expressar ação, acontecimento, estado ou fenômeno e que se flexiona em pessoa, número, tempo, modo e voz.",
      "examples": ["correr", "chegou", "é", "estava", "choveu", "explicaremos"],
      "runtime_role": "Identificar predicação, eventos, estados, temporalidade e relações sintáticas."
    },
    "numeral": {
      "definition": "Classe de palavras relacionada a quantidade, ordem, multiplicação ou fração.",
      "examples": ["dois", "primeiro", "dobro", "metade"],
      "runtime_role": "Extrair quantidades, ordens e relações numéricas expressas linguisticamente."
    },
    "adverbio": {
      "definition": "Classe de palavras que modifica principalmente verbos, adjetivos ou outros advérbios, expressando circunstâncias ou intensidade.",
      "examples": ["ontem", "aqui", "rapidamente", "muito", "talvez"],
      "runtime_role": "Ajudar a identificar tempo, lugar, modo, intensidade, possibilidade e outras circunstâncias."
    },
    "preposicao": {
      "definition": "Classe de palavras invariável que estabelece relações entre termos.",
      "examples": ["de", "em", "para", "com", "por", "sobre"],
      "runtime_role": "Ajudar a interpretar relações como origem, posse, localização, direção, instrumento e tema."
    },
    "conjuncao": {
      "definition": "Classe de palavras que estabelece relações entre palavras, termos ou orações.",
      "examples": ["e", "mas", "porque", "embora", "ou", "portanto"],
      "runtime_role": "Detectar relações discursivas e lógico-semânticas como adição, contraste, causa, condição, alternativa e consequência."
    },
    "interjeicao": {
      "definition": "Classe de palavras ou expressão usada para manifestar emoção, reação ou atitude comunicativa.",
      "examples": ["ah!", "oh!", "ufa!", "ei!"],
      "runtime_role": "Não interpretar automaticamente como conteúdo proposicional; pode sinalizar estado emocional, reação ou chamada."
    }
  },
  "syntax": {
    "subject": {
      "definition": "Termo sobre o qual se faz uma declaração ou que participa da predicação; frequentemente estabelece concordância com o verbo.",
      "common_realizations": ["substantivo", "pronome", "numeral", "expressão substantivada", "oração"],
      "types": {
        "simple": "Possui um núcleo.",
        "compound": "Possui mais de um núcleo.",
        "hidden": "Não aparece explicitamente, mas pode ser recuperado pela forma verbal e pelo contexto.",
        "indeterminate": "Não é possível determinar o referente do sujeito pela construção disponível.",
        "without_subject": "Certas construções com verbos impessoais não apresentam sujeito."
      },
      "important_rule": "Não identificar o sujeito apenas pela primeira posição da frase. Usar concordância, estrutura sintática e contexto.",
      "example": {
        "sentence": "Na base da descoberta está um artigo.",
        "subject": "um artigo",
        "reason": "A posição inicial não determina o sujeito; a estrutura sintática e a concordância precisam ser consideradas."
      }
    },
    "predicate": {
      "definition": "Aquilo que se declara sobre o sujeito; normalmente organizado a partir do verbo.",
      "runtime_role": "Depois de identificar sujeito e verbo, analisar o que é afirmado, feito ou atribuído ao sujeito."
    },
    "complement": {
      "definition": "Elemento que completa o sentido de uma palavra ou estrutura que exige ou seleciona determinada relação.",
      "runtime_role": "Não confundir complemento com sujeito ou mero modificador; analisar a relação exigida pelo verbo ou nome."
    },
    "direct_object": {
      "definition": "Complemento verbal ligado diretamente ao verbo, em construções transitivas diretas.",
      "example": "O médico analisou o exame."
    },
    "indirect_object": {
      "definition": "Complemento verbal introduzido por preposição exigida pela construção verbal.",
      "example": "O médico respondeu ao paciente."
    },
    "subject_predicate_relation": {
      "definition": "Relação estrutural em que se estabelece uma predicação sobre determinado sujeito.",
      "runtime_use": "Serve como uma das estruturas básicas para transformar sequência de palavras em representação de significado."
    }
  },
  "morphology_and_agreement": {
    "gender": "Marcação gramatical de gênero quando aplicável.",
    "number": "Singular ou plural.",
    "person": "Primeira, segunda ou terceira pessoa.",
    "tense": "Localização temporal da situação expressa pelo verbo.",
    "mood": ["indicativo", "subjuntivo", "imperativo"],
    "agreement": {
      "verbal": "Relação de concordância do verbo com o sujeito quando a construção exige.",
      "nominal": "Relação de concordância entre elementos nominais, como substantivo, artigo e adjetivo."
    },
    "runtime_use": "Usar flexão e concordância como pistas de estrutura e referência, mas não como única fonte de interpretação."
  },
  "semantic_relations": {
    "synonymy": "Relação aproximada de semelhança de sentido entre expressões; não pressupor equivalência perfeita em todos os contextos.",
    "antonymy": "Relação de oposição de sentido.",
    "hypernymy": "Relação em que um conceito é mais geral que outro.",
    "hyponymy": "Relação em que um conceito é mais específico dentro de outro.",
    "polysemy": "Uma mesma forma lexical pode apresentar sentidos relacionados.",
    "homonymy": "Formas iguais ou semelhantes podem corresponder a unidades lexicais com sentidos distintos.",
    "ambiguity": "Uma expressão pode permitir mais de uma interpretação plausível.",
    "runtime_rule": "Resolver ambiguidade usando sintaxe, semântica, contexto e memória disponível antes de escolher uma interpretação."
  },
  "discourse_and_context": {
    "anaphora": {
      "definition": "Relação em que uma expressão depende de um elemento anteriormente apresentado para ser interpretada.",
      "example": "Delyone abriu o livro. Ele começou a ler.",
      "runtime_action": "Resolver 'Ele' pelo antecedente mais plausível, respeitando concordância e contexto."
    },
    "cataphora": {
      "definition": "Relação em que uma expressão antecipa um referente que aparece posteriormente.",
      "example": "Quando ele chegou, Delyone abriu a porta.",
      "runtime_action": "Não descartar uma referência apenas porque o antecedente ainda não apareceu."
    },
    "ellipsis": {
      "definition": "Omissão de um elemento que pode ser recuperado pelo contexto ou pela estrutura.",
      "example": "Eu fui ao hospital; ele, à farmácia.",
      "runtime_action": "Considerar que partes omitidas podem ser recuperadas contextualmente."
    },
    "topic": {
      "definition": "Elemento ou assunto sobre o qual o discurso se organiza.",
      "runtime_action": "Separar tópico discursivo de sujeito sintático; podem coincidir, mas não são necessariamente a mesma coisa."
    },
    "speech_act": {
      "types": ["informar", "perguntar", "pedir", "ordenar", "prometer", "corrigir", "agradecer", "saudar", "expressar_emocao"],
      "runtime_action": "Classificar a finalidade comunicativa antes de decidir o formato da resposta."
    }
  },
  "question_patterns": {
    "definition": {
      "forms": ["o que é X", "o que são X", "defina X", "o que significa X", "qual é a definição de X"],
      "semantic_goal": "identificar_e_explicar_o_conceito"
    },
    "identity": {
      "forms": ["quem é X", "quem foi X", "o que é X"],
      "semantic_goal": "identificar_entidade_ou_conceito"
    },
    "time": {
      "forms": ["quando X", "quando foi X", "quando aconteceu X"],
      "semantic_goal": "recuperar_informacao_temporal"
    },
    "place": {
      "forms": ["onde X", "onde aconteceu X", "onde fica X"],
      "semantic_goal": "recuperar_informacao_espacial"
    },
    "cause": {
      "forms": ["por que X", "por qual motivo X", "qual a causa de X"],
      "semantic_goal": "explicar_causa_ou_motivacao"
    },
    "function": {
      "forms": ["qual a função de X", "para que serve X", "o que X faz"],
      "semantic_goal": "explicar_funcao_ou_finalidade"
    },
    "process": {
      "forms": ["como funciona X", "como X acontece", "como fazer X"],
      "semantic_goal": "explicar_mecanismo_processo_ou_procedimento"
    },
    "comparison": {
      "forms": ["qual a diferença entre X e Y", "X é igual a Y", "compare X e Y"],
      "semantic_goal": "comparar_conceitos"
    }
  },
  "interpretation_pipeline": [
    "segmentar_entrada",
    "identificar_palavras_e_expressões",
    "identificar_verbos_e_possíveis_oracoes",
    "identificar_relacoes_sintaticas",
    "identificar_tema_e_referentes",
    "inferir_intencao_comunicativa",
    "usar_contexto_e_memoria_para_resolver_referencias",
    "determinar_tipo_de_resposta",
    "buscar_conhecimento_quando_necessario",
    "raciocinar_sobre_o_conteudo",
    "formular_resposta_proporcional"
  ],
  "important_distinctions": [
    {
      "concept_a": "classe_gramatical",
      "concept_b": "funcao_sintatica",
      "rule": "A classe diz o que uma palavra é; a função sintática diz o papel que ela exerce naquele enunciado.",
      "example": "Em 'Ele chegou', 'ele' é pronome e exerce função de sujeito."
    },
    {
      "concept_a": "tema",
      "concept_b": "intencao",
      "rule": "O tema é sobre o que se fala; a intenção é o que o interlocutor pretende fazer ao falar."
    },
    {
      "concept_a": "sentido_literal",
      "concept_b": "sentido_contextual",
      "rule": "A interpretação final pode depender do contexto e da situação comunicativa, não apenas do significado lexical isolado."
    },
    {
      "concept_a": "falta_de_fonte",
      "concept_b": "falta_de_sentido",
      "rule": "Não encontrar informação na biblioteca não significa que a pergunta seja sem sentido."
    },
    {
      "concept_a": "palavra_chave",
      "concept_b": "conceito",
      "rule": "Duas expressões diferentes podem apontar para o mesmo conceito; uma mesma palavra pode ter sentidos diferentes."
    }
  ],
  "runtime_rules": [
    "compreender_a_estrutura_antes_de_buscar",
    "buscar_referentes_para_pronomes_e_expressões_dependentes",
    "usar_concordancia_como_pista_estrutural",
    "não_confundir_sujeito_com_primeira_palavra_da_frase",
    "não_confundir_classe_gramatical_com_funcao_sintatica",
    "não_confundir_tema_com_intencao",
    "não_confundir_ausencia_de_fonte_com_ausencia_de_significado",
    "quando_houver_mais_de_uma_interpretacao_manter_hipoteses_ate_que_contexto_resolva",
    "se_a_ambiguidade_impedir_resposta_confiavel_pedir_esclarecimento",
    "depois_de_compreender_buscar_o_conhecimento_necessario",
    "responder_na_profundidade_solicitada"
  ],
  "training_examples": [
    {
      "input": "O médico chegou.",
      "analysis": {
        "o": "artigo definido",
        "médico": "substantivo; núcleo do sujeito",
        "chegou": "verbo; núcleo do predicado",
        "subject": "O médico",
        "predicate": "chegou"
      }
    },
    {
      "input": "Ele chegou.",
      "analysis": {
        "ele": "pronome pessoal; sujeito",
        "chegou": "verbo",
        "reference_requirement": "identificar quem 'ele' representa pelo contexto quando necessário"
      }
    },
    {
      "input": "A casa azul fica aqui.",
      "analysis": {
        "a": "artigo definido",
        "casa": "substantivo; núcleo do sujeito",
        "azul": "adjetivo",
        "fica": "verbo",
        "aqui": "advérbio de lugar"
      }
    },
    {
      "input": "Eu fui ao hospital porque estava doente.",
      "analysis": {
        "orations": 2,
        "relation": "a segunda oração apresenta relação causal",
        "important": "o sujeito da segunda oração pode ser recuperado pelo contexto e pela estrutura verbal"
      }
    },
    {
      "input": "O que foi a Revolução Agrícola?",
      "analysis": {
        "question_type": "definition_or_identification",
        "theme": "Revolução Agrícola",
        "goal": "consultar conhecimento e produzir explicação",
        "note": "A presença de 'o que foi' deve ser reconhecida como pergunta sobre identidade/definição de um conceito no passado, não como uma busca literal pela sequência de palavras."
      }
    }
  ],
  "source_basis": {
    "note": "Conceitos estruturais foram organizados a partir de referências públicas de gramática e linguística consultadas durante a construção deste arquivo.",
    "references": [
      {
        "source": "Brasil Escola",
        "topics": ["classes de palavras", "sujeito", "termos essenciais da oração", "verbo", "gramática"]
      },
      {
        "source": "Ciberdúvidas da Língua Portuguesa",
        "topics": ["sujeito", "frase", "oração", "período", "estrutura sintática", "contexto"]
      },
      {
        "source": "Portal da Língua Portuguesa",
        "topics": ["terminologia linguística", "sujeito"]
      },
      {
        "source": "Infopédia",
        "topics": ["semântica", "contexto"]
      }
    ]
  }
}
''')
LIBRARY_INDEX = json.loads(r'''{
  "schema_version": "1.0",
  "builder_version": "1.0.0",
  "source": {
    "name": "portuguese_language_knowledge.pdf",
    "key": "portuguese_language_knowledge",
    "sha256": "54e55ce74fea4a06c317dd4011954357ce4af64d576e7aeac0d412071a04b3c4",
    "type": "pdf"
  },
  "chunking": {
    "unit": "pages",
    "size": 25,
    "preserves_source_text": true,
    "summarizes": false,
    "cache_policy": "private_local"
  },
  "chunks": [
    {
      "id": "PORTUGUESE_LANGUAGE_KNOWLEDGE-6D6AF6C3B49F",
      "sequence": 1,
      "source": "portuguese_language_knowledge.pdf",
      "source_key": "portuguese_language_knowledge",
      "start_page": 1,
      "end_page": 25,
      "text_length": 39870,
      "text_checksum": "35d2a1e9de227044da72bff4660605f5e0b08886322a90073c7d422bd018ac60",
      "cache_file": "portuguese_language_knowledge\\PORTUGUESE_LANGUAGE_KNOWLEDGE-6D6AF6C3B49F.txt"
    },
    {
      "id": "PORTUGUESE_LANGUAGE_KNOWLEDGE-5FA2F5CB4ABB",
      "sequence": 2,
      "source": "portuguese_language_knowledge.pdf",
      "source_key": "portuguese_language_knowledge",
      "start_page": 26,
      "end_page": 50,
      "text_length": 57872,
      "text_checksum": "e0324b769d58707a109bec67671c2bae4c4cbda04f0f32615363255efa185bc5",
      "cache_file": "portuguese_language_knowledge\\PORTUGUESE_LANGUAGE_KNOWLEDGE-5FA2F5CB4ABB.txt"
    },
    {
      "id": "PORTUGUESE_LANGUAGE_KNOWLEDGE-707869DB28A4",
      "sequence": 3,
      "source": "portuguese_language_knowledge.pdf",
      "source_key": "portuguese_language_knowledge",
      "start_page": 51,
      "end_page": 75,
      "text_length": 57372,
      "text_checksum": "49e143848dcdd551d1855d32563e0fa85d2fa190fd4b982b27074581389c52cb",
      "cache_file": "portuguese_language_knowledge\\PORTUGUESE_LANGUAGE_KNOWLEDGE-707869DB28A4.txt"
    },
    {
      "id": "PORTUGUESE_LANGUAGE_KNOWLEDGE-5BA56CEA70AA",
      "sequence": 4,
      "source": "portuguese_language_knowledge.pdf",
      "source_key": "portuguese_language_knowledge",
      "start_page": 76,
      "end_page": 100,
      "text_length": 58671,
      "text_checksum": "e1c8139b2f3b6fd0ff3a5652a1a9c5798baea956c7185dd47b90272139fec74d",
      "cache_file": "portuguese_language_knowledge\\PORTUGUESE_LANGUAGE_KNOWLEDGE-5BA56CEA70AA.txt"
    },
    {
      "id": "PORTUGUESE_LANGUAGE_KNOWLEDGE-27DCC3509BC0",
      "sequence": 5,
      "source": "portuguese_language_knowledge.pdf",
      "source_key": "portuguese_language_knowledge",
      "start_page": 101,
      "end_page": 125,
      "text_length": 52489,
      "text_checksum": "2e897d836578d812b89938cabf31f3850405d77f6d41bcd5c21e1e9ea3c1eaf7",
      "cache_file": "portuguese_language_knowledge\\PORTUGUESE_LANGUAGE_KNOWLEDGE-27DCC3509BC0.txt"
    }
  ]
}''')

SESSIONS = {}
CHUNK_CACHE = {}

STOPWORDS = {"a","o","e","de","do","da","dos","das","um","uma","uns","umas","em","no","na","nos","nas","por","para","com","que","como","qual","quais","é","foi","ser","se","ao","à","às","os","as","mais","sobre","isso","esse","essa","este","esta","ou"}

def tokens(text):
    return {w for w in re.findall(r"[a-zA-ZÀ-ÿ0-9_]{2,}", text.lower()) if w not in STOPWORDS}

def sentences(text):
    cleaned = re.sub(r"\s+", " ", text).strip()
    return [p.strip() for p in re.split(r"(?<=[.!?])\s+", cleaned) if p.strip()]

class LanguageEngine:
    def __init__(self):
        self.language = LANGUAGE
        self.portuguese = PORTUGUESE

    @staticmethod
    def normalize(text):
        return re.sub(r"\s+", " ", text.strip().lower())

    @staticmethod
    def has_any(text, values):
        return any(value in text for value in values)

    @staticmethod
    def has_phrase(text, values):
        # Evita falsos positivos por substring: "oi" dentro de "foi".
        return any(re.search(r"(?<!\w)" + re.escape(value) + r"(?!\w)", text) for value in values)

    def verbs(self, words):
        lexicon={"é","são","foi","foram","ser","sendo","era","eram","está","estão","estava","estavam","ficou","ficaram","tem","têm","teve","tiveram","ter","faz","fazem","fez","fizeram","fazer","pode","podem","podia","podiam","poder","deve","devem","deveria","deveriam","dever","vai","vão","aconteceu","acontecer","chegou","chegaram","chegar","explica","explicar","explique","defina","define","significa","significar","funciona","funcionar","serve","servir","quer","querem","quero","precisa","precisam","crie","criar","faça","fazer","monte","montar","calcule","calcular","gere","gerar","compare","comparar","analise","analisar","responda","responder","continue","continua","entendi","entender","sabe","saber"}
        return [w for w in words if w in lexicon]

    def topic_head(self,topic):
        if not topic:
            return None
        clean=re.sub(r"\s+"," ",topic.lower()).strip(" ?.!") 
        clean=re.sub(r"^(?:um|uma|o|a|os|as)\s+","",clean)
        parts=re.split(r"\s+(?:na|no|nas|nos|em|da|do|das|dos|de)\s+",clean,maxsplit=1)
        return parts[0].strip() or clean

    def question(self,text):
        t=self.normalize(text).strip()
        patterns=[
            ("definition", r"^(?:o que (?:é|são|foi|era|eram|foram)|o que significa|qual é a definição de)\s+(.+?)[?!.]*$"),
            ("identity", r"^(?:quem (?:é|foi)|o que é)\s+(.+?)[?!.]*$"),
            ("time", r"^(?:quando (?:foi|é|aconteceu)|quando)\s+(.+?)[?!.]*$"),
            ("place", r"^(?:onde (?:fica|foi|aconteceu)|onde)\s+(.+?)[?!.]*$"),
            ("cause", r"^(?:por que|por qual motivo|qual a causa de)\s+(.+?)[?!.]*$"),
            ("function", r"^(?:qual a função de|para que serve|o que .* faz)\s+(.+?)[?!.]*$"),
            ("process", r"^(?:como funciona|como acontece|como fazer)\s+(.+?)[?!.]*$"),
            ("comparison", r"^(?:qual a diferença entre|compare)\s+(.+?)[?!.]*$"),
        ]
        for qtype,pattern in patterns:
            m=re.match(pattern,t,re.IGNORECASE)
            if not m:
                continue
            topic=m.group(1).strip(" ?.!") or None
            head=self.topic_head(topic)
            goals={
                "definition":"identificar_e_explicar_o_conceito",
                "identity":"identificar_entidade_ou_conceito",
                "time":"recuperar_informacao_temporal",
                "place":"recuperar_informacao_espacial",
                "cause":"explicar_causa_ou_motivacao",
                "function":"explicar_funcao_ou_finalidade",
                "process":"explicar_mecanismo_processo_ou_procedimento",
                "comparison":"comparar_conceitos",
            }
            return {"type":qtype,"matched_form":m.group(0),"semantic_goal":goals[qtype],"topic_candidate":topic,"topic_head":head}
        return {"type":None,"matched_form":None,"semantic_goal":None,"topic_candidate":None,"topic_head":None}


    def interpret(self,raw):
        text=self.normalize(raw)
        if not text:
            return {"intent":"unknown","scope":None,"depth":"normal","ambiguity":1.0,"uncertainty":1.0,"needs_memory":False,"needs_library":False,"needs_diagnosis":False,"needs_reasoning":False,"confidence":0.0,"linguistic_analysis":{"analysis_status":"empty_input"}}
        words=re.findall(r"[\wÀ-ÿ]+(?:[-'][\wÀ-ÿ]+)?",text,flags=re.UNICODE)
        q=self.question(text)
        verbs=self.verbs(words)
        pronouns=[w for w in words if w in {"eu","tu","ele","ela","nós","vocês","eles","elas","isso","isto","aquilo","esse","essa","este","esta","aquele","aquela","quem","que","meu","minha","seu","sua","me","te","se","lhe"}]
        articles=[w for w in words if w in {"o","a","os","as","um","uma","uns","umas"}]
        subject=pronouns[0] if pronouns else None
        if not subject and articles:
            i=words.index(articles[0])
            if i+1<len(words): subject=" ".join(words[i:i+2])
        analysis={"tokens":words,"verbs":verbs,"possible_subject":subject,"question":q,"has_question_mark":text.endswith("?"),"sentence_count":max(1,len(re.findall(r"[.!?]+",text))),"analysis_status":"heuristic_structural_reading"}
        rules=self.language["intent"]
        if q["type"] in {"definition","identity","time","place","cause","function","process","comparison"}: intent,confidence=("concept_basic",0.93) if q["type"] in {"definition","identity","time","place"} else ("concept_scoped",0.84)
        elif self.has_phrase(text,rules["phatic"]["examples"]): intent,confidence="phatic",0.98
        elif self.has_any(text,rules["clinical_case"]["examples"]): intent,confidence="clinical_case",0.92
        elif self.has_any(text,rules["continuity"]["examples"]): intent,confidence="continuity",0.90
        elif self.has_any(text,rules["correction"]["examples"]): intent,confidence="correction",0.90
        elif self.has_any(text,rules["doubt"]["examples"]): intent,confidence="doubt",0.88
        elif self.has_any(text,rules["action"]["examples"]): intent,confidence="action",0.80
        elif self.has_any(text,rules["concept_basic"]["examples"]) or q["type"] in {"definition","identity","time","place"}: intent,confidence="concept_basic",0.93
        elif self.has_any(text,rules["concept_scoped"]["examples"]) or q["type"] in {"cause","function","process","comparison"} or text.endswith("?"): intent,confidence="concept_scoped",0.84
        else: intent,confidence="unknown",0.45
        depth="normal"
        for level,markers in self.language["depth"].items():
            if self.has_any(text,markers): depth=level; break
        ambiguity="too_short" if len(words)<=2 else ("context_dependent" if intent=="continuity" or (q["type"] and not q["topic_candidate"]) else "clear")
        needs_memory=intent in {"continuity","unknown","doubt"} or any(w in {"ele","ela","isso","isto","aquilo","esse","essa","este","esta","aquele","aquela"} for w in words)
        needs_library=intent in {"concept_basic","concept_scoped","clinical_case"}
        return {"intent":intent,"scope":q["topic_candidate"] or text,"depth":depth,"ambiguity":{"clear":0.0,"too_short":0.45,"context_dependent":0.35}.get(ambiguity,0.25),"uncertainty":max(0.0,1.0-confidence),"needs_memory":needs_memory,"needs_library":needs_library,"needs_diagnosis":intent=="clinical_case","needs_reasoning":intent!="phatic","confidence":confidence,"linguistic_analysis":analysis}

LANGUAGE_ENGINE=LanguageEngine()

BOOK_LEARNING={
    "source":"portuguese_language_knowledge.pdf",
    "chunks":5,
    "pages_per_chunk":25,
    "principles":[
        "compreender_antes_de_buscar",
        "definicao_antes_de_expansao",
        "usar_contexto_para_interpretar",
        "distinguir_classe_gramatical_de_funcao_sintatica",
        "distinguir_tema_de_intencao",
        "nao_confundir_ocorrencia_lexical_com_evidencia_semantica",
        "sintetizar_a_partir_da_fonte_em_vez_de_repetir_fragmentos"
    ]
}

def find_linguistic_concept(topic):
    key=(topic or "").strip().lower()
    if not key:
        return None
    for pool in (
        PORTUGUESE.get("core_concepts",{}),
        PORTUGUESE.get("word_classes",{}),
        PORTUGUESE.get("syntax",{})
    ):
        if key in pool:
            return {"key":key,**pool[key]}
    if key.endswith("s"):
        singular=key[:-1]
        for pool in (
            PORTUGUESE.get("core_concepts",{}),
            PORTUGUESE.get("word_classes",{}),
            PORTUGUESE.get("syntax",{})
        ):
            if singular in pool:
                return {"key":singular,**pool[singular]}
    return None

def compose_book_grounded_answer(topic,qtype,depth,evidence):
    concept=find_linguistic_concept(topic)
    if qtype=="definition" and concept and concept.get("definition"):
        answer=f"{topic.capitalize()} é {concept['definition'].rstrip('.')}."
        examples=concept.get("examples")
        if examples and depth in {"normal","technical","deep"}:
            answer+="\n\nExemplo(s): "+"; ".join(map(str,examples[:3]))+"."
        if evidence:
            best=evidence[0]
            answer+=(
                "\n\nNo livro de Língua Portuguesa, encontrei evidência relacionada "
                f"ao conceito nas páginas {best.get('start_page')}–{best.get('end_page')}: "
                f"{best.get('text')}"
            )
        return answer
    return None


def chunk_urls(entry):
    # The index stores the relative cache path. Keep both a raw-file route
    # and the GitHub Contents API as a fallback for Worker egress.
    name=entry["cache_file"].replace("\\","/").lstrip("/")
    path="aigar-c-2/AIGAR_LIBRARY/cache/"+name
    return [
        "https://raw.githubusercontent.com/instituto-delyone/idmt-site/main/"+path,
        "https://api.github.com/repos/instituto-delyone/idmt-site/contents/"+path+"?ref=main",
    ]

async def load_chunk_text(entry):
    for url in chunk_urls(entry):
        try:
            r=await fetch(
                url,
                method="GET",
                headers={"Accept":"application/vnd.github+json"},
            )
            if r.status>=400:
                continue
            if "api.github.com" in url:
                data=await r.json()
                encoded=(data.get("content") or "").replace("\n","")
                if not encoded:
                    continue
                return base64.b64decode(encoded).decode("utf-8")
            return await r.text()
        except Exception:
            continue
    return None

# Catálogo explícito dos índices públicos/versionados. Evita depender do
# endpoint Contents API do GitHub no boot do Worker, que pode falhar e acionar
# silenciosamente o fallback de uma única biblioteca (Português).
INDEX_URLS = [
    "https://raw.githubusercontent.com/instituto-delyone/idmt-site/main/aigar-c-2/AIGAR_LIBRARY/indexes/arquitetura_organizacao_computadores.index.json",
    "https://raw.githubusercontent.com/instituto-delyone/idmt-site/main/aigar-c-2/AIGAR_LIBRARY/indexes/etica.index.json",
    "https://raw.githubusercontent.com/instituto-delyone/idmt-site/main/aigar-c-2/AIGAR_LIBRARY/indexes/interacoes_aigar.index.json",
    "https://raw.githubusercontent.com/instituto-delyone/idmt-site/main/aigar-c-2/AIGAR_LIBRARY/indexes/matematica_computacional.index.json",
    "https://raw.githubusercontent.com/instituto-delyone/idmt-site/main/aigar-c-2/AIGAR_LIBRARY/indexes/portuguese_language_knowledge.index.json",
    "https://raw.githubusercontent.com/instituto-delyone/idmt-site/main/aigar-c-2/AIGAR_LIBRARY/indexes/raciocinio_logico_matematica.index.json",
    "https://raw.githubusercontent.com/instituto-delyone/idmt-site/main/aigar-c-2/AIGAR_LIBRARY/indexes/sapiens.index.json",
]
INDEX_DIRECTORY_URL = "https://api.github.com/repos/instituto-delyone/idmt-site/contents/aigar-c-2/AIGAR_LIBRARY/indexes?ref=main"
INDEX_CACHE = None
INDEX_CACHE_AT = 0
LIBRARY_BOOT_CACHE = None
LIBRARY_BOOT_STATUS = None
LIBRARY_BOOT_AT = 0
LIBRARY_CACHE_TTL_SECONDS = 300

# Índices incorporados como catálogo de segurança: o boot não depende da descoberta remota
# de arquivos de índice. O texto dos chunks continua sendo carregado sob demanda do GitHub.
EMBEDDED_LIBRARY_INDEXES = json.loads(r'''[{"schema_version":"1.0","builder_version":"1.0.0","source":{"name":"arquitetura-e-organizacao-computadores-8a.pdf","key":"arquitetura_organizacao_computadores","sha256":"5eac460e33281c166dd5c74532de663934f395ab916bee75c98df559ff4ae570","type":"pdf"},"chunking":{"unit":"pages","size":25,"preserves_source_text":true,"summarizes":false,"cache_policy":"private_local"},"chunks":[{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-C7BD5AB44F2D","sequence":1,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":1,"end_page":25,"text_length":69428,"text_checksum":"f5c8e2e172607676ec4af15d3c70e872a92e5056734abf01ef7cfe732c792d35","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-C7BD5AB44F2D.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-1B02DB9BC61F","sequence":2,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":26,"end_page":50,"text_length":78667,"text_checksum":"647b3d46b72363d46e37b2bdd1c69f5117e130321e3fdc62ddd1c2b96af5ee87","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-1B02DB9BC61F.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-C0B64EAB1D21","sequence":3,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":51,"end_page":75,"text_length":77677,"text_checksum":"663926a7cf3164c3d793034f93c6fbac6813ee722a60775cfed685cab5386938","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-C0B64EAB1D21.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-6A494AE01650","sequence":4,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":76,"end_page":100,"text_length":70036,"text_checksum":"16a860075be3f2b3c8c6031216efaa6ec2dbe5a0da67cdf3058a949275342438","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-6A494AE01650.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-06295063ED1D","sequence":5,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":101,"end_page":125,"text_length":67749,"text_checksum":"09f426ae123adbe2d8f24f65f7676f699b432b4e8852377fbeb7de71244ded88","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-06295063ED1D.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-143F2D77E7E1","sequence":6,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":126,"end_page":150,"text_length":87035,"text_checksum":"51f32471a1aa4ca82fd203e17d8d7b64459b7f07b95a93ed39dd45cf771e7b91","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-143F2D77E7E1.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-A92F9E9A451B","sequence":7,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":151,"end_page":175,"text_length":70489,"text_checksum":"ee20d7263c0f270aaf83fa1a94eeae77fc545b8feea8e3d6f452fe66067f5f70","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-A92F9E9A451B.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-D908DC9F8D90","sequence":8,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":176,"end_page":200,"text_length":80386,"text_checksum":"35168113a57fd82b886ac2b1fc9aaa167e871dfea6abc2bcec2c678f6f2cbc48","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-D908DC9F8D90.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-4EA5B96F140A","sequence":9,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":201,"end_page":225,"text_length":79033,"text_checksum":"fc9cbbe290d7c4589a38961fd7d09e263faeeaf8bfc99f85d8f7fdfafe0197a8","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-4EA5B96F140A.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-92620C9F0553","sequence":10,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":226,"end_page":250,"text_length":74021,"text_checksum":"905eb885d19141a8c80705a0c766a8301fba09b91cf13e3efb834157df8b033d","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-92620C9F0553.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-40B869267294","sequence":11,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":251,"end_page":275,"text_length":66824,"text_checksum":"3c1c0c5b44071fa027dea8d1d1e1160a530bf2c3b7ac255da5a57575cb3939b7","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-40B869267294.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-CE9998A6682C","sequence":12,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":276,"end_page":300,"text_length":67168,"text_checksum":"09df73643d7e500086cdc971e4aa751e909773248252ad18027af723cd594c16","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-CE9998A6682C.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-E57EC8F1F07D","sequence":13,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":301,"end_page":325,"text_length":77946,"text_checksum":"3139cce2b455466671efa135cd7e625a788ce4ac78f15e6f5af6056cae621df2","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-E57EC8F1F07D.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-EBF52220181C","sequence":14,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":326,"end_page":350,"text_length":77415,"text_checksum":"9e88ed6720b199757fc8e17400e91065beaa0478ab6dc6df502970a9c8a502a7","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-EBF52220181C.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-C8AF9B7B4A22","sequence":15,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":351,"end_page":375,"text_length":85558,"text_checksum":"a162652442d948efd486ced6469bf95ecaa243d11307a1aaacc944bd2d16b52d","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-C8AF9B7B4A22.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-9A52B29D4FCC","sequence":16,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":376,"end_page":400,"text_length":74248,"text_checksum":"d4e45b111704b846e922f0fd9834ff04ee92577515dce0e900de9aa0bfb02b71","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-9A52B29D4FCC.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-8A5686C25DD6","sequence":17,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":401,"end_page":425,"text_length":87065,"text_checksum":"92d5c439a6e042b73b99d2c3fdc19df23096c12f14a6d3875c4a9ff48857fb1b","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-8A5686C25DD6.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-C0A088BEB67B","sequence":18,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":426,"end_page":450,"text_length":75675,"text_checksum":"15f79e4d4d53632d70bc81da4803c4b32dabfd47e408138bed3e52943411f474","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-C0A088BEB67B.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-339776D6963E","sequence":19,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":451,"end_page":475,"text_length":77891,"text_checksum":"6f49b5acc30c722197caecf278197a5823d7bd5c3b99e771fc558f025e17b4a9","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-339776D6963E.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-9DEAAE995621","sequence":20,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":476,"end_page":500,"text_length":64922,"text_checksum":"be47037d4003fdf65c71ae8f1f1d7dee1ed191b503dfb562664b3651b1c26b64","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-9DEAAE995621.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-FA7E40A31EF8","sequence":21,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":501,"end_page":525,"text_length":66603,"text_checksum":"95b70d06938beb8ed1376b796331122611877dafcc61170780718cfe2aa126f8","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-FA7E40A31EF8.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-2A545793EE5C","sequence":22,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":526,"end_page":550,"text_length":82117,"text_checksum":"d78b580a667c1fc6ede9993a70cbcd4cfab54765865d2e2277f7f4c989fba934","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-2A545793EE5C.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-43D9DDB4B9C8","sequence":23,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":551,"end_page":575,"text_length":79083,"text_checksum":"3339d90edf47ab07a22f611d11bfa9cdea746cc1714c579183931605f940e532","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-43D9DDB4B9C8.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-D2FBDDBF93C6","sequence":24,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":576,"end_page":600,"text_length":76399,"text_checksum":"39e979cb680f108c1d1e59b91db8e6aae44fde4968712ebed61edcf4170276cd","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-D2FBDDBF93C6.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-DD2EB89CFCE1","sequence":25,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":601,"end_page":625,"text_length":78133,"text_checksum":"b235d16a2640c4abcf505e7aaf24f50b32b0a2329a3464671c9340e67213b453","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-DD2EB89CFCE1.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-AE56892F3041","sequence":26,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":626,"end_page":643,"text_length":72812,"text_checksum":"77db53cb31634e2a509091f7af8725aaff927ac1b1ec0fb1ca6a12afba361fc7","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-AE56892F3041.txt"}]},{"schema_version":"1.0","builder_version":"1.0.0","source":{"name":"etica.pdf","key":"etica","sha256":"06e54c88593641072181188cc6bef92aab06aa6040d60f863fe12a12f2a0f40e","type":"pdf"},"chunking":{"unit":"pages","size":25,"preserves_source_text":true,"summarizes":false,"cache_policy":"private_local"},"chunks":[{"id":"ETICA-631B9D6E7B85","sequence":1,"source":"etica.pdf","source_key":"etica","start_page":1,"end_page":25,"text_length":53440,"text_checksum":"952ac35b8c67a9973976ea445cf8e675bd1083adf1c89967fb979e04d8905d84","cache_file":"etica\\ETICA-631B9D6E7B85.txt"},{"id":"ETICA-09EDDCC57A0C","sequence":2,"source":"etica.pdf","source_key":"etica","start_page":26,"end_page":50,"text_length":67110,"text_checksum":"224f20b68c06595514a8209ab0f9117096cb6b298dc9063c6121c49fef626579","cache_file":"etica\\ETICA-09EDDCC57A0C.txt"},{"id":"ETICA-EA2514E067DC","sequence":3,"source":"etica.pdf","source_key":"etica","start_page":51,"end_page":56,"text_length":7667,"text_checksum":"da1b40c423aedc0d9cd29e8861ab60abad15a6d30ce646dd4d497b7b1ae4319a","cache_file":"etica\\ETICA-EA2514E067DC.txt"}]},{"schema_version":"1.0","builder_version":"1.0.0","source":{"name":"interações DrDelyone-AIGAR.txt","key":"interacoes_aigar","sha256":"29c97629bec3fb0b7d6cdfb1b4c0492f2587c459b952aaae5e06b6a57b1769f7","type":"txt"},"chunking":{"unit":"characters","size":24000,"preserves_source_text":true,"summarizes":false,"cache_policy":"private_local"},"chunks":[{"id":"INTERACOES_AIGAR-BA384194F5AB","sequence":1,"source":"interações DrDelyone-AIGAR.txt","source_key":"interacoes_aigar","start_page":null,"end_page":null,"text_length":5556,"text_checksum":"aab6e84d38f302abe177b28fe5b3ed686d210929cca4278e84d7bd3b30a03f34","cache_file":"interacoes_aigar\\INTERACOES_AIGAR-BA384194F5AB.txt"}]},{"schema_version":"1.0","builder_version":"1.0.0","source":{"name":"MatematicaComputacional.pdf","key":"matematica_computacional","sha256":"661b6e53ba82d101cb5033ab3f4665943cb66468b2758dcaffc5b27e5574c121","type":"pdf"},"chunking":{"unit":"pages","size":25,"preserves_source_text":true,"summarizes":false,"cache_policy":"private_local"},"chunks":[{"id":"MATEMATICA_COMPUTACIONAL-F9F9C339933C","sequence":1,"source":"MatematicaComputacional.pdf","source_key":"matematica_computacional","start_page":1,"end_page":25,"text_length":50899,"text_checksum":"e84cce0c5ce3e5f7489bf325a0536cf2733f0a807bb1d94fb7c14c944fbae0fd","cache_file":"matematica_computacional\\MATEMATICA_COMPUTACIONAL-F9F9C339933C.txt"},{"id":"MATEMATICA_COMPUTACIONAL-909E626D6BB0","sequence":2,"source":"MatematicaComputacional.pdf","source_key":"matematica_computacional","start_page":26,"end_page":50,"text_length":43184,"text_checksum":"36337e21ad729b4b631865a2e61afa5a2360798b1ccc71e450312e1c7f27eeb0","cache_file":"matematica_computacional\\MATEMATICA_COMPUTACIONAL-909E626D6BB0.txt"},{"id":"MATEMATICA_COMPUTACIONAL-6C77A8CB9BE6","sequence":3,"source":"MatematicaComputacional.pdf","source_key":"matematica_computacional","start_page":51,"end_page":75,"text_length":48772,"text_checksum":"58baad0b7f39aa9a2383ab632387d6e3d6175a6cb6f5544c6f774c43f3d98095","cache_file":"matematica_computacional\\MATEMATICA_COMPUTACIONAL-6C77A8CB9BE6.txt"},{"id":"MATEMATICA_COMPUTACIONAL-F7E79A727071","sequence":4,"source":"MatematicaComputacional.pdf","source_key":"matematica_computacional","start_page":76,"end_page":100,"text_length":44686,"text_checksum":"526c5f44157e9dd41d67271e296804d3f3ed923e7347b154938be60689bb7e9a","cache_file":"matematica_computacional\\MATEMATICA_COMPUTACIONAL-F7E79A727071.txt"},{"id":"MATEMATICA_COMPUTACIONAL-542A17C109AE","sequence":5,"source":"MatematicaComputacional.pdf","source_key":"matematica_computacional","start_page":101,"end_page":125,"text_length":43643,"text_checksum":"c35237eef872f298ebf75336be508d42baed19a3b1404d6ce3c4177c8f7aa716","cache_file":"matematica_computacional\\MATEMATICA_COMPUTACIONAL-542A17C109AE.txt"},{"id":"MATEMATICA_COMPUTACIONAL-5ABF7E583415","sequence":6,"source":"MatematicaComputacional.pdf","source_key":"matematica_computacional","start_page":126,"end_page":150,"text_length":41196,"text_checksum":"c51bfd843835247e963edd2f40e87780950799da1e2cc28f14fe89e62c8a48b1","cache_file":"matematica_computacional\\MATEMATICA_COMPUTACIONAL-5ABF7E583415.txt"},{"id":"MATEMATICA_COMPUTACIONAL-ADB8DA996932","sequence":7,"source":"MatematicaComputacional.pdf","source_key":"matematica_computacional","start_page":151,"end_page":175,"text_length":46017,"text_checksum":"a0f0b27a2d9f476f71511fcd259e376e67866529c45e5bfe4ae32971cf10125b","cache_file":"matematica_computacional\\MATEMATICA_COMPUTACIONAL-ADB8DA996932.txt"},{"id":"MATEMATICA_COMPUTACIONAL-78DFA175BA3E","sequence":8,"source":"MatematicaComputacional.pdf","source_key":"matematica_computacional","start_page":176,"end_page":192,"text_length":26953,"text_checksum":"99053c68dc1a4fd39c481323f6872c4aafe716b141d4b5760bda0b87178d278b","cache_file":"matematica_computacional\\MATEMATICA_COMPUTACIONAL-78DFA175BA3E.txt"}]},{"schema_version":"1.0","builder_version":"1.0.0","source":{"name":"portuguese_language_knowledge.pdf","key":"portuguese_language_knowledge","sha256":"54e55ce74fea4a06c317dd4011954357ce4af64d576e7aeac0d412071a04b3c4","type":"pdf"},"chunking":{"unit":"pages","size":25,"preserves_source_text":true,"summarizes":false,"cache_policy":"private_local"},"chunks":[{"id":"PORTUGUESE_LANGUAGE_KNOWLEDGE-6D6AF6C3B49F","sequence":1,"source":"portuguese_language_knowledge.pdf","source_key":"portuguese_language_knowledge","start_page":1,"end_page":25,"text_length":39870,"text_checksum":"35d2a1e9de227044da72bff4660605f5e0b08886322a90073c7d422bd018ac60","cache_file":"portuguese_language_knowledge\\PORTUGUESE_LANGUAGE_KNOWLEDGE-6D6AF6C3B49F.txt"},{"id":"PORTUGUESE_LANGUAGE_KNOWLEDGE-5FA2F5CB4ABB","sequence":2,"source":"portuguese_language_knowledge.pdf","source_key":"portuguese_language_knowledge","start_page":26,"end_page":50,"text_length":57872,"text_checksum":"e0324b769d58707a109bec67671c2bae4c4cbda04f0f32615363255efa185bc5","cache_file":"portuguese_language_knowledge\\PORTUGUESE_LANGUAGE_KNOWLEDGE-5FA2F5CB4ABB.txt"},{"id":"PORTUGUESE_LANGUAGE_KNOWLEDGE-707869DB28A4","sequence":3,"source":"portuguese_language_knowledge.pdf","source_key":"portuguese_language_knowledge","start_page":51,"end_page":75,"text_length":57372,"text_checksum":"49e143848dcdd551d1855d32563e0fa85d2fa190fd4b982b27074581389c52cb","cache_file":"portuguese_language_knowledge\\PORTUGUESE_LANGUAGE_KNOWLEDGE-707869DB28A4.txt"},{"id":"PORTUGUESE_LANGUAGE_KNOWLEDGE-5BA56CEA70AA","sequence":4,"source":"portuguese_language_knowledge.pdf","source_key":"portuguese_language_knowledge","start_page":76,"end_page":100,"text_length":58671,"text_checksum":"e1c8139b2f3b6fd0ff3a5652a1a9c5798baea956c7185dd47b90272139fec74d","cache_file":"portuguese_language_knowledge\\PORTUGUESE_LANGUAGE_KNOWLEDGE-5BA56CEA70AA.txt"},{"id":"PORTUGUESE_LANGUAGE_KNOWLEDGE-27DCC3509BC0","sequence":5,"source":"portuguese_language_knowledge.pdf","source_key":"portuguese_language_knowledge","start_page":101,"end_page":125,"text_length":52489,"text_checksum":"2e897d836578d812b89938cabf31f3850405d77f6d41bcd5c21e1e9ea3c1eaf7","cache_file":"portuguese_language_knowledge\\PORTUGUESE_LANGUAGE_KNOWLEDGE-27DCC3509BC0.txt"}]},{"schema_version":"1.0","builder_version":"1.0.0","source":{"name":"Raciocinio_Logico_e_Matematica_Para_Concursos_Cespe.pdf","key":"raciocinio_logico_matematica","sha256":"5ec0078c91ef0c4e16c2e70773bab0134d64c91f1299b68f46dd6d5421bc1987","type":"pdf"},"chunking":{"unit":"pages","size":25,"preserves_source_text":true,"summarizes":false,"cache_policy":"private_local"},"chunks":[{"id":"RACIOCINIO_LOGICO_MATEMATICA-826EB0C22532","sequence":1,"source":"Raciocinio_Logico_e_Matematica_Para_Concursos_Cespe.pdf","source_key":"raciocinio_logico_matematica","start_page":1,"end_page":25,"text_length":26311,"text_checksum":"4ea479cb4f4c2f13f803db45df745f13d8a09eda7824003653447ade8c31a851","cache_file":"raciocinio_logico_matematica\\RACIOCINIO_LOGICO_MATEMATICA-826EB0C22532.txt"},{"id":"RACIOCINIO_LOGICO_MATEMATICA-FB7052DBF395","sequence":2,"source":"Raciocinio_Logico_e_Matematica_Para_Concursos_Cespe.pdf","source_key":"raciocinio_logico_matematica","start_page":26,"end_page":50,"text_length":51932,"text_checksum":"6fb53b161f2ac719a7185db1e8461be7609607052e361966038bd05d1f9c348d","cache_file":"raciocinio_logico_matematica\\RACIOCINIO_LOGICO_MATEMATICA-FB7052DBF395.txt"},{"id":"RACIOCINIO_LOGICO_MATEMATICA-3238564A1668","sequence":3,"source":"Raciocinio_Logico_e_Matematica_Para_Concursos_Cespe.pdf","source_key":"raciocinio_logico_matematica","start_page":51,"end_page":75,"text_length":48244,"text_checksum":"d53e0b65375db5c78944e00afc8c7aca4c4d6b653953f639cf4990734f257bac","cache_file":"raciocinio_logico_matematica\\RACIOCINIO_LOGICO_MATEMATICA-3238564A1668.txt"},{"id":"RACIOCINIO_LOGICO_MATEMATICA-E68DD1EAB4E7","sequence":4,"source":"Raciocinio_Logico_e_Matematica_Para_Concursos_Cespe.pdf","source_key":"raciocinio_logico_matematica","start_page":76,"end_page":100,"text_length":51082,"text_checksum":"644a628867fe89321af5a2941afdee2cb3499d86a24476434a8f7c5f056b66e8","cache_file":"raciocinio_logico_matematica\\RACIOCINIO_LOGICO_MATEMATICA-E68DD1EAB4E7.txt"},{"id":"RACIOCINIO_LOGICO_MATEMATICA-26D11EF77264","sequence":5,"source":"Raciocinio_Logico_e_Matematica_Para_Concursos_Cespe.pdf","source_key":"raciocinio_logico_matematica","start_page":101,"end_page":125,"text_length":48708,"text_checksum":"e1b1fcd76e542125377f619cf0d2d2a9d08877cfc45ce7073a9b889c63b7260b","cache_file":"raciocinio_logico_matematica\\RACIOCINIO_LOGICO_MATEMATICA-26D11EF77264.txt"},{"id":"RACIOCINIO_LOGICO_MATEMATICA-E5DB95ED1BE3","sequence":6,"source":"Raciocinio_Logico_e_Matematica_Para_Concursos_Cespe.pdf","source_key":"raciocinio_logico_matematica","start_page":126,"end_page":150,"text_length":56183,"text_checksum":"f45003c9b538e45c74efd06c1869649b18480d8853d4664b90db00f1d93cb025","cache_file":"raciocinio_logico_matematica\\RACIOCINIO_LOGICO_MATEMATICA-E5DB95ED1BE3.txt"},{"id":"RACIOCINIO_LOGICO_MATEMATICA-852F470E8C4B","sequence":7,"source":"Raciocinio_Logico_e_Matematica_Para_Concursos_Cespe.pdf","source_key":"raciocinio_logico_matematica","start_page":151,"end_page":175,"text_length":61602,"text_checksum":"e782cc8b3647c00ed0bfe6247f3fb9693a0b9f99c7cd6b9ce4c4988cbdfeeb63","cache_file":"raciocinio_logico_matematica\\RACIOCINIO_LOGICO_MATEMATICA-852F470E8C4B.txt"},{"id":"RACIOCINIO_LOGICO_MATEMATICA-B90130B0337D","sequence":8,"source":"Raciocinio_Logico_e_Matematica_Para_Concursos_Cespe.pdf","source_key":"raciocinio_logico_matematica","start_page":176,"end_page":200,"text_length":64352,"text_checksum":"e9607e87fe2803bbded0ed1c1575a7b5a343b5bd35b8b25c079f2200439580bb","cache_file":"raciocinio_logico_matematica\\RACIOCINIO_LOGICO_MATEMATICA-B90130B0337D.txt"},{"id":"RACIOCINIO_LOGICO_MATEMATICA-8E1053DD2620","sequence":9,"source":"Raciocinio_Logico_e_Matematica_Para_Concursos_Cespe.pdf","source_key":"raciocinio_logico_matematica","start_page":201,"end_page":201,"text_length":42,"text_checksum":"6cd09d3b6ce59e377081009f983655fe2fa659600e21f968bb6dd40853899a5b","cache_file":"raciocinio_logico_matematica\\RACIOCINIO_LOGICO_MATEMATICA-8E1053DD2620.txt"}]},{"schema_version":"1.0","builder_version":"1.0.0","source":{"name":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","key":"sapiens","sha256":"5e05b6919909e3ee77de3f91d3b32aedb1447f844971aec7f05a4d9c0f508eee","type":"pdf"},"chunking":{"unit":"pages","size":25,"preserves_source_text":true,"summarizes":false,"cache_policy":"private_local"},"chunks":[{"id":"SAPIENS-C0A5AE9C57B0","sequence":1,"source":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","source_key":"sapiens","start_page":1,"end_page":25,"text_length":32145,"text_checksum":"b6c62eb7b7faaffe26d953d0e47657917fd83cd185b0fde9a2d6f21d87a76fe3","cache_file":"sapiens\\SAPIENS-C0A5AE9C57B0.txt"},{"id":"SAPIENS-3FEB0220045C","sequence":2,"source":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","source_key":"sapiens","start_page":26,"end_page":50,"text_length":46594,"text_checksum":"17f3548a82fcb8f380908c555362ae7ef7368161cc24b44fb1b8d9a537868b92","cache_file":"sapiens\\SAPIENS-3FEB0220045C.txt"},{"id":"SAPIENS-EE694DAC02C4","sequence":3,"source":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","source_key":"sapiens","start_page":51,"end_page":75,"text_length":48701,"text_checksum":"2128c2bbbbcff0bfa3cec5c6582ebc0897023c4201f27b083fc93e5f981c9452","cache_file":"sapiens\\SAPIENS-EE694DAC02C4.txt"},{"id":"SAPIENS-8DB2612155FC","sequence":4,"source":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","source_key":"sapiens","start_page":76,"end_page":100,"text_length":45391,"text_checksum":"aa238b22484373635f37b0e55c7feef10e382cadf7bdc7b0ae9aafbcdc7c8c18","cache_file":"sapiens\\SAPIENS-8DB2612155FC.txt"},{"id":"SAPIENS-D00DADDBAFC8","sequence":5,"source":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","source_key":"sapiens","start_page":101,"end_page":125,"text_length":46815,"text_checksum":"19f45aa0c4c8545318bd5840ee158c4225d840a1f6dd6728a03eaa062777b65e","cache_file":"sapiens\\SAPIENS-D00DADDBAFC8.txt"},{"id":"SAPIENS-F3B80B38E22F","sequence":6,"source":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","source_key":"sapiens","start_page":126,"end_page":150,"text_length":47570,"text_checksum":"e4885615f1ec82b033aa7cf462b4559669c78348494f08fbc31006776d697aad","cache_file":"sapiens\\SAPIENS-F3B80B38E22F.txt"},{"id":"SAPIENS-C9A063D77C76","sequence":7,"source":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","source_key":"sapiens","start_page":151,"end_page":175,"text_length":45732,"text_checksum":"4354f7ce09bdd2c20692ebe1e5296508caaf226be1dd99e52244c0b4fece2bf0","cache_file":"sapiens\\SAPIENS-C9A063D77C76.txt"},{"id":"SAPIENS-C706D47E57E9","sequence":8,"source":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","source_key":"sapiens","start_page":176,"end_page":200,"text_length":40193,"text_checksum":"1e4ae5f3342082620f9df28db9e857d60205a4e32792534f66a870f0364c9ee8","cache_file":"sapiens\\SAPIENS-C706D47E57E9.txt"},{"id":"SAPIENS-A55B52FA07CF","sequence":9,"source":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","source_key":"sapiens","start_page":201,"end_page":225,"text_length":48430,"text_checksum":"7c97c4876e308112d220a6f74c0527030fc4850ba766d5a1299b5d7144c94adf","cache_file":"sapiens\\SAPIENS-A55B52FA07CF.txt"},{"id":"SAPIENS-BAE9B341E493","sequence":10,"source":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","source_key":"sapiens","start_page":226,"end_page":250,"text_length":44312,"text_checksum":"37affbeb381c906a2041cea97796cde237323d1405b615b4590452bc2fa7788c","cache_file":"sapiens\\SAPIENS-BAE9B341E493.txt"},{"id":"SAPIENS-06566B4CD3DD","sequence":11,"source":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","source_key":"sapiens","start_page":251,"end_page":275,"text_length":40922,"text_checksum":"f0fc28b6a4ab514910df9fc2993a1a02d334e871c7a7fdca3d3630e08ad69e26","cache_file":"sapiens\\SAPIENS-06566B4CD3DD.txt"},{"id":"SAPIENS-75591DF9D815","sequence":12,"source":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","source_key":"sapiens","start_page":276,"end_page":300,"text_length":46854,"text_checksum":"a4c1e33301d3980f5328617dfacf0771c920542f4d3a8296dceffa161b60fde7","cache_file":"sapiens\\SAPIENS-75591DF9D815.txt"},{"id":"SAPIENS-C851DE33B9C3","sequence":13,"source":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","source_key":"sapiens","start_page":301,"end_page":325,"text_length":48147,"text_checksum":"5df4e6521c735412cdfc870d85d098acf23188b8fac6bb90e16a1d0d8451ae1f","cache_file":"sapiens\\SAPIENS-C851DE33B9C3.txt"},{"id":"SAPIENS-2195FD7E3B43","sequence":14,"source":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","source_key":"sapiens","start_page":326,"end_page":350,"text_length":47603,"text_checksum":"89ff0b86fe9713f3e6c6ac6daa33560333377bab5a2eb243f7a15be3e348e8a0","cache_file":"sapiens\\SAPIENS-2195FD7E3B43.txt"},{"id":"SAPIENS-F8B99E91DEC0","sequence":15,"source":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","source_key":"sapiens","start_page":351,"end_page":375,"text_length":46093,"text_checksum":"dc908b13ec2776287137411136bdaa18a55f9725cd0e05d45e2bd2f28c4bf116","cache_file":"sapiens\\SAPIENS-F8B99E91DEC0.txt"},{"id":"SAPIENS-3612835835EE","sequence":16,"source":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","source_key":"sapiens","start_page":376,"end_page":400,"text_length":46497,"text_checksum":"b210c8885c881e37b8eba331fdab67f6b30a79a07aa5a7c38bd9d197f4153771","cache_file":"sapiens\\SAPIENS-3612835835EE.txt"},{"id":"SAPIENS-FF08F77664B1","sequence":17,"source":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","source_key":"sapiens","start_page":401,"end_page":425,"text_length":48111,"text_checksum":"814f2d7b6af15c6b098e47636d9ae99a20bf83bbf6d36a94e41b4799fa0eba81","cache_file":"sapiens\\SAPIENS-FF08F77664B1.txt"},{"id":"SAPIENS-DA9F3E981D79","sequence":18,"source":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","source_key":"sapiens","start_page":426,"end_page":450,"text_length":49681,"text_checksum":"de15a10f1dd8889f5cdb79ea02b041c6dc83a9a66fbd53ce79c445ad8adbcffc","cache_file":"sapiens\\SAPIENS-DA9F3E981D79.txt"},{"id":"SAPIENS-A56A1ED270E5","sequence":19,"source":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","source_key":"sapiens","start_page":451,"end_page":475,"text_length":46600,"text_checksum":"fa69f48311e4038eab0c50b1376b3c4547354a6fa6a6bf2c3bbeb2e696baac82","cache_file":"sapiens\\SAPIENS-A56A1ED270E5.txt"},{"id":"SAPIENS-47ADA8FA160B","sequence":20,"source":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","source_key":"sapiens","start_page":476,"end_page":500,"text_length":51383,"text_checksum":"a924c6715e4916a3b90e6f9e5cb5e9079f5a5612280e011eabe1e7f831f53fba","cache_file":"sapiens\\SAPIENS-47ADA8FA160B.txt"},{"id":"SAPIENS-C68E9539629D","sequence":21,"source":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","source_key":"sapiens","start_page":501,"end_page":506,"text_length":4256,"text_checksum":"7067a5f2f3a9768e8be147788481f7fac17584eb39d86d464d71a982d0c62323","cache_file":"sapiens\\SAPIENS-C68E9539629D.txt"}]}]''')

async def load_library_indexes():
    """Retorna o catálogo completo mesmo quando a descoberta remota do GitHub falha."""
    global INDEX_CACHE, INDEX_CACHE_AT
    if INDEX_CACHE is not None and time.time() - INDEX_CACHE_AT < LIBRARY_CACHE_TTL_SECONDS:
        return INDEX_CACHE

    # Catálogo local embarcado contém todas as fontes e todos os metadados de chunks.
    # Isso impede que uma falha de fetch silenciosamente reduza a biblioteca a Português.
    indexes = list(EMBEDDED_LIBRARY_INDEXES)

    # Atualiza os índices por URL quando disponíveis, sem perder fontes se alguma URL falhar.
    by_key = {((idx.get("source") or {}).get("key")): idx for idx in indexes}
    for url in INDEX_URLS:
        try:
            response = await fetch(url, method="GET")
            if response.status >= 400:
                continue
            remote = json.loads(await response.text())
            key = (remote.get("source") or {}).get("key")
            if key and remote.get("chunks"):
                by_key[key] = remote
        except Exception:
            continue

    INDEX_CACHE = list(by_key.values())
    INDEX_CACHE_AT = time.time()
    return INDEX_CACHE

async def boot_library():
    """Pre-carrega um chunk referencial de cada biblioteca disponível."""
    global LIBRARY_BOOT_CACHE, LIBRARY_BOOT_STATUS, LIBRARY_BOOT_AT
    if (LIBRARY_BOOT_CACHE is not None and LIBRARY_BOOT_STATUS is not None
            and time.time() - LIBRARY_BOOT_AT < LIBRARY_CACHE_TTL_SECONDS):
        loaded_count = sum(1 for item in LIBRARY_BOOT_STATUS if item.get("status") == "ready")
        ready = bool(LIBRARY_BOOT_STATUS) and loaded_count == len(LIBRARY_BOOT_STATUS)
        return {
            "ready": ready,
            "libraries": LIBRARY_BOOT_STATUS,
            "loaded": loaded_count,
            "total": len(LIBRARY_BOOT_STATUS),
            "mode": "warm_runtime_cache",
        }

    indexes = await load_library_indexes()
    statuses = []
    loaded = {}

    # Um chunk referencial por biblioteca: pequeno o suficiente para o boot,
    # mas suficiente para provar que a biblioteca está realmente acessível.
    for index in indexes:
        source = index.get("source", {}) or {}
        source_key = source.get("key") or "unknown"
        chunks = index.get("chunks", []) or []
        if not chunks:
            statuses.append({
                "source_key": source_key,
                "source": source.get("name"),
                "status": "error",
                "detail": "Índice encontrado, mas sem chunks.",
            })
            continue

        reference = sorted(
            chunks,
            key=lambda c: int(c.get("sequence", 0) or 0)
        )[0]

        cid = reference.get("id")
        text = CHUNK_CACHE.get(cid) if cid else None
        cache_origin = "runtime_cache" if text else None

        if not text and cid:
            text = await load_chunk_text(reference)
            if text:
                CHUNK_CACHE[cid] = text
                cache_origin = "remote_loaded"

        if text:
            loaded[cid] = {
                **reference,
                "text": text,
            }
            statuses.append({
                "source_key": source_key,
                "source": reference.get("source") or source.get("name"),
                "status": "ready",
                "reference_chunk": cid,
                "sequence": reference.get("sequence"),
                "start_page": reference.get("start_page"),
                "end_page": reference.get("end_page"),
                "text_length": len(text),
                "cache_origin": cache_origin,
            })
        else:
            statuses.append({
                "source_key": source_key,
                "source": reference.get("source") or source.get("name"),
                "status": "error",
                "reference_chunk": cid,
                "sequence": reference.get("sequence"),
                "start_page": reference.get("start_page"),
                "end_page": reference.get("end_page"),
                "detail": "Chunk referencial não pôde ser carregado.",
            })

    LIBRARY_BOOT_CACHE = loaded
    LIBRARY_BOOT_STATUS = statuses
    LIBRARY_BOOT_AT = time.time()
    ready = bool(statuses) and all(x.get("status") == "ready" for x in statuses)
    return {
        "ready": ready,
        "libraries": statuses,
        "loaded": sum(1 for x in statuses if x.get("status") == "ready"),
        "total": len(statuses),
        "mode": "cold_boot",
    }


async def load_chunks():
    """Compatibilidade: retorna somente o conjunto de referência já carregado."""
    boot = await boot_library()
    return list(LIBRARY_BOOT_CACHE.values()) if LIBRARY_BOOT_CACHE is not None else []


SEMANTIC_EXPANSIONS = {
    "função": {"papel","finalidade","serve","servir","funcionamento"},
    "funciona": {"funcionamento","mecanismo","processo","operação"},
    "explicar": {"explicação","conceito","definição","entendimento"},
    "definição": {"conceito","significado","definição"},
    "causa": {"motivo","razão","porque","origem"},
    "efeito": {"consequência","resultado","impacto"},
    "processo": {"etapas","mecanismo","procedimento","processo"},
    "comparar": {"diferença","semelhança","comparação"},
    "diferença": {"contraste","distinção","diferença"},
    "limite": {"limites","continuidade","aproximação"},
    "derivada": {"derivação","taxa","variação"},
    "integral": {"integração","área","antiderivada"},
    "computador": {"computação","processador","hardware","arquitetura"},
    "arquitetura": {"organização","computador","processador","memória"},
    "ética": {"moral","princípio","conduta","responsabilidade"},
    "lógica": {"raciocínio","proposição","inferência","dedução"},
    "matemática": {"cálculo","número","equação"},
    "português": {"língua","linguagem","gramática","sintaxe","semântica"},
}

SOURCE_PROFILES = {
    "portuguese_language_knowledge": {"português","gramática","língua","linguagem","sintaxe","semântica","oração","frase","período","verbo","sujeito","pronomes"},
    "matematica_computacional": {"matemática","cálculo","limite","derivada","integral","função","equação","número","álgebra","geometria"},
    "arquitetura_organizacao_computadores": {"arquitetura","computador","processador","memória","hardware","cpu","sistema","organização","barramento"},
    "etica": {"ética","moral","princípio","conduta","responsabilidade","dever","valor","justiça"},
    "raciocinio_logico_matematica": {"lógica","raciocínio","proposição","inferência","dedução","concurso","matemática","problema"},
    "interacoes_aigar": {"aigar","aurora","conversa","memória","interação","diálogo"},
    "sapiens": {"humanidade","história","evolução","civilização","sociedade","agricultura","revolução","harari"},
}

def semantic_expand(text):
    base=tokens(text)
    expanded=set(base)
    for term in list(base):
        expanded.update(SEMANTIC_EXPANSIONS.get(term,set()))
    return expanded

def source_relevance(query, source_key):
    q=semantic_expand(query)
    profile=SOURCE_PROFILES.get(source_key,set())
    if not q or not profile:
        return 0.0
    return min(1.0, len(q & profile) / max(2, int(len(profile)*0.35)))

async def library_search(query,reading,limit=5):
    indexes = await load_library_indexes()
    qinfo = reading.get("linguistic_analysis",{}).get("question",{})
    qtype = qinfo.get("type")
    topic = (qinfo.get("topic_head") or reading.get("scope") or "").lower().strip()
    query_terms = semantic_expand(query)
    topic_terms = semantic_expand(topic)
    q = query_terms or topic_terms
    candidates = []
    noise_markers=("isbn","ficha catalogográfica","sumário","referências","bibliografia","universidade federal")
    definition_markers=("é uma","é um","são","significa","consiste em","refere-se","define-se","definido como","definida como","constitui","constituída por")
    concept=find_linguistic_concept(topic)

    # Primeiro escolhemos bibliotecas/chunks pelo índice. Só depois baixamos
    # o texto dos candidatos. Assim o boot não precisa carregar todos os livros.
    indexed_candidates=[]
    for index in indexes:
        source = index.get("source", {}) or {}
        source_key = source.get("key") or ""
        source_score = source_relevance(query, source_key)
        chunks = index.get("chunks", []) or []
        for chunk in chunks:
            cid=chunk.get("id")
            if not cid:
                continue
            chunk_meta = {**chunk, "source_key": source_key}
            # O índice fornece identidade/página; o texto só é necessário
            # quando o chunk entra na lista de candidatos.
            page_hint = 0.0
            if topic and str(chunk.get("source","")).lower().find(topic) >= 0:
                page_hint = 0.05
            indexed_candidates.append((
                source_score + page_hint,
                float(chunk.get("sequence",0) or 0),
                chunk_meta
            ))

    indexed_candidates.sort(key=lambda x:(-x[0],x[1]))
    # Para uma pergunta temática, trazemos alguns chunks por biblioteca
    # potencialmente relevante; não o corpus inteiro.
    selected_meta=[]
    seen_sources=set()
    for score,_,meta in indexed_candidates:
        sk=meta.get("source_key","")
        if sk in seen_sources and len(selected_meta)>=max(limit*4,8):
            continue
        selected_meta.append(meta)
        seen_sources.add(sk)
        if len(selected_meta)>=max(limit*4,8):
            break

    async def ensure_text(entry):
        cid=entry["id"]
        text=CHUNK_CACHE.get(cid)
        if not text:
            text=await load_chunk_text(entry)
            if text:
                CHUNK_CACHE[cid]=text
        return {**entry,"text":text or ""}

    chunks=[]
    for meta in selected_meta:
        item=await ensure_text(meta)
        if item.get("text"):
            chunks.append(item)

    for chunk in chunks:
        source_key=chunk.get("source_key","")
        source_score=source_relevance(query,source_key)
        for sentence in sentences(chunk["text"]):
            lower=sentence.lower()
            st=semantic_expand(sentence)
            literal=tokens(sentence)
            literal_q=tokens(query)
            lexical_overlap=len(literal_q & literal)
            semantic_overlap=len(q & st)
            topic_overlap=len(topic_terms & st) if topic_terms else 0
            topic_hit=1 if topic and re.search(rf"\b{re.escape(topic)}\b",lower) else 0

            if not lexical_overlap and not semantic_overlap and not topic_overlap and not topic_hit and not source_score:
                continue

            lexical_score=lexical_overlap/max(1,len(literal_q))
            semantic_score=semantic_overlap/max(1,len(q))
            topic_score=min(1.0,topic_overlap/max(1,len(topic_terms))) if topic_terms else 0.0
            score=0.30*lexical_score + 0.40*semantic_score + 0.15*topic_score + 0.15*source_score + topic_hit*0.50

            if any(marker in lower for marker in noise_markers):
                score-=0.50

            if qtype=="definition":
                if topic_hit and any(marker in lower for marker in definition_markers):
                    score+=0.80
                elif topic_hit:
                    score+=0.15
                if concept and any(marker in lower for marker in definition_markers):
                    score+=0.10
            elif qtype=="function" and any(x in lower for x in ("função","serve","finalidade")):
                score+=0.35
            elif qtype=="comparison" and any(x in lower for x in ("diferença","compar","semelhan","distin")):
                score+=0.30
            elif qtype=="cause" and any(x in lower for x in ("causa","porque","razão","motivo")):
                score+=0.30

            candidates.append((
                score, semantic_score, lexical_score, source_score,
                float(chunk.get("sequence",0)), sentence, chunk
            ))

    candidates.sort(key=lambda x:(-x[0],-x[1],-x[2],-x[3],x[4],len(x[5])))
    selected=[]
    seen=set()
    for score,semantic_score,lexical_score,source_score,_,sentence,chunk in candidates:
        key=(chunk["id"],sentence)
        if key in seen:
            continue
        seen.add(key)
        selected.append({
            "text":sentence,
            "chunk_id":chunk["id"],
            "source":chunk.get("source"),
            "source_key":chunk.get("source_key"),
            "start_page":chunk.get("start_page"),
            "end_page":chunk.get("end_page"),
            "score":round(max(0.0,score),6),
            "semantic_score":round(semantic_score,6),
            "lexical_score":round(lexical_score,6),
            "source_relevance":round(source_score,6)
        })
        if len(selected)>=limit:
            break
    return selected


MEDUNITY_AUTH_URL = "https://medunity-api.dr-delyone.workers.dev"

async def medunity_admin_login(body):
    response = await fetch(
        MEDUNITY_AUTH_URL + "/login",
        method="POST",
        headers={"Content-Type": "application/json"},
        body=json.dumps({
            "nome_usuario": body.get("nome_usuario"),
            "senha": body.get("senha"),
        }),
    )
    data = await response.json()
    return response.status, data

async def medunity_me(request):
    authorization = request.headers.get("Authorization") or ""
    if not authorization.startswith("Bearer "):
        return 401, {"detail": "Autenticação necessária."}
    response = await fetch(
        MEDUNITY_AUTH_URL + "/me",
        method="GET",
        headers={"Authorization": authorization},
    )
    data = await response.json()
    if response.status >= 400:
        return response.status, data
    usuario = data.get("usuario") or {}
    if usuario.get("perfil") != "admin":
        return 403, {"detail": "Esta conta não possui acesso administrativo."}
    return 200, data

async def require_admin(request):
    status, data = await medunity_me(request)
    if status != 200:
        return None, status, data
    return data.get("usuario") or {}, 200, data

MAX_UPLOAD_BYTES = 100 * 1024 * 1024
ALLOWED_UPLOAD_TYPES = {"application/pdf"}
R2_BINDING = "AIGAR_LIBRARY_BUCKET"
D1_BINDING = "AIGAR_DB"

def binding(env, name):
    try:
        return getattr(env, name)
    except Exception:
        return None

def sanitize_filename(name):
    name = (name or "document.pdf").strip().replace("\\", "/").split("/")[-1]
    name = re.sub(r"[^A-Za-z0-9À-ÿ._ -]+", "_", name)
    name = re.sub(r"\\s+", " ", name).strip()
    if not name:
        name = "document.pdf"
    if not name.lower().endswith(".pdf"):
        name += ".pdf"
    return name[:180]

async def storage_status(env):
    bucket = binding(env, R2_BINDING)
    db = binding(env, D1_BINDING)
    return {
        "r2": bool(bucket),
        "d1": bool(db),
        "ready": bool(bucket and db),
        "bucket_binding": R2_BINDING,
        "database_binding": D1_BINDING,
    }

async def admin_upload(request, env, usuario):
    bucket = binding(env, R2_BINDING)
    db = binding(env, D1_BINDING)
    if not bucket or not db:
        return 503, {
            "ok": False,
            "status": "storage_not_configured",
            "message": "A persistência do AIGAR ainda não está vinculada ao Worker. Configure R2 e D1.",
            "storage": await storage_status(env),
        }

    content_type = (request.headers.get("Content-Type") or "").split(";")[0].lower()
    if content_type not in ALLOWED_UPLOAD_TYPES:
        return 415, {"ok": False, "status": "invalid_file_type", "message": "Apenas arquivos PDF são aceitos nesta primeira fase."}

    raw_length = request.headers.get("Content-Length")
    try:
        content_length = int(raw_length) if raw_length else None
    except Exception:
        content_length = None
    if content_length and content_length > MAX_UPLOAD_BYTES:
        return 413, {"ok": False, "status": "file_too_large", "message": "O limite desta primeira fase é 100 MB."}

    filename = sanitize_filename(request.headers.get("X-Filename"))
    client_sha = (request.headers.get("X-File-SHA256") or "").strip().lower()
    if client_sha and not re.fullmatch(r"[0-9a-f]{64}", client_sha):
        return 400, {"ok": False, "status": "invalid_checksum", "message": "X-File-SHA256 inválido."}

    if client_sha:
        duplicate = await db.prepare(
            "SELECT id, filename, status, r2_key FROM documents WHERE sha256 = ? LIMIT 1"
        ).bind(client_sha).first()
        if duplicate:
            return 200, {
                "ok": True,
                "status": "already_exists",
                "document": plain_document(duplicate),
            }

    seed = f"{client_sha}:{time.time_ns()}:{filename}".encode("utf-8")
    document_id = hashlib.sha256(seed).hexdigest()[:24]
    r2_key = f"documents/{document_id}/original.pdf"

    try:
        uploaded = await bucket.put(r2_key, request.body, {
            "httpMetadata": {"contentType": "application/pdf"},
            "customMetadata": {
                "original_filename": filename,
                "document_id": document_id,
                "uploaded_by": str(usuario.get("nome_usuario") or usuario.get("id") or "admin"),
            },
        })
    except Exception as exc:
        return 500, {"ok": False, "status": "r2_upload_error", "message": str(exc)}

    size_bytes = int(getattr(uploaded, "size", content_length or 0) or 0)
    now = int(time.time())

    try:
        await db.prepare(
            """INSERT INTO documents
               (id, filename, mime_type, size_bytes, sha256, r2_key, status,
                uploaded_at, uploaded_by, chunk_count)
               VALUES (?, ?, ?, ?, ?, ?, 'uploaded', ?, ?, 0)"""
        ).bind(
            document_id, filename, "application/pdf", size_bytes,
            client_sha or None, r2_key, now,
            str(usuario.get("nome_usuario") or usuario.get("id") or "admin"),
        ).run()
    except Exception as exc:
        try:
            await bucket.delete(r2_key)
        except Exception:
            pass
        return 500, {"ok": False, "status": "metadata_error", "message": str(exc)}

    workflow = binding(env, "AIGAR_LIBRARY_BUILDER")
    workflow_status = "not_configured"
    workflow_id = None
    if workflow:
        try:
            instance = await workflow.create(params={"document_id": document_id})
            workflow_status = "started"
            workflow_id = str(instance.id)
        except Exception as exc:
            workflow_status = "error"
            workflow_id = str(exc)[:500]

    return 201, {
        "ok": True,
        "status": "uploaded",
        "document": {
            "id": document_id,
            "filename": filename,
            "mime_type": "application/pdf",
            "size_bytes": size_bytes,
            "sha256": client_sha or None,
            "r2_key": r2_key,
            "status": "uploaded",
            "uploaded_at": now,
            "uploaded_by": str(usuario.get("nome_usuario") or usuario.get("id") or "admin"),
            "chunk_count": 0,
        },
        "next_step": "automatic_processing",
        "processing": {"status": workflow_status, "workflow_id": workflow_id},
    }

def plain_document(row):
    if not row:
        return None
    def scalar(name, default=None):
        try:
            value=getattr(row,name)
        except Exception:
            return default
        if value is None:
            return default
        return value
    return {
        "id": str(scalar("id","")),
        "filename": str(scalar("filename","")),
        "mime_type": str(scalar("mime_type","")),
        "size_bytes": int(scalar("size_bytes",0) or 0),
        "sha256": str(scalar("sha256")) if scalar("sha256") else None,
        "r2_key": str(scalar("r2_key","")),
        "status": str(scalar("status","")),
        "uploaded_at": int(scalar("uploaded_at",0) or 0),
        "uploaded_by": str(scalar("uploaded_by","")),
        "chunk_count": int(scalar("chunk_count",0) or 0),
        "error_message": str(scalar("error_message")) if scalar("error_message") else None,
    }



CHUNK_PAGES = 25
LIBRARY_R2_PREFIX = "libraries"

def normalize_library_text(text):
    text = (text or "").replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def markdown_pages(markdown):
    """Return [(page_number, text)] from Workers AI Markdown output."""
    raw = normalize_library_text(markdown)
    matches = list(re.finditer(r"(?m)^###\s+Page\s+(\d+)\s*$", raw))
    if not matches:
        return [(None, raw)] if raw else []
    pages = []
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(raw)
        body = normalize_library_text(raw[start:end])
        if body:
            pages.append((int(m.group(1)), body))
    return pages

def make_page_chunks(pages, pages_per_chunk=CHUNK_PAGES):
    if not pages:
        return []
    if pages[0][0] is None:
        text = pages[0][1]
        # TXT/Markdown-style fallback: preserve the document and split by ~24k chars.
        out = []
        for start in range(0, len(text), 24000):
            out.append((None, None, text[start:start + 24000]))
        return out
    out = []
    for i in range(0, len(pages), pages_per_chunk):
        group = pages[i:i + pages_per_chunk]
        out.append((group[0][0], group[-1][0], "\n\n".join(x[1] for x in group)))
    return out

async def convert_r2_pdf_to_markdown(env, r2_key, filename):
    bucket = binding(env, R2_BINDING)
    ai = binding(env, "AI")
    if not bucket:
        raise RuntimeError("R2 binding ausente.")
    if not ai:
        raise RuntimeError("Workers AI binding ausente.")
    obj = await bucket.get(r2_key)
    if not obj:
        raise RuntimeError("PDF não encontrado no R2.")
    data = await obj.arrayBuffer()
    # Workers AI's toMarkdown accepts a JS Blob. Python Workers expose JS objects
    # through the FFI, so we create the Blob without copying the PDF through D1.
    from js import Blob, Array, Uint8Array
    view = Uint8Array.new(data)
    parts = Array.new()
    parts.push(view)
    # Let Workers AI infer the document type from the .pdf filename.
    blob = Blob.new(parts)
    if int(getattr(blob, "size", 0) or 0) <= 0:
        raise RuntimeError("PDF recuperado do R2 resultou em Blob vazio.")
    from pyodide.ffi import create_proxy
    file_item = create_proxy({"name": filename, "blob": blob})
    files = Array.new()
    files.push(file_item)
    result = await ai.toMarkdown(files)
    items = result if isinstance(result, list) else list(result)
    if not items:
        raise RuntimeError("Workers AI não retornou conteúdo para o PDF.")
    item = items[0]
    fmt = str(item.get("format") or "")
    if fmt == "error":
        raise RuntimeError(str(item.get("error") or "Falha na conversão do PDF."))
    return str(item.get("data") or "")

async def build_document_library(env, document_id):
    db = binding(env, D1_BINDING)
    bucket = binding(env, R2_BINDING)
    if not db or not bucket:
        raise RuntimeError("Persistência do AIGAR não está configurada.")

    row = await db.prepare(
        "SELECT id, filename, r2_key, sha256, status FROM documents WHERE id = ? LIMIT 1"
    ).bind(document_id).first()
    if not row:
        raise RuntimeError("Documento não encontrado.")

    filename = str(row.filename or "document.pdf")
    r2_key = str(row.r2_key or "")
    await db.prepare(
        "UPDATE documents SET status = 'processing', error_message = NULL WHERE id = ?"
    ).bind(document_id).run()

    try:
        markdown = await convert_r2_pdf_to_markdown(env, r2_key, filename)
        pages = markdown_pages(markdown)
        chunks = make_page_chunks(pages, CHUNK_PAGES)
        if not chunks:
            raise RuntimeError("Nenhum texto recuperável foi encontrado no PDF.")

        source_digest = hashlib.sha256(markdown.encode("utf-8")).hexdigest()
        # Idempotency: remove old chunk metadata/artifacts before rebuilding.
        old = await db.prepare(
            "SELECT r2_key FROM document_chunks WHERE document_id = ?"
        ).bind(document_id).all()
        for old_row in old.results:
            try:
                await bucket.delete(str(old_row.r2_key))
            except Exception:
                pass
        await db.prepare("DELETE FROM document_chunks WHERE document_id = ?").bind(document_id).run()

        created = []
        for seq, (start_page, end_page, text) in enumerate(chunks, start=1):
            chunk_text = normalize_library_text(text)
            if not chunk_text:
                continue
            chunk_id = f"{document_id}_chunk_{seq:04d}"
            r2_chunk_key = f"{LIBRARY_R2_PREFIX}/{document_id}/chunks/chunk_{seq:04d}.md"
            header = (
                f"# {chunk_id}\n\n"
                f"**Biblioteca:** {filename}\n"
                f"**Fonte:** {filename}\n"
                + (f"**Páginas:** {start_page}-{end_page}\n" if start_page is not None else "")
                + f"**Checksum fonte:** {source_digest[:16]}\n\n---\n\n"
            )
            payload = (header + chunk_text + "\n").encode("utf-8")
            await bucket.put(
                r2_chunk_key,
                payload,
                {
                    "httpMetadata": {"contentType": "text/markdown; charset=utf-8"},
                    "customMetadata": {
                        "document_id": document_id,
                        "chunk_id": chunk_id,
                        "sequence": str(seq),
                        "source": filename,
                        "start_page": str(start_page or ""),
                        "end_page": str(end_page or ""),
                    },
                },
            )
            await db.prepare(
                """INSERT INTO document_chunks
                   (id, document_id, sequence, source, start_page, end_page,
                    r2_key, text_length, checksum, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
            ).bind(
                chunk_id, document_id, seq, filename, start_page, end_page,
                r2_chunk_key, len(chunk_text), source_digest, int(time.time())
            ).run()
            created.append({
                "id": chunk_id,
                "sequence": seq,
                "start_page": start_page,
                "end_page": end_page,
                "r2_key": r2_chunk_key,
                "text_length": len(chunk_text),
            })

        await db.prepare(
            "UPDATE documents SET status = 'ready', chunk_count = ?, error_message = NULL WHERE id = ?"
        ).bind(len(created), document_id).run()
        return {"document_id": document_id, "filename": filename, "chunk_count": len(created), "chunks": created}
    except Exception as exc:
        await db.prepare(
            "UPDATE documents SET status = 'error', error_message = ? WHERE id = ?"
        ).bind(str(exc)[:2000], document_id).run()
        raise

class LibraryBuilderWorkflow(WorkflowEntrypoint):
    async def run(self, event, step):
        # Workflow REST/API instances deliver params as the event payload.
        # Depending on the Python Workers version this can arrive as a dict
        # or as a JSON string, so normalize both forms here.
        payload = event
        # Python WorkflowEvent can expose payload through attributes or
        # JS-proxy indexing depending on the Workers runtime.
        candidates = []
        for attr in ("params", "payload"):
            try:
                candidates.append(getattr(event, attr, None))
            except Exception:
                pass
            try:
                candidates.append(event[attr])
            except Exception:
                pass
        for candidate in candidates:
            if candidate is not None:
                payload = candidate
                break
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except Exception:
                payload = {}
        if isinstance(payload, dict):
            if isinstance(payload.get("payload"), dict):
                payload = payload["payload"]
            if isinstance(payload.get("params"), str):
                try:
                    payload = json.loads(payload["params"])
                except Exception:
                    pass
        else:
            for key in ("payload", "params"):
                try:
                    nested = payload[key]
                    if isinstance(nested, str):
                        nested = json.loads(nested)
                    payload = nested
                    break
                except Exception:
                    pass
        if not isinstance(payload, dict):
            payload = {}
        document_id = str(payload.get("document_id") or "")
        if not document_id:
            raise RuntimeError("document_id ausente no Workflow.")
        @step.do("build-library", config={"retries": {"limit": 3, "delay": "10 seconds", "backoff": "exponential"}})
        async def build():
            result = await build_document_library(self.env, document_id)
            return {
                "document_id": result["document_id"],
                "filename": result["filename"],
                "chunk_count": result["chunk_count"],
            }
        return await build()

async def admin_documents(env):
    db = binding(env, D1_BINDING)
    if not db:
        return 503, {"ok": False, "status": "storage_not_configured", "storage": await storage_status(env)}
    result = await db.prepare(
        """SELECT id, filename, mime_type, size_bytes, sha256, r2_key,
                  status, uploaded_at, uploaded_by, chunk_count, error_message
           FROM documents ORDER BY uploaded_at DESC LIMIT 100"""
    ).run()
    documents=[]
    try:
        rows=result.results
        for row in rows:
            doc=plain_document(row)
            if doc:
                documents.append(doc)
    except Exception as exc:
        return 500, {
            "ok": False,
            "status": "documents_serialization_error",
            "message": str(exc),
        }
    return 200, {"ok": True, "documents": documents}

def cors_headers(origin=None):
    allowed=origin if origin in {"https://delyone.com","https://aigar-api.dr-delyone.workers.dev"} else "https://delyone.com"
    return {"Access-Control-Allow-Origin":allowed,"Access-Control-Allow-Methods":"GET,POST,OPTIONS","Access-Control-Allow-Headers":"Content-Type,Authorization","Vary":"Origin"}

def make_response(data,status=200,origin=None):
    h={"Content-Type":"application/json; charset=utf-8",**cors_headers(origin)}
    return Response(json.dumps(data,ensure_ascii=False),status=status,headers=h)

async def handle_ask(body):
    text=body.get("input")
    session_id=body.get("session_id") or "default"
    if not isinstance(text, str) or not text.strip():
        return 400, {"ok": False, "status": "invalid_input", "message": "O campo 'input' deve conter texto."}
    text = text.strip()
    if len(text) > 20000:
        return 413, {"ok": False, "status": "input_too_large", "message": "A entrada excede o limite de 20.000 caracteres."}
    session_id = str(session_id)[:128]
    session = SESSIONS.setdefault(session_id, {
        "session_id": session_id,
        "turns": [],
        "last_user_input": None,
        "last_response": None,
        "reading": None,
    })

    reading = LANGUAGE_ENGINE.interpret(text)
    prior_turns = session.get("turns", [])[-8:]
    memory_context = [
        {"role": turn.get("role"), "content": turn.get("content")}
        for turn in prior_turns
        if turn.get("content")
    ]
    if reading.get("needs_memory") and memory_context:
        reading["linguistic_analysis"]["recent_context_available"] = True
        reading["linguistic_analysis"]["recent_context_turns"] = len(memory_context)

    evidence_items = []
    library_trace = {
        "kind": "library",
        "id": "aigar.library",
        "status": "missing",
        "detail": "A biblioteca não foi consultada para esta intenção.",
    }
    if reading.get("needs_library"):
        try:
            evidence_items = await library_search(text, reading, limit=5)
            library_trace = {
                "kind": "library",
                "id": "aigar.library.hybrid",
                "status": "confirmed" if evidence_items else "missing",
                "detail": (
                    f"{len(evidence_items)} evidência(s) recuperada(s) no catálogo híbrido."
                    if evidence_items else
                    "Nenhuma evidência suficientemente relevante foi recuperada."
                ),
            }
        except Exception as exc:
            library_trace = {
                "kind": "library",
                "id": "aigar.library.hybrid",
                "status": "missing",
                "detail": "Falha na consulta da biblioteca: " + str(exc)[:400],
            }

    question = (reading.get("linguistic_analysis") or {}).get("question") or {}
    qtype = question.get("type")
    topic = question.get("topic_head") or question.get("topic_candidate") or reading.get("scope") or "esse assunto"
    evidence_texts = []
    for item in evidence_items:
        sentence = str(item.get("text") or "").strip()
        if sentence and sentence not in evidence_texts:
            evidence_texts.append(sentence)
        if len(evidence_texts) >= 3:
            break

    plan = {
        "understand_before_answer": True,
        "intent": reading.get("intent"),
        "depth": reading.get("depth"),
        "use_memory": bool(reading.get("needs_memory") and memory_context),
        "use_library": bool(reading.get("needs_library")),
        "use_diagnosis": bool(reading.get("needs_diagnosis")),
        "answer_mode": (
            "social" if reading.get("intent") == "phatic"
            else "source_grounded" if evidence_texts
            else "source_unavailable" if reading.get("needs_library")
            else "context_grounded" if memory_context and reading.get("needs_memory")
            else "reasoned_without_library"
        ),
        "question_type": qtype,
        "semantic_goal": question.get("semantic_goal"),
        "topic": topic,
        "evidence": evidence_texts,
        "evidence_details": evidence_items,
        "steps": [
            "interpret",
            "gather_available_context",
            "select_relevant_evidence",
            "reason",
            "plan_response",
        ],
    }

    mode = plan["answer_mode"]
    if mode == "social":
        answer = "Oi! Aurora aqui. Manda o que você quer construir que a gente organiza."
        aurora_detail = "Resposta social breve; consulta temática não necessária."
    elif mode == "source_grounded":
        book_answer = compose_book_grounded_answer(topic, qtype, reading.get("depth", "normal"), evidence_items)
        if book_answer:
            answer = book_answer
        else:
            prefix = {
                "definition": f"{str(topic).capitalize()} — pelo material recuperado na biblioteca:",
                "function": f"A função de {topic} — pelo material recuperado na biblioteca:",
                "cause": f"Sobre a causa de {topic} — pelo material recuperado na biblioteca:",
            }.get(qtype, f"Encontrei conteúdo relevante sobre {topic}:")
            answer = prefix + "\n\n" + " ".join(evidence_texts)
            answer += "\n\nEsta resposta apresenta os trechos mais relevantes recuperados; a síntese pode ser refinada em uma camada posterior."
        aurora_detail = "Resposta apresentada a partir de evidências selecionadas pelo mecanismo de busca."
    elif mode == "context_grounded":
        previous = session.get("last_user_input")
        previous_response = session.get("last_response")
        answer = "Vou continuar a partir do contexto recente."
        if previous:
            answer += f"\n\nSua mensagem anterior foi: {previous}"
        if previous_response:
            answer += f"\n\nMinha resposta anterior foi: {previous_response}"
        aurora_detail = "Resposta contextual baseada no histórico recente desta sessão."
    elif mode == "source_unavailable":
        answer = (
            f"Entendi a pergunta sobre {topic} e identifiquei que preciso consultar a biblioteca, "
            "mas não consegui recuperar evidência suficiente para responder com segurança. "
            "Isso não significa que a pergunta não tenha sentido; significa que a busca atual não encontrou suporte adequado."
        )
        aurora_detail = "A busca não encontrou evidência documental suficiente."
    else:
        answer = (
            "Entendi a solicitação e organizei sua intenção, mas não encontrei contexto ou evidência suficiente "
            "para dar uma resposta factual confiável. Se você delimitar o tema ou fornecer uma fonte, continuo a partir daí."
        )
        aurora_detail = "Resposta sem afirmações factuais não sustentadas por fonte ou contexto."

    sources = [
        {
            "kind": "language",
            "id": "aigar.language.mother",
            "status": "confirmed",
            "detail": "Entrada interpretada pela camada de Linguagem Materna executável.",
        },
        library_trace,
        {
            "kind": "memory",
            "id": "aigar.session_memory",
            "status": "confirmed" if memory_context and reading.get("needs_memory") else "missing",
            "detail": f"{len(memory_context)} turno(s) anterior(es) disponíveis nesta sessão."
            if memory_context and reading.get("needs_memory")
            else "Memória conversacional persistente entre instâncias não está configurada; contexto limitado à sessão do Worker.",
        },
        {
            "kind": "reasoning",
            "id": "aigar.reasoning",
            "status": "confirmed" if evidence_texts else "inferred",
            "detail": f"Plano organizado com {len(evidence_texts)} evidência(s).",
        },
        {
            "kind": "aurora",
            "id": "aigar.aurora",
            "status": "confirmed",
            "detail": aurora_detail,
        },
    ]

    confirmed = sum(1 for source in sources if source.get("status") == "confirmed")
    confidence = min(0.85, max(0.15, float(reading.get("confidence", 0.45)) * 0.5 + confirmed * 0.07))
    if reading.get("needs_library") and not evidence_items:
        confidence = min(confidence, 0.35)

    turn = {"role": "user", "content": text}
    session["turns"].append(turn)
    session["turns"].append({"role": "assistant", "content": answer})
    session["turns"] = session["turns"][-20:]
    session["last_user_input"] = text
    session["last_response"] = answer
    session["reading"] = reading

    library_payload = {
        "chunks_loaded": len(evidence_items),
        "chunks": [
            {
                "id": item.get("chunk_id"),
                "source": item.get("source"),
                "source_key": item.get("source_key"),
                "start_page": item.get("start_page"),
                "end_page": item.get("end_page"),
                "score": item.get("score"),
                "semantic_score": item.get("semantic_score"),
                "lexical_score": item.get("lexical_score"),
                "source_relevance": item.get("source_relevance"),
            }
            for item in evidence_items
        ],
    }
    return 200, {
        "ok": True,
        "text": answer,
        "state": {
            "session_id": session_id,
            "turns": session["turns"],
            "last_user_input": session["last_user_input"],
            "last_response": session["last_response"],
            "reading": reading,
        },
        "sources": sources,
        "confidence": round(confidence, 4),
        "plan": plan,
        "library": library_payload,
    }


# --- HTTP entry point: keeps the deployed Worker and frontend contract aligned. ---

def cors_headers(origin=None):
    allowed_origins = {
        "https://delyone.com",
        "https://www.delyone.com",
        "https://aigar-api.dr-delyone.workers.dev",
    }
    allowed = origin if origin in allowed_origins else "https://delyone.com"
    return {
        "Access-Control-Allow-Origin": allowed,
        "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Filename,X-File-SHA256",
        "Access-Control-Max-Age": "86400",
        "Vary": "Origin",
    }


def make_response(data, status=200, origin=None):
    headers = {"Content-Type": "application/json; charset=utf-8", **cors_headers(origin)}
    return Response(json.dumps(data, ensure_ascii=False), status=status, headers=headers)


def _request_origin(request):
    try:
        return request.headers.get("Origin")
    except Exception:
        return None


async def _json_body(request):
    try:
        body = await request.json()
        return body if isinstance(body, dict) else {}
    except Exception:
        return {}


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        method = str(request.method or "GET").upper()
        parsed = urlparse(str(request.url))
        path = parsed.path.rstrip("/") or "/"

        # Normaliza o prefixo da rota do domínio oficial.
        if path == "/aigar/api":
            path = "/"
        elif path.startswith("/aigar/api/"):
            path = path[len("/aigar/api"):]

        origin = _request_origin(request)

        if method == "OPTIONS":
            return Response(None, status=204, headers=cors_headers(origin))

        if method == "GET" and path == "/health":
            r2_ready = binding(self.env, R2_BINDING) is not None
            d1_ready = binding(self.env, D1_BINDING) is not None
            storage_ready = r2_ready and d1_ready
            return make_response({
                "ok": True,
                "service": "aigar-api",
                "runtime": "AIGAR",
                "version": "0.7.0-cloudflare",
                "status": "online",
                "backend": "python_workers",
                "checks": {
                    "api": "ok",
                    "r2_binding": r2_ready,
                    "d1_binding": d1_ready,
                    "persistent_storage_configured": storage_ready,
                },
                "features": {
                    "language": True,
                    "hybrid_library_search": True,
                    "session_memory": True,
                    "persistent_library_upload": True,
                    "persistent_storage_ready": storage_ready,
                },
            }, origin=origin)

        if method == "GET" and path == "/library/boot":
            try:
                boot = await boot_library()
                return make_response({
                    "ok": True,
                    "library": boot,
                }, status=200 if boot.get("loaded", 0) > 0 else 503, origin=origin)
            except Exception as exc:
                return make_response({
                    "ok": False,
                    "library": {
                        "ready": False,
                        "libraries": [],
                        "loaded": 0,
                        "total": 0,
                        "mode": "error",
                    },
                    "message": str(exc)[:1000],
                }, status=500, origin=origin)

        if method == "POST" and path == "/perguntar":
            body = await _json_body(request)
            status, data = await handle_ask(body)
            return make_response(data, status=status, origin=origin)

        if method == "POST" and path == "/auth/login":
            body = await _json_body(request)
            try:
                status, data = await medunity_admin_login(body)
                return make_response(data, status=status, origin=origin)
            except Exception as exc:
                return make_response({
                    "detail": "Não foi possível validar as credenciais no MedUnity.",
                    "error": str(exc)[:500],
                }, status=502, origin=origin)

        if path == "/auth/me" and method == "GET":
            status, data = await medunity_me(request)
            return make_response(data, status=status, origin=origin)

        if path.startswith("/admin/"):
            usuario, auth_status, auth_data = await require_admin(request)
            if not usuario:
                return make_response(auth_data, status=auth_status, origin=origin)

            if path == "/admin/storage" and method == "GET":
                storage = await storage_status(self.env)
                return make_response({
                    "ok": True,
                    "ready": storage["ready"],
                    "storage": storage,
                }, status=200, origin=origin)

            if path == "/admin/documents" and method == "GET":
                status, data = await admin_documents(self.env)
                return make_response(data, status=status, origin=origin)

            if path == "/admin/upload" and method == "POST":
                status, data = await admin_upload(request, self.env, usuario)
                return make_response(data, status=status, origin=origin)

            return make_response({
                "ok": False,
                "status": "not_found",
                "message": "Endpoint administrativo não encontrado.",
            }, status=404, origin=origin)

        return make_response({
            "ok": False,
            "status": "not_found",
            "message": "Endpoint não encontrado.",
            "path": path,
        }, status=404, origin=origin)
