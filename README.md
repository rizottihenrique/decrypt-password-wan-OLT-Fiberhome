# Decodificador e Modificador de Configurações WAN (Modo Lote) - OLT Fiberhome

Este script automatizado em Python foi desenvolvido para processar arquivos de configuração em lote extraídos de OLTs Fiberhome.

1. **Desofuscação de Senhas:** Reverte a codificação estática do campo `key:VALOR` para texto claro (senha real do PPPoE).
2. **Alteração de Perfil de Gerência:** Substitui o parâmetro `mode inter` por `mode tr069_int`.
3. **Automação de Commit por Bloco:** Identifica o par de comandos de cada ONU, injeta o comando `apply wancfg` com o respectivo Slot/Pon/Onu_ID e adiciona espaçamento para facilitar a leitura.

---

## 1. Funcionamento do Fluxo de Blocos (A Nova Lógica)

Diferente de scripts de substituição linear simples, este decodificador compreende que cada equipamento (ONU) no arquivo de configuração possui um bloco estruturado de **duas linhas de comando consecutivas**. 

O script rastreia e organiza o fluxo da seguinte forma:

```text
[ Linha 1: WAN e Senha ]  --> Modifica o modo, extrai os IDs do Slot e traduz a senha.
[ Linha 2: IP-Stack ]     --> Copia as diretrizes de IPv4/IPv6 integralmente.
[ Injeção Automatizada ]  --> Insere o comando "apply wancfg sl [Slot] [Pon] [Onu_ID]".
[ Quebra de Linha ]       --> Pula um espaço em branco antes de iniciar a próxima ONU.
```

## 2. Como o Script Funciona

### A Lógica da Cifra (Espelhamento ASCII)
Durante os testes empíricos em bancada utilizando senhas conhecidas (como `aaaaaa` e o alfabeto completo), descobriu-se que o firmware da OLT não utiliza uma criptografia complexa (como MD5 ou AES), mas sim uma **Cifra de Substituição por Espelhamento** baseada na tabela ASCII padrão.

```text
A regra matemática exata aplicada pelo firmware para mascarar cada caractere é:

$$\text{Valor ASCII do Caractere Mascarado} = 158 - \text{Valor ASCII da Senha Real}$$

Para reverter a senha e descobrir o texto claro, o script faz a operação inversa:

$$\text{Valor ASCII da Senha Real} = 158 - \text{Valor ASCII do Caractere Mascarado}$$
```

#### Exemplo Prático de Conversão:
* A letra **`a`** possui o valor ASCII **97**.
* Aplicando a fórmula: $158 - 97 = 61$.
* O valor **61** na tabela ASCII corresponde ao caractere **`=`**.
* Portanto, se a senha gravada for `aaaaaa`, o comando na OLT exibirá `key:======`.

---

## 3. Otimizações de Performance (Processamento em Lote)

O script foi desenhado especificamente para ambientes de provedores de internet (ISPs) que lidam com **milhares de ONTs simultaneamente**. Para garantir velocidade máxima e consumo mínimo de hardware, foram aplicadas duas técnicas:

1. **Processamento em Stream (Linha por Linha):** O script não carrega o arquivo `.txt` inteiro na memória RAM. Ele lê, processa e escreve uma linha por vez. Isso significa que você pode processar um arquivo de configuração de 2GB contendo milhões de ONTs utilizando praticamente 0% de memória RAM.
2. **Tabela de Tradução Nativa (`str.maketrans`):** Em vez de fazer loops em Python caractere por caractere (o que seria lento), o script pré-calcula a tabela de reversão de todos os caracteres visíveis e utiliza a função `.translate()`. Essa função executa a substituição das strings diretamente em **nível de linguagem C** (mecanismo interno do Python), tornando a conversão instantânea.

---

## 4. Pré-requisitos

* Python 3.6 ou superior instalado no sistema.
* Não é necessária a instalação de nenhuma biblioteca de terceiros (o script utiliza apenas módulos nativos: `re` e `sys`).

---

## 5. Como Utilizar

1. Extraia o relatório ou o arquivo de texto contendo as linhas de comando da sua OLT.
2. Salve esse arquivo com o nome de **`input.txt`** na mesma pasta onde o script `decodificador.py` está localizado.
3. Abra o seu terminal (Prompt de Comando ou PowerShell) na pasta do projeto e execute:

```bash
python decodificador.py
