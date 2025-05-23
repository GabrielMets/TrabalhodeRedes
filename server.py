import socket
import struct
import time
import hashlib
import hmac

SECRET_KEY = b"0123456789abcdef0123456789abcdef"
IP_SERVIDOR = "127.0.0.1" #IP desejado para o servidor
PORTA = 123
cripto = None #usar None/True para desativar/ativar criptografia

def gerar_hmac(mensagem: bytes, chave: bytes) -> bytes:
    return hmac.new(chave, mensagem, hashlib.sha256).digest()

def verificar_hmac(mensagem: bytes, chave: bytes, hmac_recebido: bytes) -> bool:
    hmac_calculado = gerar_hmac(mensagem, chave)
    return hmac.compare_digest(hmac_calculado, hmac_recebido)

def criptografar_mensagem(mensagem: bytes, chave: bytes) -> bytes:
    chave_repetida = chave * (len(mensagem) // len(chave) + 1)
    mensagem_criptografada = bytes([a ^ b for a, b in zip(mensagem, chave_repetida)])
    return mensagem_criptografada

def descriptografar_mensagem(mensagem_criptografada: bytes, chave: bytes) -> bytes:
    chave_repetida = chave * (len(mensagem_criptografada) // len(chave) + 1)
    mensagem_descriptografada = bytes([a ^ b for a, b in zip(mensagem_criptografada, chave_repetida)])
    return mensagem_descriptografada

def cria_servidor_ntp(PORTA, IP_SERVIDOR):

    
    servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    servidor_socket.bind((IP_SERVIDOR, PORTA))
    print(f"Servidor NTP iniciado na porta {PORTA} e no IP {IP_SERVIDOR}...") #servidor iniciado

    if cripto:
        print('Modo de critptografia Ativado... ')
        while True:
            try:
                hmac_cliente, endereco_cliente = servidor_socket.recvfrom(32)  #recebe o HMAC primeiro
                dados_criptografados, _ = servidor_socket.recvfrom(48)  #recebe os dados criptografados
            
                if not verificar_hmac(dados_criptografados, SECRET_KEY, hmac_cliente): #verifica o hmac
                    print("Erro: Falha na autenticação do cliente.")
                    continue

                dados = descriptografar_mensagem(dados_criptografados, SECRET_KEY) #descriptografa a mensagem

                resposta_ntp = processa_requisicao_ntp(dados) #recebe o pacote NTP

                if resposta_ntp:
                    resposta_criptografada = criptografar_mensagem(resposta_ntp, SECRET_KEY) #criptografa o pacote
                    hmac_resposta = gerar_hmac(resposta_criptografada, SECRET_KEY)  #gera hmac

                    print(f"enviando resposta para {endereco_cliente}")
                    servidor_socket.sendto(hmac_resposta, endereco_cliente) #envia hmac
                    servidor_socket.sendto(resposta_criptografada, endereco_cliente) #envia pacote criptografado

            except Exception as e:
                print(f"Erro ao processar solicitação: {e}")
    else:
        print('Modo de critptografia Desativado... ')
        while True:     
            dados, endereco_cliente = servidor_socket.recvfrom(48)  #recebe os dados criptografados

            try:   
            
                resposta_ntp = processa_requisicao_ntp(dados) #recebe o pacote NTP

                if resposta_ntp:
                    print(f"enviando resposta para {endereco_cliente}")
                    servidor_socket.sendto(resposta_ntp, endereco_cliente) #envia pacote
                
            except Exception as e:
                print(f"Erro ao processar solicitação: {e}")

def processa_requisicao_ntp(dados): #monta o pacote NTP

    timestamp_atual = time.time() + 2208988800  #converte para NTP

    fracao = int((timestamp_atual - int(timestamp_atual)) * (2**32)) #fracao dos segundos
    
    resposta_ntp = bytearray(48)
    try:
        solicitacao_ntp = struct.unpack("!12I", dados)
        
        
        struct.pack_into(
            "!BBBBIIIQIIIIII",  #formato do pacote
            resposta_ntp,  #bytearray onde será armazenado
            0,  #offset inicial
            (0 << 6) | (4 << 3) | 4,  # LI (0) | Versão (4) | Modo (4 - Server)
            1,  #stratum (1 = Primary Server)
            0,  #poll Interval
            1,  #precision
            solicitacao_ntp[2],  #root Delay
            solicitacao_ntp[3],  #root Dispersion
            0,  #reference ID (0 para servidores de referência)
            int(timestamp_atual),  #reference TIMESTAMP
            fracao,
            solicitacao_ntp[8],   #origin TIMESTAMP
            int(timestamp_atual),  #receive Timestamp
            fracao,
            int(timestamp_atual),  #transmit Timestamp
            fracao
        )

        return resposta_ntp
    
    except struct.error as e:
        print(f"Erro ao desempacotar dados: {e}")
        return None

cria_servidor_ntp(PORTA, IP_SERVIDOR) #cria o servidor no IP e porta designados