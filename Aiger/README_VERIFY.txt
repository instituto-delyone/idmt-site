MC-BASE AIGAR 1.0 — Verificação de Integridade e Autoria

Arquivos:
- MC-BASE-AIGAR-1.0.yaml
- MC-BASE-AIGAR-1.0.payload.json
- MC-BASE-AIGAR-1.0.CHECKSUMS.txt

O que é o que?
- O YAML é o cartucho principal (legível).
- O payload.json é a base canônica para verificação (JSON com chaves ordenadas, minificado, NFC).
- O CHECKSUMS.txt contém os hashes/assinaturas para conferência.

1) Verificar SHA-256 e SHA3-256 do payload
   macOS / Linux:
     shasum -a 256 MC-BASE-AIGAR-1.0.payload.json
     openssl dgst -sha3-256 MC-BASE-AIGAR-1.0.payload.json
   Windows PowerShell:
     Get-FileHash MC-BASE-AIGAR-1.0.payload.json -Algorithm SHA256
     (Get-Content MC-BASE-AIGAR-1.0.payload.json -Encoding Byte | `
        Measure-Object -Sum).Sum | Out-Null  # use OpenSSL para SHA3-256

   Compare com os valores no YAML (em memory_card.proof.sha256 e sha3_256)
   ou no arquivo MC-BASE-AIGAR-1.0.CHECKSUMS.txt.

2) Verificar HMAC (autenticidade vinculada ao autor)
   A chave é derivada por PBKDF2-HMAC-SHA256 usando:
     - password: CPF do autor (como fornecido no YAML)
     - salt   : '1997-09-13|FG404392' (data de nascimento | passaporte)
     - iterações: 200000, dklen=32

   Exemplo rápido em Python:
     import hashlib, hmac, json, unicodedata
     cpf = "05366600189".encode("utf-8")
     salt = "1997-09-13|FG404392".encode("utf-8")
     key = hashlib.pbkdf2_hmac("sha256", cpf, salt, 200000, dklen=32)
     data = open("MC-BASE-AIGAR-1.0.payload.json","rb").read()
     mac = hmac.new(key, data, hashlib.sha256).hexdigest()
     print(mac)  # deve coincidir com memory_card.proof.hmac_sha256

Observações importantes
- O HMAC acima serve como amarração público-identitária (integridade + autoria
  atrelada ao CPF informado). Por conter dados pessoais no próprio documento,
  NÃO é um segredo; use como prova de não adulteração e vínculo autoral.
- Para prova pública de existência (timestamp), publique os hashes (sha256/sha3_256)
  em um post seu (ex.: Threads/LinkedIn) com a data de publicação.

Doc ID: urn:aigar:mc:base:aigar:1.0:6b02ae2b9be7bded
Criado (local): 2025-08-27T11:37:10.779897-03:00
Criado (UTC)  : 2025-08-27T14:37:10.779897Z
