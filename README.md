https://www.delyone.com

Are you a physician? that link is for you

future csi classifications
Doenças / diagnósticos
Síndromes
Sintomas
Sinais
Exames
Achados
Terapêuticas
Medicamentos
Procedimentos
Curativos
Assistência
Regulação
Leitos
Fluxos
Especialidades
Documentação médica
Educação médica
Pesquisa

O CSI não precisa ser uma aplicação. Ele pode ser uma infraestrutura semântica sobre a qual aplicações médicas inteiras podem ser construídas.

exemplos

Dispneia
   │
   ├── é sintoma de → insuficiência cardíaca
   ├── é sintoma de → pneumonia
   ├── pode estar associada a → hipoxemia
   └── pode exigir → oximetria

   possible api concepts (extremely simplified)
   CSI Clinical API
Consulta conceitos médicos.
GET /concepts/dispneia

CSI Diagnosis API
Relaciona achados, sintomas, síndromes e diagnósticos.
POST /diagnostic-relations

CSI Regulation API
Usa conceitos para estruturar regulação.
POST /regulation/request

CSI Bed API
Estrutura necessidade → perfil → leito.
POST /bed-matching

CSI Care API
Representa assistência e cuidados.
POST /care-plan

CSI Procedure API
Procedimentos e intervenções.
GET /procedures


isso me gera

                    CSI
                     │
          ┌──────────┼──────────┐
          │          │          │
      Diagnosis   MedUnity   Regulação
          │          │          │
          └──────────┼──────────┘
                     │
                 aplicações



                 principal e mais importante aplicação

internacionalização e universalização da medicina
enfrentamento a pandemias
unificação de interpretação de achados de pesquisa
padronização da bioestatistica retirada de casos clinicos
modelos de previsão biológica centenas de vezes mais poderosos

o metodo de implantação deve ser protegido e não ser gravado em unidades de memoria. memorizado via repetição visual. segredo: 100% guardado

exemplo simples de implantação caso eu não leve o projeto adiante

csi - unifica achados e procedimentos
forms mesmo personalizados podem usar tags csi em campos para posterior padronização
banco de dados epidemiologico atualizado em tempo real pode ser criado facilmente devido ao csi
comunicação global
qualquer surto ou discrepancia de incidencia ou mudança importante em padroes epidemiologicos
alerta imediato
inicio de esforços de diagnostico controle prevenção e cura de endemias, epidemias surtos regionais, pandemias e erros humanos ou de maquinas perfeitamente auditaveis. (isso é o plano o qual ja esta estruturado porem não documentado)

CURRENT
CSI semantic infrastructure

FUTURE / VISION
International interoperability
Epidemiological standardization
Research harmonization
Clinical-data normalization
Pandemic/surveillance applications
Predictive biological models

limitations: human capital. no investments. the disease outbreaks have a repeated pattern,but with suficient time to the humanity completely forget they will happen. this is the cause of: no invesments at all
