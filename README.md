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

