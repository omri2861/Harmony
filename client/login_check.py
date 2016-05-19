import sys
sys.path.insert(0, r'F:\Python\HARMONY\src\server')
import management
import socket

__author__ = 'Omri Levy'


def main():
    """
    The main function of the program.
    """
    username = raw_input("Username:  ")
    password = raw_input("Password:  ")
    login_msg = management.Message(management.LOGIN, username, password)
    my_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_sock.connect(("10.0.0.13", 1729))
    my_sock.send(str(login_msg))
    answer = management.ReceivedMessage(my_sock.recv(1024))
    print str(answer)
    if answer.flags & management.HDTP_FLAGS['authorized'] and answer.flags & management.HDTP_FLAGS['successfull']:
        print "\nLogged in."
    elif answer.flags & management.HDTP_FLAGS['successfull']:
        print "Incorrect password."
    else:
        print "No such user."
    my_sock.close()

if __name__ == '__main__':
    main()
