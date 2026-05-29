# Script de Migração e Apontamento Massivo de TR-069 - OLT Fiberhome

Este script automatizado em Python foi desenvolvido especificamente para cenários de migração, auditoria e gerência centralizada de provedores de internet (ISPs). O objetivo principal da ferramenta é **automatizar o apontamento e a ativação do protocolo TR-069 (ACS)** em milhares de ONTs simultaneamente através da CLI da OLT.

Para que o apontamento do TR-069 funcione perfeitamente sem intervenção manual, o script processa os arquivos de configuração em lote e resolve três grandes gargalos de uma só vez:
1. **Ativação da WAN TR-069 (Dual Stack):** Altera o perfil da WAN de `mode inter` para `mode tr069_int` e força o provisionamento em IPv4/IPv6 (`both`) via `dhcpv6`.
2. **Desofuscação de Senhas PPPoE:** Quebra a criptografia estática nativa do firmware (`key:VALOR`), inserindo as senhas reais em texto claro para que a migração não derrube a autenticação dos clientes.
3. **Divisão de Contexto da CLI (Context-Aware):** Separa os comandos em blocos distintos de execução (WAN e Gerência Remota), respeitando a árvore de diretórios nativa da OLT.

---

## 1. Funcionamento e Arquitetura do Script

O script divide o arquivo final (`output.txt`) em duas etapas lógicas fundamentais para que você possa copiar e colar no terminal da OLT sem erros de sintaxe ou contexto:

### Bloco 1: Ajuste de WAN e Conectividade (Diretório: `gepon/onu/lan`)
Cada ONU possui um par de comandos sequenciais. O script intercepta essas linhas, aplica as correções de protocolo, traduz a senha, insere o comando de validação (`apply wancfg`) e pula uma linha para o próximo equipamento.
* **Modificação do Modo:** Substitui `mode inter` por `mode tr069_int`.
* **Upgrade de IP-Stack:** Altera a pilha de rede antiga (`ipv4` / `slaac`) para o padrão recomendado de transição: Dual Stack (`both`) com atribuição dinâmica via `dhcpv6`.

### Bloco 2: Apontamento Remoto do Servidor ACS (Diretório: `gepon/onu`)
Como o comando de gerenciamento remoto pertence a outro nível da CLI, o script mapeia dinamicamente todos os IDs de **Slot, Pon e ONU** processados no Bloco 1 e, no final do arquivo, gera de forma isolada a lista de comandos para direcionar os equipamentos até o servidor TR-069 do provedor.

---

## 2. Engenharia Reversa da Senha (`key:`)

Para garantir que o TR-069 assuma a gerência sem quebrar os acessos atuais, o script descriptografa os caracteres contidos no parâmetro `key:` usando a regra matemática de espelhamento estático do firmware da OLT descoberta em testes de bancada:

$$\text{Valor ASCII da Senha Real} = 158 - \text{Valor ASCII do Caractere Mascarado}$$

O script executa essa conversão instantaneamente em nível de linguagem C através da função nativa `.translate()` do Python, garantindo performance máxima.

---

## 3. Otimização para Provedores (Alta Performance)

* **Consumo de Memória RAM Próximo a zero:** Utiliza processamento em formato de *Stream* (linha por linha). Arquivos de backup gigantescos contendo configurações de mais de 10.000 ONTs são processados em segundos sem travar o computador.
* **Geração Limpa:** Comandos não reconhecidos ou linhas de comentários são preservados integralmente, mantendo o histórico e a integridade dos dados originais.

---

## 4. Como Utilizar

1. Extraia o script de provisionamento ou backup de comandos atual da sua OLT.
2. Salve este arquivo com o nome de **`input.txt`** na mesma pasta do script Python.
3. Execute o script no terminal:
   ```bash
   python decodificador.py
