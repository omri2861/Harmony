import socket
import login
import sys
from PyQt4 import QtGui
from PyQt4.QtCore import *
import threading

sys.path.insert(0, r'F:\Python\HARMONY\src\server')
import management
from time import sleep

__author__ = "Omri Levy"

"""
The main file of the client program, will run the app and interact with the user and server.
"""

SERVER_IP = "10.0.0.13"
SERVER_PORT = 1729
SERVER_ADDRESS = SERVER_IP, SERVER_PORT
LOGIN_COMMAND = "LOGIN"
BAND_WIDTH = 1024
CONNECTION_ATTEMPTS = 5
SOCKET_TIMEOUT = 2
USERNAME_LEN = 8, 12
PASSWORD_LEN = 8, 14


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
                   " about. If this doesn't work after a few times, please try again later or"
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
        self.sock.settimeout(SOCKET_TIMEOUT)
        self.signals = {
            'connected': False,
            'correct-password': False,
            'correct-username': False,
            'logged-in': False,
            'login_requested': False
        }

        self.username = ""
        self.password = ""

        self.login_window = login.LoginWindow()
        self.login_window.set_login(self.request_login)
        self.login_window.set_signup(feature_not_available)

        self.threads = {
            'login': threading.Thread(target=self.login),
            'establish_connection': threading.Thread(target=self.establish_connection)
        }

        for thread in self.threads.values():
            thread.setDaemon(True)
            thread.start()

    def request_login(self):
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
        while not self.signals['connected']:
            try:
                self.sock.connect(SERVER_ADDRESS)
                self.signals['connected'] = True
            except socket.error, socket.timeout:
                pass

    def login(self):
        """
        This method will send a login message to the server and will then update the class' signals attribute
        accordingly. It should run as a thread, and will only execute a login command if signaled through the class'
        signals.
        :return: None
        """
        while True:
            if self.signals['login_requested'] and self.signals['connected']:
                msg = management.Message(management.LOGIN, self.login_window.get_username(),
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

    def exit_and_logout(self, exit_code):
        """
        Will kill all the running threads, send exit message, etc...
        This should run after app.exec_(), before the termination of the program.
        :parameter exit_code: The exit code given.
        :returns: exit_code
        """
        logout_msg = management.Message(management.LOGOUT, self.username, self.password)
        self.sock.send(str(logout_msg))
        self.sock.close()
        return exit_code


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
