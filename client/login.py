import resources
import sys
from PyQt4 import QtCore, QtGui
import threading

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class LoginWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.centralwidget = QtGui.QWidget(self)
        self.label = QtGui.QLabel(self.centralwidget)
        self.label_2 = QtGui.QLabel(self.centralwidget)
        self.username_edit = QtGui.QLineEdit(self.centralwidget)
        self.password_edit = QtGui.QLineEdit(self.centralwidget)
        self._remember_me = QtGui.QCheckBox(self.centralwidget)
        self.login_button = QtGui.QPushButton(self.centralwidget)
        self.signup_button = QtGui.QPushButton(self.centralwidget)

        self.setupUi()

        self.signup_button.clicked.connect(self.default_onSignup)

    def setupUi(self):
        self.setObjectName(_fromUtf8("LoginWindow"))
        self.resize(960, 768)
        self.setMinimumSize(QtCore.QSize(960, 768))
        self.setMaximumSize(QtCore.QSize(960, 768))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        self.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("HP Simplified"))
        font.setPointSize(22)
        self.setFont(font)
        self.setStyleSheet(_fromUtf8("border-image: url(:/General/bg.jpg);"))
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.username_edit.setGeometry(QtCore.QRect(360, 240, 240, 40))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("HP Simplified"))
        font.setPointSize(20)
        self.username_edit.setFont(font)
        self.username_edit.setStyleSheet(_fromUtf8("border-image: rgba(255, 255, 255, 0);"))
        self.username_edit.setObjectName(_fromUtf8("username_edit"))
        self.password_edit.setGeometry(QtCore.QRect(360, 330, 240, 40))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("HP Simplified"))
        font.setPointSize(20)
        self.password_edit.setFont(font)
        self.password_edit.setStyleSheet(_fromUtf8("border-image: rgba(255, 255, 255, 0);"))
        self.password_edit.setInputMask(_fromUtf8(""))
        self.password_edit.setText(_fromUtf8(""))
        self.password_edit.setMaxLength(20)
        self.password_edit.setFrame(True)
        self.password_edit.setEchoMode(QtGui.QLineEdit.Password)
        self.password_edit.setObjectName(_fromUtf8("password_edit"))
        self._remember_me.setGeometry(QtCore.QRect(370, 410, 220, 60))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("HP Simplified"))
        font.setPointSize(22)
        font.setStyleStrategy(QtGui.QFont.NoAntialias)
        self._remember_me.setFont(font)
        self._remember_me.setStyleSheet(_fromUtf8("border-image: rgba(255, 255, 255, 0);\n"
"color: rgb(255, 255, 255);"))
        self._remember_me.setObjectName(_fromUtf8("_remember_me"))
        self.login_button.setGeometry(QtCore.QRect(490, 490, 140, 40))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 100))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 100))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 100))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 100))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 100))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 100))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 100))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 100))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 100))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.login_button.setPalette(palette)
        self.login_button.setStyleSheet(_fromUtf8("border-image:rgb(255, 255, 255);\n"
"font: 22pt \"HP Simplified\";\n"
"background-color: rgba(255, 255, 255, 100);\n"
"color: rgb(255, 255, 255);"))
        self.login_button.setObjectName(_fromUtf8("login_button"))
        self.signup_button.setGeometry(QtCore.QRect(330, 490, 140, 40))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 100))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 100))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 100))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 100))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 100))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 100))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 100))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 100))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 100))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.signup_button.setPalette(palette)
        self.signup_button.setStyleSheet(_fromUtf8("border-image:rgb(255, 255, 255);\nfont: 22pt \"HP Simplified\";\n"
                                         "background-color: rgba(255, 255, 255, 100);\ncolor: rgb(255, 255, 255);"))
        self.signup_button.setObjectName(_fromUtf8("signup_button"))
        self.label.setGeometry(QtCore.QRect(305, 50, 360, 130))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("AR BONNIE"))
        font.setPointSize(36)
        self.label.setFont(font)
        self.label.setStyleSheet(_fromUtf8("border-image: rgba(255, 255, 255, 0);\ncolor: rgba(145, 145, 145, 150);"))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2.setGeometry(QtCore.QRect(298, 50, 360, 130))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("AR BONNIE"))
        font.setPointSize(36)
        self.label_2.setFont(font)
        self.label_2.setStyleSheet(_fromUtf8("border-image: rgba(255, 255, 255, 0);\ncolor: rgba(255, 255, 255, 255);"))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.setCentralWidget(self.centralwidget)

        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self, LoginWindow):
        LoginWindow.setWindowTitle(_translate("LoginWindow", "HARMONY- Login", None))
        self.username_edit.setPlaceholderText(_translate("LoginWindow", "Username", None))
        self.password_edit.setPlaceholderText(_translate("LoginWindow", "Password", None))
        self._remember_me.setText(_translate("LoginWindow", "Remember Me", None))
        self.login_button.setText(_translate("LoginWindow", "Login", None))
        self.signup_button.setText(_translate("LoginWindow", "Signup", None))
        self.label.setText(_translate("LoginWindow", "<html><head/><body><p><span style=\" font-size:92pt; font-weight:800;\">HARMONY</span></p></body></html>", None))
        self.label_2.setText(_translate("LoginWindow", "<html><head/><body><p><span style=\" font-size:92pt; font-weight:800;\">HARMONY</span></p></body></html>", None))

    def default_onLogin(self):
        print "Username:%s\nPassword:%s" % (self.username_edit.text(), self.password_edit.text())
        if self._remember_me.isChecked():
            print "You should know that the user wants to be remembered."
        print '\n'

    def default_onSignup(self):
        print "'Signup' pressed."

    def set_login(self, func):
        """
        Sets up the function that should be ran when 'login' is pressed.
        :param func: The function that should be executed.
        :return: None
        """
        self.login_button.clicked.connect(func)

    def set_signup(self, func):
        """
        Sets up the function that should be ran when 'signup' is pressed.
        :param func: The function that should be executed.
        :return: None
        """
        self.signup_button.clicked.connect(func)

    def get_username(self):
        return self.username_edit.text()

    def get_password(self):
        return self.password_edit.text()

    def remember_me(self):
        """
        :return: True if the 'Remember Me' box is checked and False otherwise.
        """
        return self._remember_me.checkState()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    window = LoginWindow()
    window.show()

    sys.exit(app.exec_())
