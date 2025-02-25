import socket
import struct
import time
import os

PORTA = 123

def cria_pacote_ntp():
    versao_e_modo = (3 << 3) | 3 #versão 3, modo cliente

    camada = 0
    precisao = 0
    Poll = 0
    atraso_raiz = 0
    dispersao_raiz = 0
    id_referencia = 0
    carimbo_de_tempo_origem = 0
    carimbo_de_tempo_recebimento = 0
    carimbo_de_tempo_transmissao = 0

    
    pacote = bytearray(48)  #cria um bytearray de 48 bytes preenchido com zeros

    #empacota os campos no bytearray
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
   
    if not END_Servidor:
        END_Servidor = "a.st1.ntp.br"
        
    print('O SERVER É:', END_Servidor)
    return END_Servidor      

def imprime_pacote_hex(pacote):

    for i, byte in enumerate(pacote):
        print(f"Byte {i}: {byte:02X}", end=" ")
        if (i + 1) % 4 == 0:
            print()
    print()


def get_tempo(END_Servidor, PORTA, pacote):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #cria um socket UDP
    sock.settimeout(5)  #timeout de 5 segundos

    sock.sendto(pacote, (END_Servidor, PORTA)) #envia a requisição ao servidor NTP

    T1 = time.time() #registra o tempo de envio (Origin Timestamp)

    data, _ = sock.recvfrom(48) #recebe a resposta do servidor

    T4 = time.time() #registra o tempo de recebimento (Receive Timestamp)

    unpacked = struct.unpack('!12I', data) #desempacota os dados do pacote NTP

    #extrai os timestamps relevantes
    T2 = unpacked[8] - 2208988800  #receive Timestamp (converte para época Unix)
    T3 = unpacked[10] - 2208988800  #transmit Timestamp (converte para época Unix)

    #converte os timestamps para segundos
    T2 = T2 + (unpacked[9] / 2**32)  #adiciona a fração de segundos
    T3 = T3 + (unpacked[11] / 2**32)  #adiciona a fração de segundos

    #calcula o offset e o tempo correto
    offset = ((T2 - T1) + (T3 - T4)) / 2
    correct_time = T4 + offset

    return correct_time
       
# início da execução do programa
#-----------------------------------------------------
END_Servidor = Servidor_teclado()
pacote = cria_pacote_ntp()  

tempo = get_tempo(END_Servidor, PORTA, pacote)
#imprime_pacote_hex(correct_time)

print(f"Tempo correto (UTC): {time.ctime(tempo)}")

