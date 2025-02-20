import socket
import struct
import time
import os

PORTA = 123

# função  principal
def Cliente():
   print()
   
def Servidor( parâmetros_de_f ):
      print()

def cria_pacote_ntp():
    # Versão 3, modo cliente
    versao_e_modo = (3 << 3) | 3

    # Outros campos (inicializados com zero)
    camada = 0
    precisao = 0
    Poll = 0
    atraso_raiz = 0
    dispersao_raiz = 0
    id_referencia = 0
    carimbo_de_tempo_origem = 0
    carimbo_de_tempo_recebimento = 0
    carimbo_de_tempo_transmissao = 0

    # Estrutura do pacote NTP
    pacote = bytearray(48)  # Cria um bytearray de 48 bytes preenchido com zeros

    # Empacota os campos no bytearray
    struct.pack_into(
        "!B B b b I I I Q Q Q",
        pacote,
        0,  # Deslocamento inicial
        versao_e_modo,
        camada,
        precisao,
        Poll, 
        atraso_raiz,
        dispersao_raiz,
        id_referencia,
        carimbo_de_tempo_origem,
        carimbo_de_tempo_recebimento,
        carimbo_de_tempo_transmissao,
    )

    return pacote
  
def Servidor_teclado():
    END_Servidor = input('Por favor digite o server: ')
    print('O SERVER É:', END_Servidor)

    if not END_Servidor:
        END_Servidor = "a.st1.ntp.br"

    return END_Servidor      

def imprime_pacote_hex(pacote):
    """Imprime um pacote NTP em hexadecimal."""

    for i, byte in enumerate(pacote):
        print(f"Byte {i}: {byte:02X}", end=" ")
        if (i + 1) % 4 == 0:
            print()  # Quebra de linha a cada 4 bytes
    print()


def get_tempo(END_Servidor, PORTA, pacote):
    #imprime_pacote_hex(pacote)

    # Cria um socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)  # Timeout de 5 segundos

    
    # Envia a requisição ao servidor NTP
    sock.sendto(pacote, (END_Servidor, PORTA))

    # Registra o tempo de envio (Origin Timestamp)
    T1 = time.time()

    # Recebe a resposta do servidor
    data, _ = sock.recvfrom(48)

    # Registra o tempo de recebimento (Receive Timestamp)
    T4 = time.time()

    # Desempacota os dados do pacote NTP
    unpacked = struct.unpack('!12I', data)

    # Extrai os timestamps relevantes
    T2 = unpacked[8] - 2208988800  # Receive Timestamp (segundos desde 1900)
    T3 = unpacked[10] - 2208988800  # Transmit Timestamp (segundos desde 1900)

    # Converte os timestamps para segundos desde 1970 (epoch)
    T2 = T2 + (unpacked[9] / 2**32)  # Adiciona a fração de segundos
    T3 = T3 + (unpacked[11] / 2**32)  # Adiciona a fração de segundos

    # Calcula o offset e o tempo correto
    offset = ((T2 - T1) + (T3 - T4)) / 2
    correct_time = T4 + offset
    
    return correct_time

    
# início da execução do programa
#-----------------------------------------------------
END_Servidor = Servidor_teclado()
pacote = cria_pacote_ntp()  


try:
        correct_time = get_tempo(END_Servidor, PORTA, pacote)
        print(f"Tempo correto (UTC): {time.ctime(correct_time)}")
except Exception as e:
        print(f"Erro ao obter o tempo NTP: {e}")
