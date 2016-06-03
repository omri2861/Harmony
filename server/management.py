import os
import re
import wave
from pydub import AudioSegment as audioseg
import eyed3
import pickle
import copy
import threading

"""
This module contains objects that helps the server manage it's users, songs and other data.
"""
VERSION = 1.1

LINE_BREAK = "\r\n"
USERNAME_LEN_RANGE = 8, 12
PASSWORD_LEN_RANGE = 8, 14
USER_STR_FORMAT = "USERNAME: %s\nPASSWORD: %s" + LINE_BREAK
DATABASE_USERNAME_PATTERN = "USERNAME: (.{%d,%d})\n" % USERNAME_LEN_RANGE
DATABASE_PASSWORD_PATTERN = "PASSWORD: (.{%d,%d})" % PASSWORD_LEN_RANGE
DATABASE_PATH = os.curdir + os.sep + 'users' + os.sep + "database.txt"
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
    "DATA:" + LINE_BREAK + "%s"
)
HDTP_FLAGS = {
    "authorized": 0b00000010,
    "successfull": 0b00000001
}
HDTP_COMMANDS = {
    'login': 'LOGIN',
    'logout': 'LOGOUT',
    'tags': 'TAGS'
}
HDTP_SIZE_PATTERN = "SIZE: ([0-9]*)"
HDTP_DATA_PATTERN = "DATA:" + LINE_BREAK + "(.*)"


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

        songs_paths = [os.path.join(self.dir, song_path) for song_path in os.listdir(self.dir) if song_path.endswith('.mp3')]
        self.songs = [Song(song_path) for song_path in songs_paths]
        
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
        return USER_STR_FORMAT % (self._username, self._password)

    def get_songs_properties(self):
        """
        :return: A pickled string of a of a list containing the user's songs properties.
        """
        songs_properties = []
        for song in self.songs:
            songs_properties.append(song.properties)
        return pickle.dumps(songs_properties)


class NewUser(User):
    """
    The User class can only be initiated through a given string. This class only overrides User's __init__ method, so it
    could be initialized with given parameters.
    """
    def __init__(self, username, password):
        super(NewUser, self).__init__(USER_STR_FORMAT % (username, password))


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
    def __init__(self, request_type, username, password, data=None, flags=0b11111111):
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

    def set_data(self, data_dict):
        """
        The data_dict of the message is a private property, and is not just a simple dictionary, but a modified one to match
        the HDTP protocol. Therefore, in order to change the data_dict, the programmer must use this method.
        :param data_dict: The new data dictionary.
        :return: None
        """
        if data_dict is None or type(data_dict) is not dict:
            self._data = ""
            return
        self._data = '&'.join(['%s=%s' % (key, data_dict[key].encode('base64')) for key in data_dict.keys()])

    def get_data(self):
        """
        As the data is modified to match the HDTP protocol, in order to access it, this method should be called to
        return an accessible copy of the data as a dictionary.
        :return: A dictionary of the message's data.
        """
        result = {}
        for attr in self._data.split('&'):
            key, value = attr.split('=', 1)[0], attr.split('=', 1)[1]
            result[key] = value.decode('base64').rstrip()
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
        if re.findall(re.compile(HDTP_PATTERN), raw_msg):
            request, username, password, flags, size, data = re.findall(re.compile(HDTP_PATTERN), raw_msg)[0]
            data = re.findall(re.compile(HDTP_DATA_PATTERN, re.DOTALL), raw_msg)[0]
            flags = int(flags)
        else:
            username = None
            password = None
            request = None
            data = {}
            flags = 0b11111111
        super(ReceivedMessage, self).__init__(request, username, password, flags=flags)
        self._data = data  # this is because when taken from a raw message, there is no need to format a data dictionary
        #  to  str again


class Song(object):
    """
    This class is meant to help harmony to manage it's songs.
    """
    def __init__(self, filename):
        """
        :param filename: A valid mp3 file stored on the server.
        """
        if os.path.isfile(filename) and filename.endswith('mp3'):
            self.mp3_path = filename
            self.wav_path = filename.replace('.mp3', '.wav')

            properties_analyzer = eyed3.load(self.mp3_path)
            self.properties = {
                'artist': copy.copy(properties_analyzer.tag.artist),
                'title': copy.copy(properties_analyzer.tag.title),
                'album': copy.copy(properties_analyzer.tag.album),
                'time_secs': properties_analyzer.info.time_secs
            }

            properties_analyzer.tag.save()

            if self.properties['title'] is None:
                self.properties['title'] = self.mp3_path[self.mp3_path.rindex(os.sep):self.mp3_path.rindex('.')]

            for field in self.properties.keys():
                if self.properties[field] is None:
                    self.properties[field] = "Unknown"
                elif type(self.properties[field]) is unicode:
                    self.properties[field] = str(self.properties[field])

            if not os.path.isfile(self.wav_path):
                threading.Thread(target=self.convert_to_wav).start()

            self.info = {}
        else:
            raise ValueError("HARMONY only supports existing mp3 files.\nFile Given:\n%s\n" % filename)

    def load_data(self):
        """
        This method will load the wave dile data to the class in order to stream. It will not be loaded with the
        init method due to efficiency.
        :return: None
        """
        info_analyzer = wave.Wave_read(self.wav_path)
        self.info = {
            'frames': info_analyzer.getnframes(),
            'channels': info_analyzer.getnchannels(),
            'frame_rate': info_analyzer.getframerate(),
            'width': info_analyzer.getsampwidth()
        }

        info_analyzer.close()

    def convert_to_wav(self):
        """
        This method will convert the mp3 song file to wav, so the server could handle it's data.
        :return: None
        """
        audioseg.from_mp3(self.mp3_path).export(self.wav_path, 'wav')
