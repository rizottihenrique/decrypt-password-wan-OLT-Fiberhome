import re

# 1. Mapeamento matemático otimizado (chr(158 - ord(caractere)))
tabela_traducao = str.maketrans({chr(i): chr(158 - i) for i in range(32, 127) if 0 <= (158 - i) <= 255})

# 2. Regex para localizar o padrão key:VALOR
regex_key = re.compile(r'(key:)(\S+)')

# 3. Regex para capturar os números de: sl [slot] [pon] [onu_id]
regex_sl = re.compile(r'sl\s+(\d+)\s+(\d+)\s+(\d+)')

def processar_lote_olt(arquivo_entrada, arquivo_saida):
    try:
        with open(arquivo_entrada, 'r', encoding='utf-8') as f_in, \
             open(arquivo_saida, 'w', encoding='utf-8') as f_out:
            
            # Variáveis para rastrear o bloco atual da ONU
            slot_atual = None
            pon_atual = None
            onu_id_atual = None
            
            for linha in f_in:
                if not linha.strip():
                    continue
                
                # Se for a linha que contém o modo e a senha criptografada
                if "mode inter" in linha:
                    # Captura os parâmetros do slot/pon/onu antes de modificar
                    match_sl = regex_sl.search(linha)
                    if match_sl:
                        slot_atual = match_sl.group(1)
                        pon_atual = match_sl.group(2)
                        onu_id_atual = match_sl.group(3)
                    
                    # Altera 'mode inter' para 'mode tr069_int'
                    linha = linha.replace("mode inter", "mode tr069_int")
                    
                    # Localiza e decodifica a senha do 'key:'
                    match_key = regex_key.search(linha)
                    if match_key:
                        senha_criptografada = match_key.group(2)
                        senha_real = senha_criptografada.translate(tabela_traducao)
                        # Substitui o bloco key:XXXX pela senha em texto claro
                        linha = linha.replace(f"key:{senha_criptografada}", senha_real)
                    
                    # Escreve a primeira linha modificada
                    f_out.write(linha)
                
                # Se for a segunda linha (configuração de IP-stack/IPv6)
                elif "ip-stack-mode" in linha:
                    # Escreve a segunda linha exatamente como ela é
                    f_out.write(linha)
                    
                    # Se tivermos capturado o slot correspondente a esse bloco
                    if slot_atual and pon_atual and onu_id_atual:
                        # Gera o apply logo abaixo da linha de ip-stack e pula uma linha para a próxima ONU
                        comando_apply = f"apply wancfg sl {slot_atual} {pon_atual} {onu_id_atual}\n\n"
                        f_out.write(comando_apply)
                        
                        # Reseta as variáveis para garantir integridade no próximo bloco
                        slot_atual = None
                        pon_atual = None
                        onu_id_atual = None
                
                # Caso haja alguma outra linha no TXT que não se encaixe nos padrões acima
                else:
                    f_out.write(linha)
                    
        print(f"Sucesso! Comandos organizados e salvos em: {arquivo_saida}")
        
    except FileNotFoundError:
        print(f"Erro: O arquivo '{arquivo_entrada}' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    arquivo_input = "input.txt"
    arquivo_output = "output.txt"
    
    processar_lote_olt(arquivo_input, arquivo_output)
