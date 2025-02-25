import socket
import struct
import time

def imprime_pacote_hex(pacote):
    """Imprime um pacote NTP em hexadecimal."""
    for i, byte in enumerate(pacote):
        print(f"Byte {i}: {byte:02X}", end=" ")
        if (i + 1) % 4 == 0:
            print()
    print()

def cria_servidor_ntp(porta=123):

    servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    servidor_socket.bind(("", porta)
                         )
    print(f"Servidor NTP iniciado na porta {porta}...")

    while True:
        try:
            dados, endereco_cliente = servidor_socket.recvfrom(1024)
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
        
        resposta_ntp = struct.pack(
            "!12I",
            (solicitacao_ntp[0] & 0xFFFFFFC7) | 0x24,
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
        return resposta_ntp
    
    except struct.error as e:
        print(f"Erro ao desempacotar dados: {e}")
        return None

cria_servidor_ntp()
