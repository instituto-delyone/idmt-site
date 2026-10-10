# Memory — estado de implementação

**Estado:** parcialmente implementado para estado de trabalho e continuidade da sessão; memória persistente não conectada.

## Componentes existentes
- `working_memory.py`: `WorkingStateStore`, armazena estado de sessão no processo e limita o histórico a 40 entradas.
- `hippocampal_memory.py`: `HippocampalMemoryAdapter`, retorna turnos recentes através de `MemoryRecallRequest` e `MemoryRecallResult`.
- Contratos canônicos em `CORTEX/thalamus/models.py`.

## Limites conhecidos
- O estado atual não é persistido após reinício do processo.
- A recuperação do Memory Card e a memória de longo prazo ainda não estão conectadas.
- A analogia com o hipocampo é funcional e não uma equivalência neuroanatômica literal.

Não apagar ou substituir artefatos históricos até identificar seus consumidores. Testes permanecem adiados até a conclusão das movimentações e da atualização de referências.
