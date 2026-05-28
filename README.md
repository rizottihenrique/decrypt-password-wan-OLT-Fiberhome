# Decodificador de Senhas WAN - OLT Fiberhome / AN5000 e AN6000 Series

Este projeto consiste em um script automatizado em Python desenvolvido para descriptografar/desofuscar em lote as senhas de conexões WAN (PPPoE) contidas em arquivos de configuração extraídos de OLTs

O script localiza o parâmetro `key:VALOR` dentro dos comandos `set wancfg`, reverte a cifragem estática do firmware e substitui o campo diretamente pelo texto claro (senha real), gerando um arquivo pronto para provisionamento ou auditoria.

---

## 2. Como o Script Funciona por Baixo dos Panos

### A Lógica da Cifra (Espelhamento ASCII)
Durante os testes empíricos em bancada utilizando senhas conhecidas (como `aaaaaa` e o alfabeto completo), descobriu-se que o firmware da OLT não utiliza uma criptografia complexa (como MD5 ou AES), mas sim uma **Cifra de Substituição por Espelhamento** baseada na tabela ASCII padrão.

A regra matemática exata aplicada pelo firmware para mascarar cada caractere é:

$$\text{Valor ASCII do Caractere Mascarado} = 158 - \text{Valor ASCII da Senha Real}$$

Para reverter a senha e descobrir o texto claro, o script faz a operação inversa:

$$\text{Valor ASCII da Senha Real} = 158 - \text{Valor ASCII do Caractere Mascarado}$$

#### Exemplo Prático de Conversão:
* A letra **`a`** possui o valor ASCII **97**.
* Aplicando a fórmula: $158 - 97 = 61$.
* O valor **61** na tabela ASCII corresponde ao caractere **`=`**.
* Portanto, se a senha gravada for `aaaaaa`, o comando na OLT exibirá `key:======`.

---

## 3. Otimizações de Performance (Processamento em Lote)

O script foi desenhado especificamente para ambientes de provedores de internet (ISPs) que lidam com **milhares de ONTs simultaneamente**. Para garantir velocidade máxima e consumo mínimo de hardware, foram aplicadas duas técnicas avançadas:

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
