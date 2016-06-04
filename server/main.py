import socket
import management
import select
import re

"""
This program is the server of the 'HARMONY' project.
It is the main program of the server, managing the database and taking care of the online users' requests.
"""


def get_self_ip():
    """
    :return: The machine's IP on the local network.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("gmail.com",80))
    ip = s.getsockname()[0]
    s.close()
    return ip

MAX_CLIENTS = 5
SELF_PORT = 1729
SELF_IP = get_self_ip()
SELF_ADDRESS = SELF_IP, SELF_PORT
SERVER_SOCK_TIMEOUT = 5
BAND_WIDTH = 1024
FRAMES_PER_MESSAGE = 10000
FRAME_SIZE = 4


def accept_login(sock, msg, manager, waiting_messages):
    """
    This method will receive a LOGIN message from the client, and will check if the user is registered in the database
    and can log in to the server.
    If so, it will update the parameters accordingly.
    :param sock: The socket the message should be received from.
    :param msg: A management.Message object containing the received message.
    :param manager: The manager class object used by the server.
    :param waiting_messages: A list of the waiting messages and their sockets.
    :return: A management.User object if the user could be logged in, None otherwise.
    """
    if msg.request != management.HDTP_COMMANDS['login']:
        return None
    user = manager.get_user_by_name(msg.username)
    if user is not None:
        if user.is_authorized(msg.password):
            return_msg = management.Message(management.HDTP_COMMANDS['login'], msg.username, msg.password, str(user))
        else:
            return_msg = management.Message(management.HDTP_COMMANDS['login'], msg.username, msg.username)
            return_msg.flags ^= management.HDTP_FLAGS['authorized']
    else:
        return_msg = management.Message(management.HDTP_COMMANDS['login'], msg.username, msg.username)
        return_msg.flags ^= management.HDTP_FLAGS['successfull']
    waiting_messages.append((sock, str(return_msg)))
    if user is not None and user.is_authorized(msg.password):
        data_msg = management.Message(management.HDTP_COMMANDS['tags'], msg.username, msg.password,
                                      {'data': user.get_songs_properties()})
        waiting_messages.append((sock, str(data_msg)))
        return user


def receive_and_handle_msg(client, online_clients, manager, waiting_messages, open_songs):
    """
    This function will receive a message from a client and will then handle it's request.
    It will update the given parameters accordingly.
    :param client: A tuple which contains the user object and it's socket.
    :param online_clients: The list of connected clients, each client is a tuple: (user, socket).
    :param manager: The database manager object of the running server.
    :param waiting_messages: The list of messages waiting to be sent to the clients.
    :param open_songs: A list of the songs which are currently being streamed.
    :return: None
    """
    user, sock = client
    try:
        raw_msg = sock.recv(BAND_WIDTH)
    except socket.error:
        online_clients.remove(client)
        return
        # Connection was forcibly closed from the client side during runtime

    if not re.findall(re.compile(management.HDTP_PATTERN), raw_msg):
        return
        # The sender is not using HDTP protocol, so I can't take him seriously.

    msg = receive_full_message(raw_msg, sock)

    if msg.request == management.HDTP_COMMANDS['login']:
        new_user = accept_login(sock, msg, manager, waiting_messages)
        try:
            online_clients.remove((None, sock))
            # Delete the temporary user that was added when the server socket accepted the client.
        except ValueError:
            pass  # This user is connected on another device so there is no need to delete a temporary version of him,
        # just add a new one.
        online_clients.append((new_user, sock))

    elif not user.is_authorized(msg.password):
        return

    elif msg.request == management.HDTP_COMMANDS['logout']:
        sock.close()
        online_clients.remove(client)

    elif msg.request == management.HDTP_COMMANDS['info']:
        song_info(msg, user, sock, waiting_messages)

    elif msg.request == management.HDTP_COMMANDS['stream']:
        stream_song(msg, user, open_songs, sock)

    elif msg.request == management.HDTP_COMMANDS['close_song']:
        close_song(msg, sock, open_songs)


def stream_song(msg, user, open_songs, sock):
    """

    :param msg:
    :param user:
    :param open_songs:
    :param sock:
    :return:
    """
    song_path = msg.get_data()['file_path']
    song = user.get_song_by_path(song_path)
    open_songs.append((sock, song))


def song_info(msg, user, sock, waiting_messages):
    """

    :param msg:
    :param user:
    :param sock:
    :param waiting_messages:
    :return:
    """
    song_path = msg.get_data()['file_path']
    song = user.get_song_by_path(song_path)
    song.open_data()
    return_msg = management.Message(msg.request, msg.username, msg.password, song.info)
    return_msg_data = return_msg.get_data()
    return_msg_data['msg_size'] = FRAMES_PER_MESSAGE * FRAME_SIZE
    return_msg_data['frames_per_msg'] = FRAMES_PER_MESSAGE
    return_msg.set_data(return_msg_data)
    waiting_messages.append((sock, str(return_msg)))


def close_song(msg, sock, open_songs):
    """

    :param msg:
    :param sock:
    :param open_songs:
    :return:
    """
    song_path = msg.get_data()['file_path']
    song = find_song_by_path(song_path, [song for sock, song in open_songs])
    song.close_data()
    open_songs.remove((sock, song))


def find_song_by_path(song_path, songs_list):
    """
    Finds the management.Song object according to the given song_path path.
    :param song_path: The song_path path.
    :param songs_list: The list of the songs objects.
    :return: management.Song which matches the song_path path. If not found, returns None.
    """
    for song in songs_list:
        if song.properties['file_path'] == song_path:
            return song
    return None


def delete_client_by_sock(sock, clients):
    """
    Given a list of clients, and a socket, deletes a client from the list according to it's socket.
    :param sock: The socket which belongs to the user that should be deleted.
    :param clients: The list which the socket should be deleted from.
    :return: None
    """
    for client in clients:
        if client[1] == sock:
            clients.remove(client)
            break


def receive_full_message(msg, sock):
    """
    Receive the full message which includes all the data from the given socket.
    :param msg: The first part of the message already received.
    :param sock: The socket that should be received from.
    :return: A Message object which contains all the data.
    """
    result = msg
    bytes_to_read = int(re.findall(re.compile(management.HDTP_SIZE_PATTERN), msg)[0])
    bytes_to_read -= len(re.findall(re.compile("DATA:\r\n(.*)", re.DOTALL), msg)[0])
    while bytes_to_read > BAND_WIDTH:
        piece = sock.recv(BAND_WIDTH)
        result += piece
        bytes_to_read -= len(piece)
    if bytes_to_read > 0:
        result += sock.recv(bytes_to_read)
    return management.ReceivedMessage(result)


def send_messages(messages, writable):
    """
    This function will send the messages that are waiting to be sent to the server.
    :param messages: The list of waiting messages, each cell contains the socket and the message.
    :param writable: The lists of sockets that can receive a message.
    :return: None
    """
    for sock, msg in messages:
        if sock in writable:
            sock.send(msg)
            writable.remove(sock)
            messages.remove((sock, msg))


def get_user_by_socket(sock, clients):
    """
    Finds the user in the client's list according to the given socket.
    :param sock: The user's socket.
    :param clients: A list tuples containing the online clients (user, socket).
    :return:
    """
    for client in clients:
        user, user_sock = client
        if user_sock == sock:
            return user


def send_songs_data(open_songs, waiting_messages):
    """
    This function will add data of open songs to the waiting messages.
    :param open_songs: The list of songs which are currently streaming.
    :param waiting_messages: The list of the messages waiting to be sent to the clients.
    :return:
    """
    for sock, song in open_songs:
        frames = song.read_frames(FRAMES_PER_MESSAGE)
        waiting_messages.append((sock, frames))
        print "sending..."


def main():
    """
    The main function of the server, will take care of all the requests and run the server.
    :return: None
    """
    database_manager = management.Manager()
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clients = []
    running = True
    waiting_messages = []
    open_songs = []

    server_sock.settimeout(SERVER_SOCK_TIMEOUT)
    server_sock.bind(SELF_ADDRESS)
    server_sock.listen(MAX_CLIENTS)

    while running:
        clients_sockets = [client[1] for client in clients]
        readable, writable, excepted = select.select([server_sock]+clients_sockets, clients_sockets, clients_sockets)
        for sock in excepted:
            if sock in readable:
                readable.remove(sock)
            if sock in writable:
                writable.remove(sock)
        for sock in readable:
            if sock is server_sock:
                new_client, new_address = sock.accept()
                clients.append((None, new_client))
                #  temporarily inserting None as a user, as this will be taken care of when the client will send a login
                #  message
            else:
                sending_user = get_user_by_socket(sock, clients)
                receive_and_handle_msg((sending_user, sock), clients, database_manager, waiting_messages, open_songs)
        send_songs_data(open_songs, waiting_messages)
        send_messages(waiting_messages, writable)


if __name__ == '__main__':
    main()
