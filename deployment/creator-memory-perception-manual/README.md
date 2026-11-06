# Patch manual — Creator Memory Perception

Este pacote é uma atualização focada para o Worker ativo `aigar-api`, baseada no `main.py` extraído do Worker ativo (versão 68) e não no `main.py` mais amplo do pacote de migração.

## Arquivos
- `main.py`: código ativo preservado, com import e rota `POST /admin/creator-memory/perceive` adicionados.
- `creator_memory_perception.py`: módulo da percepção longitudinal, preservando os registros originais em R2 e gravando apenas o artefato derivado.

## D1
A tabela `creator_memory_perceptions` e o índice `idx_creator_memory_perceptions_owner` já foram criados de forma aditiva no banco AIGAR. Nenhuma tabela ou registro existente foi apagado.

## Atenção ao deploy
Não publique apenas o `main.py`: adicione também `creator_memory_perception.py` como módulo Python no mesmo Worker. Preserve as bindings atuais: `AI`, `AIGAR_DB`, `AIGAR_LIBRARY_BUCKET`, `AIGAR_LIBRARY_BUILDER` e o secret `Uei`. Não crie um valor novo para `Uei`.

O Worker deve continuar com compatibilidade `2026-10-08` e flags `python_workers`, `python_workflows`, `disable_python_external_sdk`.

## Teste pós-deploy
1. Confirme que o Worker responde normalmente.
2. Faça login administrativo.
3. Envie `POST /admin/creator-memory/perceive` com `include_creator_memory: true` e, opcionalmente, uma pergunta.
4. Confirme que a resposta informa os registros utilizados e a gravação da percepção.
5. Verifique em D1 a nova linha em `creator_memory_perceptions`.

Este pacote não altera rotas, DNS, Workflow ou bindings do Worker.
