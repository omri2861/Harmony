import os
import re

"""
This module contains objects that helps the server manage it's users, songs and other data.
"""
VERSION = 1.1

USERNAME_LEN_RANGE = 8, 12
PASSWORD_LEN_RANGE = 8, 14
USER_STR_FORMAT = "USERNAME: %s\nPASSWORD: %s\n[\n%s\n]\r\n"
DATABASE_USERNAME_PATTERN = "USERNAME: (.{%d,%d})\n" % USERNAME_LEN_RANGE
DATABASE_PASSWORD_PATTERN = "PASSWORD: (.{%d,%d})\n" % PASSWORD_LEN_RANGE
DATABASE_PATH = os.curdir + os.sep + 'users' + os.sep + "database.txt"
LINE_BREAK = "\r\n"
HDTP_PATTERN = (
    "HARMONY " + str(VERSION) + LINE_BREAK +
    "(.{1,10})" + LINE_BREAK +
    "USERNAME: (.{8,12})" + LINE_BREAK +
    "PASSWORD: (.{8,14})" + LINE_BREAK +
    "FLAGS: ([0-9]*)" + LINE_BREAK +
    "SIZE: ([0-9]*)" + LINE_BREAK +
    "DATA:" + LINE_BREAK + "(.*)"
)
HDTP_FORMAT = (
    "HARMONY " + str(VERSION) + LINE_BREAK +
    "%s" + LINE_BREAK +
    "USERNAME: %s" + LINE_BREAK +
    "PASSWORD: %s" + LINE_BREAK +
    "FLAGS: %d" + LINE_BREAK +
    "SIZE: %d" + LINE_BREAK +
    "DATA:" + LINE_BREAK + "%s" + LINE_BREAK
)
HDTP_FLAGS = {
    "authorized": 0b00000010,
    "successfull": 0b00000001
}
LOGIN = "LOGIN"
LOGOUT = "LOGOUT"
HDTP_SIZE_PATTERN = "SIZE: ([0-9]*)"
HDTP_DATA_PATTERN = "DATA:" + LINE_BREAK + "(.*)" + LINE_BREAK


class User(object):
    """
    This class helps the server maintain it's users and access the information of each user with ease.
    properties:
    - username- The user's username.
    - password- The user's password.
    - dir- The user's directory. Each user has a directory of his songs in the server's machine.
    """
    def __init__(self, info):
        """
        Takes a string which contains the users's information and creates a new user.
        'Info' is the result of an str(User) call.
        """
        try:
            username = re.findall(re.compile(DATABASE_USERNAME_PATTERN), info)[0]
            password = re.findall(re.compile(DATABASE_PASSWORD_PATTERN), info)[0]
        except IndexError:
            username = None
            password = None

        self._username = username
        self._password = password

        self.dir = os.curdir + os.sep + 'users' + os.sep + str(self._username)
        if not os.path.isdir(self.dir):
            os.mkdir(self.dir)

        self.songs = []  # Still needs to be changed
        
    def get_username(self):
        """
        Since the username is private, returns the username.
        :return:
        """
        return self._username

    def is_authorized(self, password):
        """
        Checks if the password given matches the user's password.
        You cannot access the password directly through this class due to security reasons.
        :param password: The password you think is true.
        :return: True if it is the correct password, False otherwise.
        """
        return password == self._password

    def change_password(self, old_password, new_password):
        """
        If the old password matches the user password, a new password for this user will be set.
        :param old_password: The current user password.
        :param new_password: The new password that should be set.
        :return: True if the process was successfull and False otherwise.
        """
        if self.is_authorized(old_password):
            self._password = new_password
            return True
        else:
            return False

    def __eq__(self, other):
        """
        Overwrites the __eq__ method of object.
        :param other: The other user given that should match this instance.
        :return: True if the usernames are the same and False otherwise.
        """
        try:
            return self._username == other.get_username()
        except AttributeError:
            return False

    def __str__(self):
        return USER_STR_FORMAT % (self._username, self._password, '\n'.join(self.songs))


class NewUser(User):
    """
    The User class can only be initiated through a given string. This class only overrides User's __init__ method, so it
    could be initialized with given parameters.
    """
    def __init__(self, username, password):
        super(NewUser, self).__init__(USER_STR_FORMAT % (username, password, ""))


class Manager(object):
    """
    This class will help the server manage the user database with some helpful functions returning only specific things,
    being more productive.
    """
    def __init__(self):
        self.path = DATABASE_PATH
        with open(self.path, 'r') as database:
            self.data = database.read()

    def get_user_by_name(self, username):
        """
        Finds the given user and returns it if the password is correct.
        :param username: The user's username.
        :return: If the user is found in the database, returns a User object. otherwise,
        returns None.
        """
        raw_users = self.data.split('\r\n')[0:-1]   # The last one will always be an empty string
        for info in raw_users:
            user = User(info)
            if user.get_username() == username:
                return user
        return None

    def get_usernames(self):
        """
        Scans the database's users.
        :return: A list of strings which contains the usernames of the database.
        """
        return re.findall(re.compile(DATABASE_USERNAME_PATTERN), self.data)


class Message(object):
    """
    This class helps the server and client to communicate using the HDTP protocol-
        HARMONY DATA TRANSFER PROTOCOL
    It will give easy access to the fields of each message, and the str(Message) call will provide a string that can be
    sent and analyzed by the other side.
    You might notice that this protocol resembles HTTP, but this is not by mistake.
    """
    def __init__(self, request_type, username, password, data="", flags=0b11111111):
        """
        Receives the field of the message and creates the message object.
        :param request_type: A string chosen from the options of the HDTP.
        :param username: The username of the user that sends the message.
        :param password: The password of the user that sends the message, as you need to configure yourself as a user of
        the program in order to make any changes in the server.
        :param data: The data of the message, as a dictionary (data transfer in HDTP is similar to data transfer in
        HTTP, as both are divided to parameters and base64 encoded.
        :param flags: A number, according to HDTP protocol.
        """
        self.request = request_type
        self.username = username
        self.password = password
        self.flags = flags
        self._data = None
        self.set_data(data)

    def set_data(self, data):
        """
        The data of the message is a private property, and is not just a simple dictionary, but a modified one to match
        the HDTP protocol. Therefore, in order to change the data, the programmer must use this method.
        :param data: The new data dictionary.
        :return: None
        """
        self._data = data
        self._data.encode('base64')

    def get_data(self):
        """
        As the data is modified to match the HDTP protocol, in order to access it, this method should be called to
        return an accessible copy of the data.
        :return: A dictionary of the message's data.
        """
        self._data.decode('base64')
        result = self._data
        self._data.encode('base64')
        return result

    def get_size(self):
        """
        :return: The size of the message's data.
        """
        return len(self._data)

    def __len__(self):
        return len(str(self))

    def __str__(self):
        return HDTP_FORMAT % (self.request, self.username, self.password, self.flags, self.get_size(), self._data)


class ReceivedMessage(Message):
    """
    This class only overrides the __init__ method of the Message class, allowing the user to build a message from the
    result of the str(Message) call. In other words, this class is analyzing the HDTP messages received from a socket.
    """
    def __init__(self, raw_msg):
        """
        :param raw_msg: The message received from the socket.
        """
        if re.findall(re.compile(HDTP_PATTERN+LINE_BREAK), raw_msg):
            request, username, password, flags, size, data = re.findall(re.compile(HDTP_PATTERN+LINE_BREAK), raw_msg)[0]
            flags = int(flags)
        else:
            username = None
            password = None
            data = ""
            request = None
            flags = 0b11111111
        super(ReceivedMessage, self).__init__(request, username, password, data, flags)
