import socket
import struct
import time
import hashlib
import hmac

SECRET_KEY = b"0123456789abcdef0123456789abcdef"
IP_SERVIDOR = "127.0.0.1"
PORTA = 123
cripto = None

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

def imprime_pacote_hex(pacote):
    """Imprime um pacote NTP em hexadecimal."""
    for i, byte in enumerate(pacote):
        print(f"Byte {i}: {byte:02X}", end=" ")
        if (i + 1) % 4 == 0:
            print()
    print()

def cria_servidor_ntp(PORTA, IP_SERVIDOR):

    
    servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    servidor_socket.bind((IP_SERVIDOR, PORTA))
    print(f"Servidor NTP iniciado na porta {PORTA} e no IP {IP_SERVIDOR}...")

    if cripto:
        print('ta criptado')
        while True:
            try:
                hmac_cliente, endereco_cliente = servidor_socket.recvfrom(32)  #recebe o HMAC primeiro
                dados_criptografados, _ = servidor_socket.recvfrom(48)  #recebe os dados criptografados
            
                if not verificar_hmac(dados_criptografados, SECRET_KEY, hmac_cliente):
                    print("Erro: Falha na autenticação do cliente.")
                    continue

                dados = descriptografar_mensagem(dados_criptografados, SECRET_KEY)

                resposta_ntp = processa_requisicao_ntp(dados)

                if resposta_ntp:
                    resposta_criptografada = criptografar_mensagem(resposta_ntp, SECRET_KEY)
                    hmac_resposta = gerar_hmac(resposta_criptografada, SECRET_KEY)

                    servidor_socket.sendto(hmac_resposta, endereco_cliente)
                    servidor_socket.sendto(resposta_criptografada, endereco_cliente)

            except Exception as e:
                print(f"Erro ao processar solicitação: {e}")
    else:
        print('nao ta ')
        while True:     
            dados, endereco_cliente = servidor_socket.recvfrom(48)  #recebe os dados criptografados

            try:   
            
                resposta_ntp = processa_requisicao_ntp(dados)

                if resposta_ntp:
                    servidor_socket.sendto(resposta_ntp, endereco_cliente)
                
            except Exception as e:
                print(f"Erro ao processar solicitação: {e}")

def processa_requisicao_ntp(dados):

    timestamp_atual = time.time() + 2208988800  #converte para NTP

    fracao = int((timestamp_atual - int(timestamp_atual)) * (2**32)) #sla porque

    try:
        solicitacao_ntp = struct.unpack("!12I", dados)
        li_vn_mode = (0 << 6) | (4 << 3) | 4

        # Combina a parte inteira e fracionária dos timestamps
        
        
        resposta_ntp = struct.pack(
            #"!BBBBIIIQQQQQQ",
            "!12I",
            #(solicitacao_ntp[0] & 0xFFFFFFC0) | 0x24 | 0x04,
            li_vn_mode,
            1,
            solicitacao_ntp[2],
            solicitacao_ntp[3],
            0,
            0,
            0,
            solicitacao_ntp[8],
            int(timestamp_atual),
            fracao,
            int(timestamp_atual),
            fracao
        )

        print(f"Pacote NTP gerado: {resposta_ntp.hex()}")

        return resposta_ntp
    
    except struct.error as e:
        print(f"Erro ao desempacotar dados: {e}")
        return None

cria_servidor_ntp(PORTA, IP_SERVIDOR)
