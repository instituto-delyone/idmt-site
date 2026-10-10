# Sensory — estado de implementação

**Estado:** implementado parcialmente como fronteira de entrada textual.

## Componente existente
- `ingress.py`: `capture_request()` converte `RuntimeRequest` em `SensoryInput`, preservando texto e identificador de sessão. Não normaliza nem classifica a entrada.

## Ainda não implementado
- Classificação sensorial multimodal.
- Adaptadores dedicados para imagem, áudio ou outras modalidades.
- Processamento sensorial além do envelope de entrada textual.

A presença de `SensoryInput` não deve ser interpretada como suporte multimodal já funcional.
