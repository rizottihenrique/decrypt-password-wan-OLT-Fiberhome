import re

# 1. Mapeamento matemático otimizado (chr(158 - ord(caractere)))
# Criamos a tabela de tradução nativa para velocidade máxima em nível de C
tabela_traducao = str.maketrans({chr(i): chr(158 - i) for i in range(32, 127) if 0 <= (158 - i) <= 255})

# 2. Regex compilada para localizar o padrão key:VALOR
# Captura o 'key:' e tudo que não for espaço logo em seguida
regex_key = re.compile(r'(key:)(\S+)')

def processar_e_substituir(arquivo_entrada, arquivo_saida):
    try:
        with open(arquivo_entrada, 'r', encoding='utf-8') as f_in, \
             open(arquivo_saida, 'w', encoding='utf-8') as f_out:
            
            # Processa linha por linha para manter o consumo de memória RAM zerado
            for linha in f_in:
                if not linha.strip():
                    continue
                
                # Busca o padrão no comando
                match = regex_key.search(linha)
                if match:
                    senha_criptografada = match.group(2)
                    
                    # Descriptografa a senha instantaneamente
                    senha_real = senha_criptografada.translate(tabela_traducao)
                    
                    # Substitui 'key:XXXXX' pela senha descriptografada
                    # Exemplo: key:=<;: vira abcdef
                    linha_modificada = linha.replace(f"key:{senha_criptografada}", senha_real)
                    
                    f_out.write(linha_modificada)
                else:
                    # Se por acaso a linha não contiver o campo 'key:', mantém a linha original
                    f_out.write(linha)
                    
        print(f"Sucesso! Comandos atualizados e salvos em: {arquivo_saida}")
        
    except FileNotFoundError:
        print(f"Erro: O arquivo '{arquivo_entrada}' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    # Nomes dos arquivos de entrada e saída
    arquivo_input = "input.txt"
    arquivo_output = "output.txt"
    
    processar_e_substituir(arquivo_input, arquivo_output)