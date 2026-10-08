from __future__ import annotations

import asyncio
import json
import re
from workers import WorkerEntrypoint, Response, fetch

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

    def verbs(self, words):
        lexicon={"é","são","foi","foram","ser","sendo","era","eram","está","estão","estava","estavam","ficou","ficaram","tem","têm","teve","tiveram","ter","faz","fazem","fez","fizeram","fazer","pode","podem","podia","podiam","poder","deve","devem","deveria","deveriam","dever","vai","vão","aconteceu","acontecer","chegou","chegaram","chegar","explica","explicar","explique","defina","define","significa","significar","funciona","funcionar","serve","servir","quer","querem","quero","precisa","precisam","crie","criar","faça","fazer","monte","montar","calcule","calcular","gere","gerar","compare","comparar","analise","analisar","responda","responder","continue","continua","entendi","entender","sabe","saber"}
        return [w for w in words if w in lexicon]

    def question(self,text):
        patterns=self.portuguese["question_patterns"]
        ordered=[("definition",patterns["definition"]["forms"]),("identity",patterns["identity"]["forms"]),("time",patterns["time"]["forms"]),("place",patterns["place"]["forms"]),("cause",patterns["cause"]["forms"]),("function",patterns["function"]["forms"]),("process",patterns["process"]["forms"]),("comparison",patterns["comparison"]["forms"])]
        for qtype,forms in ordered:
            for form in sorted(forms,key=len,reverse=True):
                if form in text:
                    remainder=text.replace(form,"",1).strip(" ?")
                    return {"type":qtype,"matched_form":form,"semantic_goal":patterns[qtype]["semantic_goal"],"topic_candidate":remainder or None}
        return {"type":None,"matched_form":None,"semantic_goal":None,"topic_candidate":None}

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
        if self.has_any(text,rules["phatic"]["examples"]): intent,confidence="phatic",0.98
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

def chunk_url(entry):
    name=entry["cache_file"].replace("\\","/")
    prefix="aigar-c-2/AIGAR_LIBRARY/cache/"
    return "https://raw.githubusercontent.com/instituto-delyone/idmt-site/main/"+prefix+name.split("portuguese_language_knowledge/")[-1]

async def load_chunks():
    async def one(entry):
        cid=entry["id"]
        if cid not in CHUNK_CACHE:
            try:
                r=await fetch(chunk_url(entry))
                if r.status>=400: return None
                CHUNK_CACHE[cid]=await r.text()
            except Exception: return None
        return {**entry,"text":CHUNK_CACHE.get(cid,"")}
    result=await asyncio.gather(*(one(e) for e in LIBRARY_INDEX.get("chunks",[])))
    return [x for x in result if x and x.get("text")]

async def library_search(query,reading,limit=5):
    chunks=await load_chunks()
    q=tokens(reading.get("scope") or query)
    if not q: q=tokens(query)
    qtype=reading.get("linguistic_analysis",{}).get("question",{}).get("type")
    candidates=[]
    for chunk in chunks:
        for sentence in sentences(chunk["text"]):
            st=tokens(sentence); overlap=len(q&st)
            if not overlap: continue
            score=overlap/max(1,len(q))
            exact=1.0 if (reading.get("scope") and reading["scope"].lower() in sentence.lower()) else 0.0
            definition=0.0
            if qtype=="definition":
                lower=sentence.lower()
                topic=(reading.get("scope") or "").lower()
                if topic and re.search(rf"\b{re.escape(topic)}\b\s+(é|são|significa|consiste|refere-se)",lower): definition=2.0
                elif any(m in lower for m in ["é uma","é um","são","significa"]): definition=0.35
            candidates.append((score+exact+definition,float(chunk.get("sequence",0)),sentence,chunk))
    candidates.sort(key=lambda x:(-x[0],x[1],len(x[2])))
    selected=[]; seen=set()
    for score,_,sentence,chunk in candidates:
        if sentence in seen: continue
        seen.add(sentence)
        selected.append({"text":sentence,"chunk_id":chunk["id"],"source":chunk.get("source"),"start_page":chunk.get("start_page"),"end_page":chunk.get("end_page"),"score":round(score,6)})
        if len(selected)>=limit: break
    return selected

MEDUNITY_AUTH_URL = "https://medunity-api.dr-delyone.workers.dev"

async def medunity_admin_login(body):
    response = await fetch(MEDUNITY_AUTH_URL + "/admin/login", {
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "nome_usuario": body.get("nome_usuario"),
            "senha": body.get("senha"),
        }),
    })
    data = await response.json()
    return response.status, data

async def medunity_me(request):
    authorization = request.headers.get("Authorization") or ""
    if not authorization.startswith("Bearer "):
        return 401, {"detail": "Autenticação necessária."}
    response = await fetch(MEDUNITY_AUTH_URL + "/me", {
        "method": "GET",
        "headers": {"Authorization": authorization},
    })
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

def cors_headers(origin=None):
    allowed=origin if origin in {"https://delyone.com","https://aigar-api.dr-delyone.workers.dev"} else "https://delyone.com"
    return {"Access-Control-Allow-Origin":allowed,"Access-Control-Allow-Methods":"GET,POST,OPTIONS","Access-Control-Allow-Headers":"Content-Type,Authorization","Vary":"Origin"}

def make_response(data,status=200,origin=None):
    h={"Content-Type":"application/json; charset=utf-8",**cors_headers(origin)}
    return Response(json.dumps(data,ensure_ascii=False),status=status,headers=h)

async def handle_ask(body):
    text=body.get("input")
    session_id=body.get("session_id") or "default"
    if not isinstance(text,str) or not text.strip():
        return {"error":"input obrigatório"}
    state=SESSIONS.setdefault(session_id,{"session_id":session_id,"turns":[],"last_user_input":None,"last_response":None,"reading":{}})
    reading=LANGUAGE_ENGINE.interpret(text)
    state["reading"]=reading
    memory=state["turns"][-8:] if (reading["needs_memory"] or reading["intent"]=="continuity") else []
    sources=[]
    if memory:
        sources.append({"kind":"memory","id":"runtime.recent_context","status":"inferred","detail":"Session-local continuity."})
    evidence=await library_search(text,reading) if reading["needs_library"] else []
    if reading["needs_library"]:
        sources.append({"kind":"library","id":"github.versioned.library","status":"confirmed" if evidence else "missing","detail":f"{len(evidence)} evidência(s) recuperada(s) da biblioteca versionada."})
    mode="social" if reading["intent"]=="phatic" else ("source_grounded" if evidence else ("source_unavailable" if reading["needs_library"] else "reasoned_without_library"))
    topic=(reading.get("scope") or "esse assunto").strip(" ?")
    if mode=="social":
        answer="Oi! Aurora aqui. Manda o que você quer construir que a gente organiza."
    elif mode=="source_grounded":
        qtype=reading["linguistic_analysis"].get("question",{}).get("type")
        prefix=f"{topic.capitalize()} — pelo material recuperado:" if qtype=="definition" else f"Encontrei conteúdo relevante sobre {topic}:"
        answer=prefix+"\n\n"+" ".join(e["text"] for e in evidence[:3])
    elif mode=="source_unavailable":
        answer=f"Entendi a pergunta sobre {topic}. A biblioteca está conectada, mas não encontrei evidência local suficiente para responder com segurança."
    elif mode=="reasoned_without_library":
        answer="Entendi a solicitação e organizei a intenção, mas não vou inventar conteúdo que não foi fundamentado."
    else:
        last=memory[-1]["content"] if memory else None
        answer="Vou continuar a partir do contexto recente."+ (f" O ponto anterior foi: {last}" if last else "")
    plan={"understand_before_answer":True,"intent":reading["intent"],"depth":reading["depth"],"use_memory":bool(memory),"use_library":reading["needs_library"],"use_diagnosis":False,"answer_mode":mode,"question_type":reading["linguistic_analysis"].get("question",{}).get("type"),"semantic_goal":reading["linguistic_analysis"].get("question",{}).get("semantic_goal"),"topic":reading.get("scope"),"evidence":[e["text"] for e in evidence],"steps":["interpret","gather_available_context","select_relevant_evidence","reason","plan_response"]}
    sources += [{"kind":"reasoning","id":"runtime.reasoning","status":"confirmed" if evidence else "inferred","detail":f"Resposta planejada em modo {mode}."},{"kind":"aurora","id":"runtime.aurora","status":"confirmed","detail":"Apresentação final no Runtime Cloudflare."}]
    state["last_user_input"]=text; state["last_response"]=answer
    state["turns"] += [{"role":"user","content":text},{"role":"assistant","content":answer}]
    if len(state["turns"])>40: state["turns"]=state["turns"][-40:]
    confidence=min(0.75,0.35+0.1*sum(1 for s in sources if s["status"] in {"confirmed","inferred"}))
    return {"text":answer,"state":state,"sources":sources,"confidence":confidence,"plan":plan}

class Default(WorkerEntrypoint):
    async def fetch(self, request):
        origin=request.headers.get("Origin")
        path=request.url.split("?",1)[0].rstrip("/")
        if request.method=="OPTIONS":
            return Response("",status=204,headers=cors_headers(origin))
        if path.endswith("/health") and request.method=="GET":
            return make_response({"ok":True,"service":"aigar-api","runtime":"AIGAR","version":"0.4.0-cloudflare","status":"production_runtime","backend":"python_workers","admin_auth":"medunity_delegated"},origin=origin)
        if path.endswith("/auth/login") and request.method=="POST":
            try:
                body=await request.json()
                status, data = await medunity_admin_login(body)
                return make_response(data, status, origin)
            except Exception as exc:
                return make_response({"ok":False,"status":"auth_proxy_error","message":str(exc)},502,origin)
        if path.endswith("/auth/me") and request.method=="GET":
            try:
                _, status, data = await require_admin(request)
                return make_response(data, status, origin)
            except Exception as exc:
                return make_response({"ok":False,"status":"auth_validation_error","message":str(exc)},502,origin)
        if path.endswith("/perguntar") and request.method=="POST":
            try:
                body=await request.json()
                result=await handle_ask(body)
                if "error" in result: return make_response(result,400,origin)
                return make_response(result,200,origin)
            except Exception as exc:
                return make_response({"ok":False,"service":"aigar-api","status":"runtime_error","message":str(exc)},500,origin)
        return make_response({"ok":False,"service":"aigar-api","status":"not_found"},404,origin)
