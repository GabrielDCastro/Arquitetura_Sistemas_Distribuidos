import socket
import select

Header_length = 10
ip  = "127.0.0.1"
Port = 666

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Criando uma conexão TCP, IPV4
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #Isso modifica o socket para nos permitir reutilizar o endereço

 #Próximos passos fazem o programa escutar e ver se alguém se conecta a ele
server_socket.bind((ip, Port))
server_socket.listen()
#A seguir, vamos criar uma lista de sockets para selecionar para acompanhar
sockets_list = [server_socket]
#Criando lista de clientes
clients = {}

def receive_message(client_socket):
    try:# Para receber uma mensagem etem que ler o cabeçalho
        message_header = client_socket.recv(Header_length)
        # Se um cliente fechar uma conexão normalmente, um socket.close() será emitido e não haverá nenhum cabeçalho. Podemos cuidar disso com:
        if not len(message_header):
            return False
        # Então, podemos converter nosso cabeçalho para um comprimento:
        message_length = int(message_header.decode("utf-8").strip())
        # Retorna objeto do cabeçalho da mensagem e dados da mensagem
        return {"header": message_header, "data": client_socket.recv(message_length)}

    except:
        return False

while True:
    # Vamos ficar recebendo as mensagens "Eternamente" de todos os clientes.
    # Usando select.select aqui para a entrada e saída para nossos soquetes.
    # O que esta função toma como parâmetros é rlist, wlist e xlist, que são lista de leitura, gravação e erros.
    # O retorno desta função são os mesmos 3 elementos onde os retornos são "subconjuntos" das listas de entrada onde o subconjunto é uma lista dos soquetes que estão prontos.
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_socket in read_sockets:
        # Verifica se alguém está conectando ao servidor
        if notified_socket == server_socket:
            # Faz a conexão ínica para cada cliente
            client_socket, client_address  = server_socket.accept()
            # O cliente deve enviar seu nome imediatamente
            user = receive_message(client_socket)
            if user is False:
                continue

            # Aceita o cliente e o adiciona a lista
            sockets_list.append(client_socket)
            # Salva o nome de usuário e cabeçalho
            clients[client_socket] = user
            print(f"Conexão aceita de {client_address[0]}:{client_address[1]} usuário:{user['data'].decode('utf-8')}")

        # Verifica se já estão conectados e fica enviando as mensagens
        else:
            # Recebe mensagens
            message = receive_message(notified_socket)
            # Se a menagem for falsa o cliente é desconectado e liberado da lista
            if message is False:
                print(f"Conexão perdida entre {clients[notified_socket]['data'].decode('utf-8')}")
                # Remove da lista para o socket.socket()
                sockets_list.remove(notified_socket)
                # Remove da lista
                del clients[notified_socket]
                continue

            # Confirmando quem enviou a mensagem
            user = clients[notified_socket]
            print(f"Mensagem recebida pelo {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}")

            for client_socket in clients:
                if client_socket != notified_socket:
                    # Manda usuário e a mensagem dele
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

    # Lidar com algumas exceções, caso ocorram
    for notified_socket in exception_sockets:
        #remove da lista para o socket.socket()
        sockets_list.remove(notified_socket)
        # Remove da lista
        del clients[notified_socket]
