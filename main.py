import socket
import struct
import time
import hashlib
import hmac

PORTA = 123
SECRET_KEY = b"0123456789abcdef0123456789abcdef"
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

def get_tempo_servidor_local(END_Servidor, PORTA, pacote):
    if cripto:
        print('ta criptado.')
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #cria um socket UDP
        sock.settimeout(5)  #timeout de 5 segundos

        pacote_criptografado = criptografar_mensagem(pacote, SECRET_KEY)
        hmac_gerado = gerar_hmac(pacote_criptografado, SECRET_KEY)

        sock.sendto(hmac_gerado, (END_Servidor, PORTA))
        sock.sendto(pacote_criptografado, (END_Servidor, PORTA))

        T1 = time.time() #registra o tempo de envio (Origin Timestamp)

        hmac_recebido, _ = sock.recvfrom(32)  # Recebe o HMAC primeiro
        dados_criptografados, _ = sock.recvfrom(48)  # Recebe os dados criptografados

        if not verificar_hmac(dados_criptografados, SECRET_KEY, hmac_recebido):
            print("Erro: Falha na autenticação do servidor.")
            return None

        dados = descriptografar_mensagem(dados_criptografados, SECRET_KEY)

        T4 = time.time()

        unpacked = struct.unpack('!12I', dados)

        T2 = unpacked[8] - 2208988800
        T3 = unpacked[10] - 2208988800

        T2 = T2 + (unpacked[9] / 2**32)
        T3 = T3 + (unpacked[11] / 2**32)

        offset = ((T2 - T1) + (T3 - T4)) / 2

        correct_time = T4 + offset

        return correct_time
    
    else:
        print('nao ta ')
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #cria um socket UDP
        sock.settimeout(5)  #timeout de 5 segundos

        sock.sendto(pacote, (END_Servidor, PORTA))
        T1 = time.time() #registra o tempo de envio (Origin Timestamp)

        dados, _ = sock.recvfrom(48)  # Recebe os dados

        T4 = time.time()

        unpacked = struct.unpack('!12I', dados)

        T2 = unpacked[8] - 2208988800
        T3 = unpacked[10] - 2208988800

        T2 = T2 + (unpacked[9] / 2**32)
        T3 = T3 + (unpacked[11] / 2**32)

        offset = ((T2 - T1) + (T3 - T4)) / 2

        correct_time = T4 + offset

        return correct_time


def get_tempo_official(END_Servidor, PORTA, pacote):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #cria um socket UDP
    sock.settimeout(5)  #timeout de 5 segundos

    
    sock.sendto(pacote, (END_Servidor, PORTA)) #envia a requisição ao servidor NTP

    T1 = time.time() #registra o tempo de envio (Origin Timestamp)


    dados, _ = sock.recvfrom(48) #recebe a resposta do servidor

    T4 = time.time() #registra o tempo de recebimento (Receive Timestamp)

    unpacked = struct.unpack('!12I', dados) #desempacota os dados do pacote NTP

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


if END_Servidor == '127.0.0.1':
    tempo = get_tempo_servidor_local(END_Servidor, PORTA, pacote)
else:
    tempo = get_tempo_official(END_Servidor, PORTA, pacote)

print(f"Tempo correto (UTC): {time.ctime(tempo)}")

