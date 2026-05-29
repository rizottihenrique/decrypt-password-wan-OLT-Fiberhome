import re

# 1. Mapeamento matemático otimizado (chr(158 - ord(caractere)))
tabela_traducao = str.maketrans({chr(i): chr(158 - i) for i in range(32, 127) if 0 <= (158 - i) <= 255})

# 2. Regex para localizar o padrão key:VALOR
regex_key = re.compile(r'(key:)(\S+)')

# 3. Regex para capturar os números de: sl [slot] [pon] [onu_id]
regex_sl = re.compile(r'sl\s+(\d+)\s+(\d+)\s+(\d+)')

def processar_lote_olt_completo(arquivo_entrada, arquivo_saida):
    try:
        lista_equipamentos = []
        
        with open(arquivo_entrada, 'r', encoding='utf-8') as f_in, \
             open(arquivo_saida, 'w', encoding='utf-8') as f_out:
            
            # Cabeçalho do Bloco 1
            f_out.write("! ==================================================\n")
            f_out.write("! BLOCO 1: CONFIGURACAO DE WAN (DIRETORIO: gepon/onu/lan)\n")
            f_out.write("! ==================================================\n\n")
            
            slot_atual = None
            pon_atual = None
            onu_id_atual = None
            
            for linha in f_in:
                if not linha.strip():
                    continue
                
                # Se for a primeira linha (WAN e senha)
                if "mode inter" in linha:
                    match_sl = regex_sl.search(linha)
                    if match_sl:
                        slot_atual = match_sl.group(1)
                        pon_atual = match_sl.group(2)
                        onu_id_atual = match_sl.group(3)
                        
                        equipamento = (slot_atual, pon_atual, onu_id_atual)
                        if equipamento not in lista_equipamentos:
                            lista_equipamentos.append(equipamento)
                    
                    # Altera 'mode inter' para 'mode tr069_int'
                    linha = linha.replace("mode inter", "mode tr069_int")
                    
                    # Localiza e decodifica a senha do 'key:'
                    match_key = regex_key.search(linha)
                    if match_key:
                        senha_criptografada = match_key.group(2)
                        senha_real = senha_criptografada.translate(tabela_traducao)
                        linha = linha.replace(f"key:{senha_criptografada}", senha_real)
                    
                    f_out.write(linha)
                
                # Se for a segunda linha (Configuração de IP-stack / IPv6)
                elif "ip-stack-mode" in linha:
                    # Aplica a alteração para habilitar IPv4/IPv6 (both) e DHCPv6
                    if "ip-stack-mode ipv4" in linha:
                        linha = linha.replace("ip-stack-mode ipv4", "ip-stack-mode both")
                    if "ipv6-src-type slaac" in linha:
                        linha = linha.replace("ipv6-src-type slaac", "ipv6-src-type dhcpv6")
                    
                    f_out.write(linha)
                    
                    if slot_atual and pon_atual and onu_id_atual:
                        # Injeta o apply correspondente ao bloco
                        comando_apply = f"apply wancfg sl {slot_atual} {pon_atual} {onu_id_atual}\n\n"
                        f_out.write(comando_apply)
                        
                        # Reseta as variáveis do bloco atual
                        slot_atual = None
                        pon_atual = None
                        onu_id_atual = None
                else:
                    f_out.write(linha)
            
            # Cabeçalho do Bloco 2 (Final do arquivo)
            f_out.write("\n! ==================================================\n")
            f_out.write("! BLOCO 2: APONTAMENTO TR-069 (DIRETORIO: gepon/onu)\n")
            f_out.write("! ==================================================\n\n")
            
            for slot, pon, onu_id in lista_equipamentos:
                comando_tr069 = (
                    f"set remote_manage_cfg slot {slot} pon {pon} onu {onu_id} tr069 enable "
                    f"acs_url http://cwmp.teste.teste:8000 acl_user teste acl_pswd teste@123 "
                    f"inform enable interval 43200 port 30005 user cpe pswd cpe\n"
                )
                f_out.write(comando_tr069)
                
        print(f"Sucesso! Todos os blocos foram gerados e salvos em: {arquivo_saida}")
        
    except FileNotFoundError:
        print(f"Erro: O arquivo '{arquivo_entrada}' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    arquivo_input = "input.txt"
    arquivo_output = "output.txt"
    
    processar_lote_olt_completo(arquivo_input, arquivo_output)
