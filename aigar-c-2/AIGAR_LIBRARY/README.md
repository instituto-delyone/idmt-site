# AIGAR Library

Camada de conhecimento documental do AIGAR. O índice e o cache são separados: o índice guarda IDs, ordem, páginas e checksums; o texto processado fica no cache local e não é versionado por padrão.

Fluxo: fonte -> Builder -> chunks -> IDs -> cache local -> índice -> Retriever -> AIGAR Runtime.

O AIGAR carrega somente os chunks necessários. A biblioteca não substitui Linguagem Materna, Reasoning, Memory ou Diagnosis.
