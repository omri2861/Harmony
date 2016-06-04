import socket
import login
import sys
from PyQt4 import QtGui
import threading
import main_window
from time import sleep
import pickle
import re
from pyaudio import PyAudio

sys.path.insert(0, r'F:\Python\HARMONY\src\server')
import management

__author__ = "Omri Levy"

"""
The main file of the client program, will run the app and interact with the user and server.
"""

SERVER_IP = "10.0.0.13"
SERVER_PORT = 1729
SERVER_ADDRESS = SERVER_IP, SERVER_PORT
BAND_WIDTH = 1024
CONNECTION_ATTEMPTS = 5
SOCKET_TIMEOUT = 2
USERNAME_LEN = 8, 12
PASSWORD_LEN = 8, 14
FRAMES_PER_REQUEST = 1000


def clean_buffer(sock):
    """
    Cleans the buffer of the sock.
    :param sock: The socket that should be cleaned.
    :return: None
    """
    sock.settimeout(0.01)
    flag = True
    while flag:
        try:
            sock.recv(BAND_WIDTH)
        except socket.timeout:
            flag = False
    sock.settimeout(None)


def receive_full_message(sock):
    """
    Receive the full message which includes all the data from the given socket.
    :param sock: The socket that should be received from.
    :return: A Message object which contains all the data.
    """
    result = sock.recv(BAND_WIDTH)
    bytes_to_read = int(re.findall(re.compile(management.HDTP_SIZE_PATTERN), result)[0])
    bytes_to_read -= len(re.findall(re.compile("DATA:\r\n(.*)", re.DOTALL), result)[0])
    while bytes_to_read > BAND_WIDTH:
        piece = sock.recv(BAND_WIDTH)
        result += piece
        bytes_to_read -= len(piece)
    if bytes_to_read > 0:
        result += sock.recv(bytes_to_read)
    return management.ReceivedMessage(result)


def dialog(text, informative):
    """
    Creates a message dialog that should be executed to display to the user.
    :param text: The main text of the dialog
    :param informative: The informative text of the dialog.
    :return: QtGui.QMessageBox object instance containing the given data.
    """
    msg = QtGui.QMessageBox()
    msg.setIcon(QtGui.QMessageBox.Information)

    msg.setWindowTitle("Info")
    msg.setText(text)
    msg.setInformativeText(informative)
    msg.setStandardButtons(QtGui.QMessageBox.Ok)
    msg.buttonClicked.connect(msg.close)
    return msg


def feature_not_available(feature=None):
    """
    Displays a 'feature not available' message.
    :param feature: The feature's name.
    :return: None
    """
    if not feature:
        text = 'Feature not available'
    else:
        text = "Feature '%s' not available" % feature
    informative = "This application is still being built. Therefore, some Features of it may not yet be available."
    dialog_box = dialog(text, informative)
    dialog_box.exec_()


def server_connection_error_msg():
    """
    Creates a message box that should be displayed to the user, informing him there is no connection to the server.
    :return: A QMessageBox object containing the information.
    """
    text = "Cannot connect to the server."
    informative = ("HARMONY program is constantly trying to connect to the server, so you got nothing to worry"
                   " about. If this doesn't work after a few times, please try again later or "
                   "contact the server administrator.")

    msg = dialog(text, informative)
    msg.setWindowTitle("Error")

    return msg


def error_message_box(excepted):
    """
    Displays a PyQt message box that contains the error's details.
    :param excepted: The Exception object which raised the error.
    :return: None
    """
    msg = QtGui.QMessageBox()
    msg.setIcon(QtGui.QMessageBox.Information)

    msg.setText("An error occurred.")
    msg.setInformativeText("An exception of type %s occurred." % type(excepted))
    msg.setWindowTitle("Error")
    msg.setDetailedText('\n'.join([str(arg) for arg in excepted.args]))
    msg.setStandardButtons(QtGui.QMessageBox.Ok)
    msg.buttonClicked.connect(sys.exit)
    return msg


def presentable_time(seconds):
    """
    Converts the amount of seconds to the format: "mins:secs"
    :param seconds: The amount of seconds, an int
    :return: A string of the presentable time.
    """
    mins = seconds / 60
    if mins < 10:
        mins = "0%d" % mins
    else:
        mins = str(mins)
    secs = seconds % 60
    if secs < 10:
        secs = "0%d" % secs
    else:
        secs = str(secs)
    return mins + ":" + secs


def presentable_to_seconds(time):
    """
    Translates time from string to int.
    :param time: string indicating time in the following format: "mins:secs"
    :return: The amount of seconds
    """
    mins = int(time.split(':')[0])
    secs = int(time.split(':')[1])
    return (mins * 60) + secs


class Stream(object):
    """
    This class will help the client stream wav frames from the server.
    """
    def __init__(self, file_path, info=None):
        """
        Initializes a stream object.
        :param file_path: The server file path of the song.
        :param info: A dictionary containing the stream's information. If empty, a string will not be created.
        """
        self.file_path = file_path
        self.output = None
        self.streamer = None
        self.current_frame = 0
        self.current_secs = 0
        self.frame_count = 0
        self.frame_rate = 0
        if type(info) is dict:
            self.set_stream_info(info)

    def set_stream_info(self, info):
        """
        Sets the stream settings such as format, channels, framerate and so on.
        :param info: A dictionary containing the song framerate,
        :return:
        """
        if type(info) is not dict:
            return
        self.streamer = PyAudio()
        self.output = self.streamer.open(
            format=self.streamer.get_format_from_width(info['width']),
            channels=info['channels'],
            rate=info['framerate'],
            output=True
        )
        self.frame_rate = info['framerate']

    def play_frames(self, frame_count, frames):
        """
        This method will receive the frames which should be played, output them and will update the stream parameters
        accordingly.
        :param frame_count: How many frames were given.
        :param frames: The raw data of the frames.
        :return: None
        """
        if self.output is not None:
            self.output.write(frames)
            self.current_frame += frame_count
            if int(self.current_frame / self.frame_rate) > self.current_secs:
                self.current_secs += 1

    def close(self):
        """
        Closes the stream.
        :return: None
        """
        if self.output is not None:
            self.output.close()
            del self.output
            self.output = None
            self.streamer.terminate()
            del self.streamer
            self.streamer = None

    def reset(self, file_path, info=None):
        """
        This method will re- set the object so a the stream will play a new song.
        :param file_path: The new song's file path.
        :param info: The new song's information dictionary.
        :return: None
        """
        if self.output is not None or self.streamer is not None:
            self.close()
        self.__init__(file_path, info)


class ThreadedClient(object):
    """
    This class is meant to help the client program execute blocking commands from the GUI window while still responding
    to the user's requests and Managing the program's data.
    This class is threaded, meaning it constantly runs all the threads, but signals them to execute their given commands
    only if needed, through an attribute called 'signals'. This is a logical solution for the fact that running
    complicated or blocking functions makes the GUI windows: 'not responding'. Figure it out windows!!
    """
    def __init__(self):
        """
        Sets up all the GUI windows and starts all the threads.
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.signals = {
            'connected': False,
            'correct-password': False,
            'correct-username': False,
            'logged-in': False,
            'login_requested': False,
            'stream': True
        }

        self.username = ""
        self.password = ""

        self.stream = None
        self.songs_file_paths = {}

        self.login_window = login.LoginWindow()
        self.login_window.set_login(self.onLogin)
        self.login_window.set_signup(feature_not_available)

        self.main_frame = main_window.MainWindow()
        self.main_frame.logout_button.clicked.connect(self.onLogout)
        self.main_frame.delete_button.clicked.connect(feature_not_available)
        self.main_frame.upload_button.clicked.connect(feature_not_available)
        self.main_frame.stop_button.clicked.connect(self.onStop)
        self.main_frame.play_button.clicked.connect(self.onPlay)
        self.selected_row = None

        self.threads = {
            'login': threading.Thread(target=self.login),
            'establish_connection': threading.Thread(target=self.establish_connection),
            'update_time_display': threading.Thread(target=self.update_time_display),
            'on_selection_change': threading.Thread(target=self.on_selection_change)
        }

        for thread in self.threads.values():
            thread.setDaemon(True)
            thread.start()

    def update_time_display(self):
        """
        Constantly updates the time display of the main window.
        Should be threaded.
        :return: None
        """
        while True:
            if self.stream is None:
                self.main_frame.update_time_display(0)
            else:
                self.main_frame.update_time_display(self.stream.current_secs)

    def receive_songs_data(self):
        """
        Receives the songs data from the server.
        :return: None
        """
        msg = receive_full_message(self.sock)
        songs_properties = pickle.loads(msg.get_data()['data'])
        for song_dict in songs_properties:
            song_dict['length'] = presentable_time(song_dict['time_secs'])
            song_title = song_dict['title']
            self.songs_file_paths[song_title] = song_dict['file_path']
            self.main_frame.add_song(song_dict)

    def onLogin(self):
        """
        This method will check if it is possible to send a login message to the server. If so, it will signal the thread
        which is taking care of the login to send a message to the server. It will respond to the user with the correct
        dialog box.
        :return: None
        """
        if self.signals['connected'] and USERNAME_LEN[0] <= len(self.login_window.get_username()) <= USERNAME_LEN[1] \
                and PASSWORD_LEN[0] <= len(self.login_window.get_password()) <= PASSWORD_LEN[1]:
            self.signals['login_requested'] = True

            if self.login_window.remember_me():
                feature_not_available('Remember Me')

            while self.signals['login_requested']:
                pass

            if self.signals['logged-in']:
                self.username = self.login_window.get_username()
                self.password = self.login_window.get_password()
                self.login_window.setShown(False)
                self.main_frame.set_label_text("Hello, "+self.username)
                self.main_frame.show()
                self.receive_songs_data()
            elif self.signals['correct-username']:
                msg = dialog("Incorrect Password", '')
                msg.exec_()
            else:
                msg = dialog("No such user", "Please register to HARMONY")
                msg.exec_()
        elif not (USERNAME_LEN[0] <= len(self.login_window.get_username()) <= USERNAME_LEN[1]):
            msg = dialog('Wrong length username', 'Please enter a username %d-%d characters long.' % USERNAME_LEN)
            msg.exec_()
        elif not (PASSWORD_LEN[0] <= len(self.login_window.get_password()) <= PASSWORD_LEN[1]):
            msg = dialog('Wrong length password', 'Please enter a password %d-%d characters long.' % PASSWORD_LEN)
            msg.exec_()
        else:
            msg = server_connection_error_msg()
            msg.exec_()

    def establish_connection(self):
        """
        This function will connect the socket of the client to the server.
        It should be ran as a thread, so as long as the client program is not connected to the server, it will keep
        trying to initialize a connection.
        :return: None
        """
        self.signals['connected'] = False
        self.sock.settimeout(SOCKET_TIMEOUT)
        while not self.signals['connected']:
            try:
                self.sock.connect(SERVER_ADDRESS)
                self.signals['connected'] = True
            except socket.error, socket.timeout:
                pass
        self.sock.settimeout(None)

    def login(self):
        """
        This method will send a login message to the server and will then update the class' signals attribute
        accordingly. It should run as a thread, and will only execute a login command if signaled through the class'
        signals.
        :return: None
        """
        while True:
            if self.signals['login_requested'] and self.signals['connected']:
                msg = management.Message(management.HDTP_COMMANDS['login'], self.login_window.get_username(),
                                         self.login_window.get_password())
                self.sock.send(str(msg))
                answer = management.ReceivedMessage(self.sock.recv(BAND_WIDTH))
                if answer.flags & management.HDTP_FLAGS['authorized'] \
                        and answer.flags & management.HDTP_FLAGS['successfull']:
                    self.signals['correct-username'] = True
                    self.signals['correct-password'] = True
                    self.signals['logged-in'] = True
                elif answer.flags & management.HDTP_FLAGS['successfull']:
                    self.signals['correct-username'] = True
                    self.signals['correct-password'] = False
                    self.signals['logged-in'] = False
                else:
                    self.signals['correct-username'] = False
                    self.signals['correct-password'] = False
                    self.signals['logged-in'] = False

                self.signals['login_requested'] = False

    def logout(self):
        """
        Send a logout message to the server.
        :return: None
        """
        logout_msg = management.Message(management.HDTP_COMMANDS['logout'], self.username, self.password)
        self.sock.send(str(logout_msg))
        self.sock.close()  # When the server receives a logout message, it automatically closes the connection.
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        threading.Thread(target=self.establish_connection).start()
        threading.Thread(target=self.main_frame.clear_table).start()
        if self.stream is not None:
            self.stream.close()
        self.signals['correct-username'] = False
        self.signals['correct-password'] = False
        self.signals['logged-in'] = False
        self.main_frame.setShown(False)
        self.login_window.show()

    def onLogout(self):
        """
        Unlike the logout method, which performs a logout from the server, this method should be called when
        the 'logout' button is pressed.
        :return: None
        """
        self.onStop()
        threading.Thread(target=self.logout).start()

    def exit_and_logout(self, exit_code):
        """
        Will kill all the running threads, send exit message, etc...
        This should run after app.exec_(), before the termination of the program.
        :parameter exit_code: The exit code given.
        :returns: exit_code
        """
        if self.sock is not None:
            self.onStop()
        if self.stream is not None:
            self.stream.close()
        if self.signals['logged-in']:
            self.logout()
        elif self.signals['connected']:
            self.sock.close()
        return exit_code

    def on_selection_change(self):
        """
        This method checks if the selected song has changed. If so, it will change the class' properties accordingly.
        This method should be threaded.
        :return: None
        """
        while True:
            if self.main_frame.get_selected_row() != self.selected_row:
                self.selected_row = self.main_frame.get_selected_row()
                self.onStop()

    def start_stream(self):
        """
        Starts streaming the data of the selected song from the server.
        Should be threaded.
        :return: None
        """
        self.signals['stream'] = True
        selected_row = self.main_frame.get_selected_row()
        if selected_row is None:
            return

        song_title = str(self.main_frame.get_selected_tag('title'))  # from unicode, because PyQt4 stores in unicode
        server_song_path = self.songs_file_paths[song_title]
        msg = management.Message(management.HDTP_COMMANDS['info'], self.username, self.password,
                                 {'file_path': server_song_path})
        self.sock.send(str(msg))
        answer = receive_full_message(self.sock)
        if self.stream is None:
            self.stream = Stream(server_song_path, answer.get_data())
        else:
            self.stream.reset(server_song_path, answer.get_data())
        msg_size = answer.get_data()['msg_size']
        frames_per_msg = answer.get_data()['frames_per_msg']
        msg = management.Message(management.HDTP_COMMANDS['stream'], self.username, self.password,
                                 {'file_path': server_song_path})
        self.sock.send(str(msg))
        data = self.sock.recv(msg_size)
        while self.signals['stream'] and data != "":
            self.stream.play_frames(frames_per_msg, data)
            data = self.sock.recv(msg_size)

        msg = management.Message(management.HDTP_COMMANDS['close_song'], self.username, self.password,
                                 {'file_path': server_song_path})
        self.sock.send(str(msg))
        clean_buffer(self.sock)
        self.signals['stream'] = True

    def onStop(self):
        self.signals['stream'] = False
        clean_buffer(self.sock)

    def onPlay(self):
        thread = threading.Thread(target=self.start_stream)
        thread.setDaemon(True)
        thread.start()


def main():
    """
    The main function of the program.
    :return: None
    """
    app = QtGui.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    client = None

    try:
        client = ThreadedClient()
        client.login_window.show()
    except socket.error:
        msg = server_connection_error_msg()
        msg.exec_()
    except Exception as ex:
        box = error_message_box(ex)
        box.exec_()

    if client:
        sys.exit(client.exit_and_logout(app.exec_()))
    else:
        sys.exit(app.exec_())


if __name__ == '__main__':
    main()
