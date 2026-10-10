## id: AIGAR\-TM\-08 title: “Dicionário de tradução entre comandos computacionais e linguagem humana” collection: “Texto\-Matriz AIGAR” chapter: 8 version: “0\.1” status: “rascunho didático” language: “pt\-BR” type: “catálogo de exemplos comentados”

# Capítulo 08 — Dicionário de tradução entre comandos computacionais e linguagem humana

## 1\. Objetivo

Este documento reúne exemplos variados de comandos, trechos de código e expressões técnicas, traduzindo\-os para o português cotidiano\. A intenção é ajudar o AIGAR a relacionar **a forma escrita de uma instrução** com **a ação que ela solicita**, sem confundir tradução literal com explicação funcional\.

Cada exemplo pode ter até quatro camadas:

1. **Código ou comando:** como aparece na linguagem técnica\.
2. **Tradução simples:** como uma pessoa explicaria a instrução em português\.
3. **Interpretação funcional:** o que o sistema tende a fazer\.
4. **Observação:** condições, limites ou detalhes que mudam o significado\.

> Importante: comandos dependem da linguagem, da biblioteca, do ambiente e do contexto. Um trecho isolado nem sempre pode ser executado. As traduções deste capítulo explicam o sentido pretendido, não garantem que o código funcione em qualquer sistema.

## 2\. Verbos fundamentais de programação

|Palavra ou operador  |Tradução humana aproximada                                   |Exemplo                                                                      |
|---------------------|-------------------------------------------------------------|-----------------------------------------------------------------------------|
|`get`                |obter, buscar ou ler                                         |`get_user()` — obter os dados de um usuário                                  |
|`set`                |definir ou atribuir                                          |`set_name("Ana")` — definir o nome como Ana                                  |
|`add`                |adicionar ou somar                                           |`add(2, 3)` — somar dois e três, dependendo da função                        |
|`remove`             |remover                                                      |`remove(item)` — retirar um item                                             |
|`delete`             |apagar ou excluir                                            |`delete_file()` — excluir um arquivo                                         |
|`create`             |criar                                                        |`create_user()` — criar um usuário                                           |
|`update`             |atualizar                                                    |`update_record()` — atualizar um registro                                    |
|`fetch`              |buscar ou solicitar dados                                    |`fetch(url)` — fazer uma solicitação a um endereço                           |
|`send`               |enviar                                                       |`send(message)` — enviar uma mensagem                                        |
|`read`               |ler                                                          |`read(file)` — ler o conteúdo de um arquivo                                  |
|`write`              |escrever ou gravar                                           |`write(data)` — gravar dados                                                 |
|`load`               |carregar para uso                                            |`load_model()` — carregar um modelo                                          |
|`save`               |salvar                                                       |`save(result)` — salvar um resultado                                         |
|`run`                |executar                                                     |`run_task()` — executar uma tarefa                                           |
|`return`             |devolver como resultado                                      |`return value` — devolver o valor                                            |
|`print`              |mostrar na saída                                             |`print("Olá")` — mostrar “Olá”                                               |
|`parse`              |analisar e converter uma estrutura                           |`parse_json(text)` — interpretar texto como JSON                             |
|`validate`           |verificar se atende a regras                                 |`validate(data)` — verificar se os dados são válidos                         |
|`filter`             |selecionar os que atendem a uma condição                     |`filter(active)` — manter os itens ativos, conforme a operação               |
|`map`                |transformar cada elemento de uma coleção                     |`map(transform, items)` — aplicar uma transformação a cada item              |
|`sort`               |ordenar                                                      |`sort(items)` — colocar itens em uma ordem                                   |
|`find`               |encontrar                                                    |`find_user(id)` — procurar um usuário pelo identificador                     |
|`search`             |pesquisar                                                    |`search("febre")` — pesquisar o termo “febre”                                |
|`check`              |verificar                                                    |`check_status()` — verificar o estado                                        |
|`compare`            |comparar                                                     |`compare(a, b)` — comparar A e B                                             |
|`await`              |esperar a conclusão de uma operação assíncrona               |`await fetch(url)` — aguardar a resposta da solicitação                      |
|`async`              |declarar uma função assíncrona                               |`async function f()` — definir uma função que pode usar operações assíncronas|
|`try`                |tentar executar um bloco que pode falhar                     |`try: ...` — tentar realizar uma operação                                    |
|`except` / `catch`   |tratar uma falha capturada                                   |`except Error:` — executar tratamento se ocorrer o erro correspondente       |
|`if`                 |se                                                           |`if x > 0` — se X for maior que zero                                         |
|`else`               |caso contrário                                               |`else` — executar a alternativa                                              |
|`for`                |para cada elemento / repetir                                 |`for item in items` — para cada item da lista                                |
|`while`              |enquanto uma condição for verdadeira                         |`while active` — repetir enquanto estiver ativo                              |
|`break`              |interromper o laço atual                                     |`break` — parar a repetição                                                  |
|`continue`           |passar para a próxima repetição                              |`continue` — pular o restante desta iteração                                 |
|`import`             |importar ou disponibilizar um módulo                         |`import math` — disponibilizar as funções matemáticas do módulo              |
|`from ... import ...`|importar algo específico de um módulo                        |`from pathlib import Path` — importar `Path` do módulo `pathlib`             |
|`as`                 |dar um nome alternativo                                      |`import numpy as np` — importar NumPy usando o apelido `np`                  |
|`def`                |definir uma função                                           |`def soma(a, b):` — criar uma função chamada soma                            |
|`class`              |definir uma classe                                           |`class Pessoa:` — definir uma estrutura chamada Pessoa                       |
|`return`             |encerrar a função devolvendo um resultado                    |`return total` — devolver o total calculado                                  |
|`raise`              |lançar um erro deliberadamente                               |`raise ValueError()` — sinalizar um erro desse tipo                          |
|`null` / `None`      |ausência de um valor definido                                |`x = None` — indicar que X não contém um valor definido                      |
|`true` / `True`      |verdadeiro                                                   |`active = True` — marcar como verdadeiro                                     |
|`false` / `False`    |falso                                                        |`active = False` — marcar como falso                                         |
|`==`                 |é igual a?                                                   |`x == 5` — verificar se X é igual a cinco                                    |
|`!=`                 |é diferente de?                                              |`x != 5` — verificar se X é diferente de cinco                               |
|`>` / `<`            |maior que / menor que                                        |`x > 5` — verificar se X é maior que cinco                                   |
|`>=` / `<=`          |maior ou igual / menor ou igual                              |`x >= 5` — verificar se X é pelo menos cinco                                 |
|`=`                  |atribuir um valor                                            |`x = 5` — guardar o valor cinco em X                                         |
|`+=`                 |atualizar somando ao valor atual                             |`x += 1` — aumentar X em um                                                  |
|`and` / `&&`         |e lógico                                                     |`a and b` — ambas as condições precisam ser verdadeiras                      |
|`or` / `                                                                          ||`                                                                            |
|`not` / `!`          |negar uma condição                                           |`not active` — verificar a negação de ativo                                  |
|`.`                  |acessar um membro ou propriedade                             |`user.name` — acessar o nome do usuário                                      |
|`[]`                 |acessar um item ou declarar uma coleção, conforme o contexto |`items[0]` — acessar o primeiro item em linguagens de índice zero            |
|`()`                 |chamar uma função ou agrupar uma expressão                   |`save(data)` — chamar a função `save` com `data`                             |
|`{}`                 |bloco, objeto, conjunto ou interpolação, conforme a linguagem|`{"name": "Ana"}` — objeto com um campo chamado `name` em JSON               |
|`#` ou `//`          |comentário em linguagens que usam esse marcador              |`# nota` — texto explicativo não executado como instrução em Python          |

## 3\. Exemplos em Python

### Exemplo 1 — Mostrar uma mensagem

```python
print("Olá, mundo!")
```

**Em português:** “Mostre na saída a frase ‘Olá, mundo\!’\.”

**Função:** exibe texto\. Não cria uma conversa nem envia uma mensagem pela internet\.

### Exemplo 2 — Guardar um valor

```python
nome = "Ana"
```

**Em português:** “Guarde o texto ‘Ana’ na variável chamada `nome`\.”

**Função:** associa um nome a um valor durante a execução\. Não significa, por si só, salvar esse valor permanentemente em um arquivo ou banco de dados\.

### Exemplo 3 — Somar dois números

```python
total = 10 + 5
```

**Em português:** “Some dez e cinco e guarde o resultado em `total`\.”

**Resultado:** `total` passa a valer `15`\.

### Exemplo 4 — Tomar uma decisão

```python
if temperatura > 38:
    print("Temperatura elevada")
else:
    print("Temperatura dentro do limite definido")
```

**Em português:** “Se a temperatura for maior que 38, mostre ‘Temperatura elevada’; caso contrário, mostre a segunda mensagem\.”

**Observação:** o código não determina sozinho se uma pessoa está doente; apenas compara um número com um limite escolhido\.

### Exemplo 5 — Repetir uma operação

```python
for nome in nomes:
    print(nome)
```

**Em português:** “Para cada nome existente na coleção `nomes`, mostre esse nome\.”

**Função:** percorre os elementos disponíveis\. O comportamento depende do conteúdo de `nomes`\.

### Exemplo 6 — Definir uma função

```python
def saudacao(nome):
    return f"Olá, {nome}!"
```

**Em português:** “Crie uma função chamada `saudacao` que recebe um nome e devolve a frase ‘Olá, &#91;nome&#93;\!’\.”

**Observação:** definir a função não a executa automaticamente; ela precisa ser chamada\.

### Exemplo 7 — Chamar uma função

```python
mensagem = saudacao("Ana")
```

**Em português:** “Execute a função `saudacao` usando ‘Ana’ como entrada e guarde a resposta em `mensagem`\.”

**Resultado esperado:** `mensagem` contém `Olá, Ana!`, desde que a função tenha sido definida antes\.

### Exemplo 8 — Importar uma biblioteca

```python
import math
```

**Em português:** “Disponibilize o módulo matemático padrão chamado `math` neste programa\.”

**Observação:** `math` faz parte da biblioteca padrão do Python; nem todo módulo que se importa é uma biblioteca externa\.

### Exemplo 9 — Importar uma ferramenta específica

```python
from pathlib import Path
```

**Em português:** “Do módulo `pathlib`, importe a ferramenta `Path`, usada para representar e manipular caminhos de arquivos e diretórios\.”

### Exemplo 10 — Usar um apelido

```python
import numpy as np
```

**Em português:** “Importe a biblioteca NumPy e use `np` como nome curto para acessá\-la\.”

**Observação:** NumPy é uma dependência externa comum em computação científica; precisa estar instalada no ambiente\.

### Exemplo 11 — Ler um arquivo de texto

```python
from pathlib import Path

texto = Path("notas.txt").read_text(encoding="utf-8")
```

**Em português:** “Localize o arquivo `notas.txt`, leia seu conteúdo como texto UTF\-8 e guarde o texto na variável `texto`\.”

**Limite:** o arquivo precisa existir no caminho esperado e o programa precisa ter permissão para lê\-lo\.

### Exemplo 12 — Gravar um arquivo de texto

```python
Path("resultado.txt").write_text("Processo concluído.", encoding="utf-8")
```

**Em português:** “Grave a frase ‘Processo concluído\.’ no arquivo `resultado.txt` usando UTF\-8\.”

**Observação:** conforme a operação e o ambiente, um arquivo existente pode ser sobrescrito\. Para dados importantes, é necessário definir regras de preservação e backup\.

### Exemplo 13 — Tratar uma falha

```python
try:
    numero = int(entrada)
except ValueError:
    print("A entrada não é um número inteiro válido.")
```

**Em português:** “Tente converter `entrada` para um número inteiro\. Se essa conversão gerar um `ValueError`, mostre uma mensagem explicativa\.”

**Observação:** isso trata um tipo específico de erro; não captura automaticamente todas as falhas possíveis\.

### Exemplo 14 — Criar uma lista

```python
sintomas = ["febre", "tosse", "cansaço"]
```

**Em português:** “Crie uma lista chamada `sintomas` contendo três textos: febre, tosse e cansaço\.”

**Observação:** essa lista apenas armazena rótulos\. Não confirma que uma pessoa apresenta esses sintomas\.

### Exemplo 15 — Filtrar dados

```python
idades_adultas = [idade for idade in idades if idade >= 18]
```

**Em português:** “Crie uma nova lista contendo apenas as idades da lista `idades` que sejam maiores ou iguais a 18\.”

### Exemplo 16 — Somar os valores de uma lista

```python
total = sum(valores)
```

**Em português:** “Some os valores da coleção `valores` e guarde a soma em `total`\.”

**Observação:** os elementos precisam ser compatíveis com a operação de soma\.

### Exemplo 17 — Consultar a data atual

```python
from datetime import datetime

agora = datetime.now()
```

**Em português:** “Importe a ferramenta de data e hora e consulte a data e hora locais disponíveis para o processo neste ambiente\.”

**Observação:** o fuso horário e a configuração do sistema influenciam o resultado; não é necessariamente um horário universal\.

### Exemplo 18 — Fazer uma requisição HTTP com biblioteca externa

```python
import requests

resposta = requests.get("https://example.com")
```

**Em português:** “Use a biblioteca `requests` para enviar uma requisição HTTP do tipo GET ao endereço indicado e guardar a resposta em `resposta`\.”

**Observações:**

- A biblioteca `requests` precisa estar instalada\.
- A chamada pode falhar por rede, DNS, TLS, timeout ou outros motivos\.
- Receber uma resposta HTTP não significa que o conteúdo seja confiável\.
- Em aplicações reais, convém configurar timeout e tratamento de erros\.

### Exemplo 19 — Aguardar uma operação assíncrona

```python
resposta = await cliente.get(url)
```

**Em português:** “Aguarde a conclusão da operação assíncrona `cliente.get(url)` e guarde a resposta\.”

**Observação:** `await` só pode ser usado em um contexto assíncrono permitido pela linguagem\. O objeto `cliente` precisa oferecer um método compatível\.

### Exemplo 20 — Converter texto JSON em estrutura de dados

```python
import json

dados = json.loads('{"nome": "Ana", "ativo": true}')
```

**Em português:** “Interprete o texto no formato JSON e converta\-o para a estrutura de dados correspondente em Python\.”

**Nota técnica:** em JSON, os valores lógicos são escritos `true` e `false`; em código Python, os equivalentes são `True` e `False`\. O texto do exemplo é JSON válido\.

## 4\. Exemplos em JavaScript e navegador

### Exemplo 21 — Declarar uma variável

```javascript
const nome = "Ana";
```

**Em português:** “Declare uma variável chamada `nome` cujo vínculo não será reatribuído e associe a ela o texto ‘Ana’\.”

**Observação:** `const` não torna todo objeto associado imutável; impede a reatribuição daquela variável\.

### Exemplo 22 — Criar uma função

```javascript
function somar(a, b) {
  return a + b;
}
```

**Em português:** “Defina uma função chamada `somar`, que recebe dois valores e devolve o resultado da operação `a + b`\.”

**Observação:** o operador `+` pode somar números ou concatenar textos, dependendo dos valores\.

### Exemplo 23 — Buscar dados com `fetch`

```javascript
const resposta = await fetch("https://example.com/api/dados");
```

**Em português:** “Faça uma requisição HTTP ao endereço indicado, usando o comportamento padrão de `fetch`, aguarde a resposta e guarde o objeto de resposta em `resposta`\.”

**Importante:** `fetch` não significa simplesmente “baixar um arquivo”\. Ele inicia uma requisição de rede\. Em muitos casos, é preciso verificar `resposta.ok` e ler o corpo com um método como `resposta.json()` ou `resposta.text()`\. Uma falha HTTP como 404 normalmente não rejeita a promessa por si só\.

### Exemplo 24 — Interpretar o corpo da resposta como JSON

```javascript
const dados = await resposta.json();
```

**Em português:** “Leia o corpo da resposta e tente interpretá\-lo como JSON; guarde o resultado em `dados`\.”

**Observação:** se o corpo não contiver JSON válido, a operação poderá falhar\.

### Exemplo 25 — Verificar uma condição

```javascript
if (usuario.ativo) {
  console.log("Usuário ativo");
}
```

**Em português:** “Se a propriedade `ativo` do objeto `usuario` for avaliada como verdadeira, mostre ‘Usuário ativo’ no console\.”

**Observação:** isso não prova que o usuário esteja autorizado a realizar uma ação; autorização exige regras específicas\.

### Exemplo 26 — Percorrer uma coleção

```javascript
for (const item of itens) {
  console.log(item);
}
```

**Em português:** “Para cada item da coleção iterável `itens`, mostre o item no console\.”

### Exemplo 27 — Transformar uma lista

```javascript
const dobrados = numeros.map(n => n * 2);
```

**Em português:** “Crie uma nova lista aplicando a cada número a operação de multiplicar por dois\.”

### Exemplo 28 — Filtrar uma lista

```javascript
const aprovados = notas.filter(nota => nota >= 7);
```

**Em português:** “Crie uma nova lista contendo somente as notas maiores ou iguais a sete\.”

**Observação:** o limite sete é uma regra definida pelo programador, não uma verdade universal sobre aprovação\.

### Exemplo 29 — Tratar uma promessa com erro

```javascript
try {
  const resposta = await fetch(url);
} catch (erro) {
  console.error("Falha na requisição", erro);
}
```

**Em português:** “Tente fazer a requisição\. Se a operação rejeitar a promessa por uma falha capturada, registre uma mensagem e os detalhes do erro\.”

**Observação:** para tratar respostas HTTP como 404 ou 500, também é necessário verificar o status da resposta\.

### Exemplo 30 — Enviar JSON em uma requisição

```javascript
const resposta = await fetch("/api/usuarios", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ nome: "Ana" })
});
```

**Em português:** “Envie uma requisição POST para `/api/usuarios`, informando que o corpo está no formato JSON e convertendo um objeto com o nome Ana em texto JSON\.”

**Observação:** o servidor precisa aceitar esse endpoint e esse formato\. Enviar a requisição não garante que o registro tenha sido criado\.

## 5\. Exemplos de terminal e instalação

Os comandos abaixo variam conforme o sistema operacional, o shell e o ambiente virtual\.

### Exemplo 31 — Instalar uma biblioteca Python

```bash
python -m pip install requests
```

**Em português:** “Execute o módulo `pip` associado a este interpretador Python e peça a instalação da biblioteca `requests`\.”

**Observação:** pode ser necessário ativar um ambiente virtual e ter acesso ao repositório de pacotes\. A instalação não garante compatibilidade com qualquer versão ou projeto\.

### Exemplo 32 — Executar um arquivo Python

```bash
python main.py
```

**Em português:** “Peça ao interpretador Python disponível no ambiente para executar o arquivo `main.py`\.”

### Exemplo 33 — Mostrar o diretório atual

```bash
pwd
```

**Em português:** “Mostre o caminho do diretório de trabalho atual\.” O comando é comum em shells Unix, Linux e macOS; o comportamento no Windows depende do shell\.

### Exemplo 34 — Listar arquivos

```bash
ls
```

**Em português:** “Liste os arquivos e diretórios do local atual\.” É comum em shells Unix, Linux e macOS; PowerShell também oferece aliases e comandos próprios\.

### Exemplo 35 — Criar um diretório

```bash
mkdir documentos
```

**Em português:** “Crie um diretório chamado `documentos` no local atual, se as condições do ambiente permitirem\.”

### Exemplo 36 — Instalar dependências de um projeto

```bash
python -m pip install -r requirements.txt
```

**Em português:** “Leia a lista de dependências no arquivo `requirements.txt` e solicite ao `pip` a instalação dos pacotes especificados\.”

**Observação:** o arquivo precisa existir e conter especificações válidas; a instalação pode falhar por incompatibilidade ou problemas de rede\.

### Exemplo 37 — Consultar a versão do Python

```bash
python --version
```

**Em português:** “Mostre a versão do interpretador Python chamado pelo comando `python`\.”

### Exemplo 38 — Clonar um repositório Git

```bash
git clone https://github.com/exemplo/projeto.git
```

**Em português:** “Peça ao Git para copiar o repositório remoto indicado para uma nova pasta local, incluindo seu histórico disponível\.”

**Observação:** o endereço é ilustrativo\. O acesso depende de o repositório existir e das permissões necessárias\.

## 6\. Exemplos de estruturas de dados e APIs

### Exemplo 39 — Objeto JSON

```json
{
  "nome": "Ana",
  "ativo": true,
  "tentativas": 3
}
```

**Em português:** “Represente um objeto com três campos: nome igual a Ana, ativo igual a verdadeiro e tentativas igual a três\.”

**Observação:** JSON é um formato de dados, não uma linguagem de programação executável por si só\.

### Exemplo 40 — Endpoint de API

```text
GET /api/usuarios/42
```

**Em português:** “Solicite ao endpoint `/api/usuarios/42` a representação do recurso identificado por 42, usando o método HTTP GET\.”

**Observação:** a semântica exata depende da API\. GET costuma ser usado para leitura, mas a implementação do servidor precisa seguir o contrato definido\.

### Exemplo 41 — Criar um recurso por API

```text
POST /api/usuarios
Content-Type: application/json

{"nome":"Ana"}
```

**Em português:** “Envie ao endpoint de usuários uma requisição POST cujo corpo contém um objeto JSON com o nome Ana\.”

**Observação:** a API pode validar, rejeitar, modificar ou armazenar o conteúdo conforme suas regras\.

### Exemplo 42 — Consulta SQL

```sql
SELECT nome, idade
FROM usuarios
WHERE idade >= 18;
```

**Em português:** “Selecione as colunas nome e idade da tabela usuarios, considerando apenas os registros cuja idade seja maior ou igual a 18\.”

**Observação:** a consulta lê dados de acordo com o esquema e as permissões do banco\. Ela não altera os registros\.

### Exemplo 43 — Inserir um registro SQL

```sql
INSERT INTO usuarios (nome, idade)
VALUES ('Ana', 30);
```

**Em português:** “Solicite a inserção de um registro na tabela usuarios, preenchendo nome com Ana e idade com 30\.”

**Observação:** a operação pode falhar por restrições, permissões, transação ou incompatibilidade do esquema\.

### Exemplo 44 — Consultar o estado de um serviço HTTP

```bash
curl -i https://example.com
```

**Em português:** “Faça uma requisição HTTP ao endereço e inclua na saída informações de cabeçalho da resposta, além do conteúdo retornado conforme o comportamento do `curl`\.”

**Observação:** `curl` é uma ferramenta de transferência de dados; a resposta pode variar conforme o servidor e a rede\.

## 7\. Exemplos de conceitos de inteligência artificial

### Exemplo 45 — Tokenização

```python
tokens = tokenizer.encode("Bom dia")
```

**Em português:** “Use o tokenizador disponível para converter o texto ‘Bom dia’ em uma sequência de identificadores de tokens\.”

**Observação:** tokens não correspondem necessariamente a palavras inteiras; podem representar partes de palavras, sinais ou outros fragmentos\.

### Exemplo 46 — Gerar uma representação vetorial

```python
vetor = modelo.encode("insuficiência cardíaca")
```

**Em português:** “Peça ao modelo ou codificador utilizado para transformar o texto em uma representação numérica vetorial\.”

**Observação:** o método `encode` depende da biblioteca e do modelo\. A existência de um vetor não garante que ele represente perfeitamente o significado\.

### Exemplo 47 — Recuperar documentos semelhantes

```python
resultados = indice.search(vetor_consulta, top_k=5)
```

**Em português:** “Pesquise no índice os cinco resultados mais relevantes segundo o critério de busca implementado, usando `vetor_consulta` como consulta\.”

**Observação:** `top_k=5` pede cinco resultados, se disponíveis; relevância depende do índice, da métrica e dos dados\.

### Exemplo 48 — Calcular uma pontuação

```python
pontuacao = avaliar(resposta, criterios)
```

**Em português:** “Passe a resposta e os critérios para a função de avaliação e guarde a pontuação devolvida\.”

**Observação:** o nome da função não revela como ela avalia\. É preciso conhecer sua implementação e validar se a pontuação mede aquilo que se pretende medir\.

### Exemplo 49 — Chamar um modelo de linguagem, em pseudocódigo

```python
resposta = modelo.gerar(prompt)
```

**Em português:** “Solicite ao modelo que produza uma saída a partir do texto de entrada chamado `prompt` e guarde o resultado\.”

**Observação:** é pseudocódigo ilustrativo\. APIs reais variam, podem exigir parâmetros adicionais e podem produzir respostas não determinísticas\.

### Exemplo 50 — Verificar uma resposta antes de utilizá\-la

```python
if validar(resposta):
    usar(resposta)
else:
    revisar(resposta)
```

**Em português:** “Se a resposta passar pela função de validação, use\-a; caso contrário, encaminhe\-a para revisão\.”

**Observação:** a confiabilidade depende dos critérios da função `validar`\. Uma verificação fraca pode aprovar uma resposta incorreta\.

## 8\. Exemplos de tradução em linguagem cotidiana

|Instrução técnica       |Tradução natural                                                                                                             |
|------------------------|-----------------------------------------------------------------------------------------------------------------------------|
|`fetch(url)`            |“Busque dados nesse endereço por meio de uma requisição.”                                                                    |
|`await fetch(url)`      |“Faça a requisição e espere a resposta antes de continuar neste fluxo assíncrono.”                                           |
|`import requests`       |“Disponibilize a biblioteca `requests` para este programa.”                                                                  |
|`pip install requests`  |“Instale a biblioteca `requests` no ambiente selecionado.”                                                                   |
|`return resultado`      |“Encerre esta chamada da função devolvendo `resultado`.”                                                                     |
|`if not dados:`         |“Se `dados` for avaliado como vazio ou falso nesta linguagem, execute o bloco seguinte.”                                     |
|`items.append(item)`    |“Adicione `item` ao final da lista `items`, se esse objeto for uma lista Python.”                                            |
|`dict.get("nome")`      |“Consulte o valor associado à chave `nome`, devolvendo o padrão configurado se ela não existir.”                             |
|`json.loads(texto)`     |“Interprete o texto como JSON e transforme-o em dados Python.”                                                               |
|`response.status_code`  |“Consulte o código de status HTTP presente no objeto de resposta, se esse objeto usar essa interface.”                       |
|`SELECT * FROM tabela`  |“Solicite todas as colunas de todos os registros da tabela, sujeitos às regras do banco.”                                    |
|`git commit -m "ajuste"`|“Registre no histórico Git local as mudanças preparadas, com a mensagem ‘ajuste’.”                                           |
|`git push`              |“Envie os commits locais para um repositório remoto configurado, se houver acesso e destino válidos.”                        |
|`docker build -t app .` |“Peça ao Docker para construir uma imagem usando o contexto do diretório atual e atribuir a etiqueta `app`.”                 |
|`npm install`           |“Peça ao npm para instalar as dependências descritas pelo projeto, conforme a configuração e o arquivo de lock.”             |
|`chmod +x script.sh`    |“Adicione permissão de execução ao arquivo para as categorias afetadas pela regra, em sistemas compatíveis com esse comando.”|

## 9\. Como traduzir sem distorcer

O AIGAR deve seguir um procedimento consistente quando receber um comando desconhecido ou ambíguo:

1. **Identificar a linguagem:** Python, JavaScript, SQL, shell, JSON, pseudocódigo ou outra\.
2. **Separar os elementos:** verbo, argumentos, variáveis, operadores, tipos e contexto\.
3. **Explicar a ação literal:** o que o comando solicita ao ambiente\.
4. **Explicar o propósito provável:** por que alguém poderia usá\-lo, marcando a inferência como provável\.
5. **Verificar pré\-condições:** bibliotecas, permissões, variáveis, arquivos, rede e versões\.
6. **Indicar efeitos colaterais:** gravação, exclusão, envio de dados, chamadas externas ou custos\.
7. **Separar intenção de resultado:** o comando pode pedir uma ação sem que ela tenha sido concluída\.
8. **Explicitar incerteza:** se a função ou biblioteca não for conhecida, não inventar seu comportamento\.
9. **Traduzir para o nível adequado:** português simples para iniciantes ou descrição técnica para profissionais\.
10. **Preservar os nomes originais:** explicar termos como `fetch`, `await` e `return`, sem substituir o código por uma tradução que não possa ser executada\.

## 10\. Padrão recomendado de resposta do AIGAR

Quando alguém perguntar “O que significa este código?”, a resposta pode seguir este formato:

**Código:** `await fetch(url)`

**Tradução simples:** “Faça uma requisição ao endereço indicado e aguarde a resposta\.”

**Por partes:**

- `fetch`: inicia uma requisição de rede\.
- `url`: indica o endereço de destino\.
- `await`: espera a operação assíncrona terminar antes de continuar no fluxo atual\.

**O que não garante:** não garante que o servidor responda com sucesso, que o conteúdo seja confiável ou que a resposta já tenha sido convertida em JSON\.

**Em uma frase:** “Peça os dados ao endereço indicado e espere a resposta chegar\.”

## 11\. Exercícios para consolidar

Para cada exemplo, tente responder:

1. Qual é o verbo ou a operação principal?
2. Quais dados entram?
3. Qual resultado é esperado?
4. O que pode impedir a execução?
5. O comando modifica algum estado ou apenas consulta?
6. Que parte da tradução é literal e que parte é uma inferência sobre o propósito?
7. Como você explicaria o mesmo comando a uma criança, a um iniciante e a um programador?

### Exercício A

```python
resultado = max([4, 9, 2])
```

Traduza: o que é solicitado e qual valor será guardado em `resultado`?

### Exercício B

```javascript
const ativo = usuario && usuario.ativo;
```

Traduza com cuidado: o que a expressão faz quando `usuario` é um valor falsy? Considere as regras do JavaScript, não apenas a palavra “e”\.

### Exercício C

```sql
DELETE FROM registros WHERE expirado = TRUE;
```

Traduza e identifique o risco: quais registros podem ser removidos? Por que seria importante confirmar a condição antes de executar?

### Exercício D

```bash
python -m pip install -r requirements.txt
```

Explique quais arquivos e ambientes influenciam o resultado e por que o comando não garante uma instalação bem\-sucedida\.

## 12\. Síntese

Código é uma forma precisa, mas contextual, de expressar operações\. Traduzir código para linguagem humana exige mais do que trocar palavras: é necessário identificar a linguagem, interpretar a estrutura, conhecer as condições de execução e distinguir o que foi solicitado do que realmente aconteceu\.

Para o AIGAR, essa competência funciona como uma ponte entre linguagem humana e linguagem computacional\. A tradução deve ser **compreensível, tecnicamente fiel, contextualizada e honesta quanto às incertezas**\.

## 13\. Relação com os capítulos anteriores

- **Capítulo 02 — Linguagem:** como símbolos e contexto produzem significado\.
- **Capítulo 03 — Linguagem computacional e humana:** diferenças entre instruções técnicas e expressões humanas\.
- **Capítulo 06 — Raciocínio e SNC:** mecanismos de compreensão e controle na cognição humana\.
- **Capítulo 07 — Analogias entre raciocínio e computação:** correspondências funcionais entre sistemas\.
- **Capítulo 08 — Este capítulo:** exemplos concretos de comandos e suas traduções para o português\.

## 14\. Nota editorial

Os exemplos foram selecionados para fins didáticos\. Antes de utilizar comandos em ambientes reais, confirme a documentação oficial da linguagem ou biblioteca, as versões e os efeitos colaterais\. Comandos que excluem dados, alteram permissões, enviam informações ou executam código devem ser testados em ambiente seguro e autorizados\.

---

**Fim do Capítulo 08 — Texto\-Matriz AIGAR**
