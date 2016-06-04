import resources
import sys
from PyQt4 import QtCore, QtGui, phonon

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

LABEL_TEXT_FORMAT = "<html><head/><body><p><span style=\" font-size:36pt; font-weight:600; " \
                    "color:#ffffff;\">%s</span></p></body></html>"
LABEL_SHADOW_TEXT_FORMAT = "<html><head/><body><p><span style=\" font-size:36pt; font-weight:600; " \
                    "color:#adadad;\">%s</span></p></body></html>"

TABLE_COLUMN_INDEX = {
    'title': 0,
    'artist': 1,
    'album': 2,
    'length': 3

}


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


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.centralwidget = QtGui.QWidget(self)
        self.table = QtGui.QTableWidget(self.centralwidget)
        self.time_slider = QtGui.QSlider(self.centralwidget)
        self.time_display = QtGui.QLCDNumber(self.centralwidget)
        self.label = QtGui.QLabel(self.centralwidget)
        self.label_shadow = QtGui.QLabel(self.centralwidget)
        self.upload_button = QtGui.QPushButton(self.centralwidget)
        self.play_button = QtGui.QPushButton(self.centralwidget)
        self.stop_button = QtGui.QPushButton(self.centralwidget)
        self.delete_button = QtGui.QPushButton(self.centralwidget)
        self.logout_button = QtGui.QPushButton(self.centralwidget)

        self.setupUi()

        self.time_display.display("00:00")
        self.table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)

    def setupUi(self):
        self.setObjectName(_fromUtf8("self"))
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
        self.table.setGeometry(QtCore.QRect(30, 90, 710, 440))
        self.table.setStyleSheet(_fromUtf8("border-image: rgba(255, 255, 255, 0);\n"
                                           "selection-background-color: rgba(130, 130, 130, 100);\n"
                                           "selection-color: rgb(255, 255, 255);\n"
                                           "gridline-color: rgb(255, 255, 255);\n"
                                           "border-color: rgb(255, 255, 255);\n"
                                           "background-color: rgba(255, 255, 255, 0);\n"
                                           "colort:rgb(255, 255, 255);"))
        self.table.setFrameShape(QtGui.QFrame.StyledPanel)
        self.table.setFrameShadow(QtGui.QFrame.Sunken)
        self.table.setLineWidth(1)
        self.table.setMidLineWidth(0)
        self.table.setGridStyle(QtCore.Qt.SolidLine)
        self.table.setWordWrap(False)
        self.table.setObjectName(_fromUtf8("table"))
        self.table.setColumnCount(4)
        self.table.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.table.setVerticalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(3, item)
        self.table.horizontalHeader().setDefaultSectionSize(173)
        self.time_slider.setGeometry(QtCore.QRect(30, 570, 710, 22))
        self.time_slider.setStyleSheet(_fromUtf8("border-image: rgba(255, 255, 255, 0);"))
        self.time_slider.setOrientation(QtCore.Qt.Horizontal)
        self.time_slider.setObjectName(_fromUtf8("time_slider"))
        self.time_slider.setMaximum(100)
        self.time_display.setGeometry(QtCore.QRect(560, 620, 180, 60))
        self.time_display.setStyleSheet(_fromUtf8("border-image: rgba(255, 255, 255, 0);\n"
"color: rgb(255, 255, 255);"))
        self.time_display.setObjectName(_fromUtf8("time_display"))
        self.label.setGeometry(QtCore.QRect(30, 0, 491, 91))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Gadugi"))
        font.setPointSize(28)
        font.setBold(False)
        font.setItalic(True)
        font.setWeight(50)
        self.label.setFont(font)
        self.label.setStyleSheet(_fromUtf8("border-image: rgba(255, 255, 255, 0);\n"
"font: italic 28pt \"Gadugi\";"))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_shadow.setGeometry(QtCore.QRect(35, 0, 491, 91))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Gadugi"))
        font.setPointSize(28)
        font.setBold(False)
        font.setItalic(True)
        font.setWeight(50)
        self.label_shadow.setFont(font)
        self.label_shadow.setStyleSheet(_fromUtf8("border-image: rgba(255, 255, 255, 0);\n"
"font: italic 28pt \"Gadugi\";"))
        self.label_shadow.setObjectName(_fromUtf8("label_shadow"))
        self.upload_button.setGeometry(QtCore.QRect(790, 430, 140, 40))
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
        self.upload_button.setPalette(palette)
        self.upload_button.setStyleSheet(_fromUtf8("border-image:rgb(255, 255, 255);\n"
"font: 22pt \"HP Simplified\";\n"
"background-color: rgba(255, 255, 255, 100);\n"
"color: rgb(255, 255, 255);"))
        self.upload_button.setObjectName(_fromUtf8("upload_button"))
        self.play_button.setGeometry(QtCore.QRect(30, 630, 140, 40))
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
        self.play_button.setPalette(palette)
        self.play_button.setStyleSheet(_fromUtf8("border-image:rgb(255, 255, 255);\n"
"font: 22pt \"HP Simplified\";\n"
"background-color: rgba(255, 255, 255, 100);\n"
"color: rgb(255, 255, 255);"))
        self.play_button.setObjectName(_fromUtf8("play_button"))
        self.stop_button.setGeometry(QtCore.QRect(195, 630, 140, 40))
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
        self.stop_button.setPalette(palette)
        self.stop_button.setStyleSheet(_fromUtf8("border-image:rgb(255, 255, 255);\n"
"font: 22pt \"HP Simplified\";\n"
"background-color: rgba(255, 255, 255, 100);\n"
"color: rgb(255, 255, 255);"))
        self.stop_button.setObjectName(_fromUtf8("stop_button"))
        self.delete_button.setGeometry(QtCore.QRect(790, 490, 140, 40))
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
        self.delete_button.setPalette(palette)
        self.delete_button.setStyleSheet(_fromUtf8("border-image:rgb(255, 255, 255);\n"
"font: 22pt \"HP Simplified\";\n"
"background-color: rgba(255, 255, 255, 100);\n"
"color: rgb(255, 255, 255);"))
        self.delete_button.setObjectName(_fromUtf8("delete_button"))
        self.logout_button.setGeometry(QtCore.QRect(790, 700, 140, 40))
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
        self.logout_button.setPalette(palette)
        self.logout_button.setStyleSheet(_fromUtf8("border-image:rgb(255, 255, 255);\n"
"font: 22pt \"HP Simplified\";\n"
"background-color: rgba(255, 255, 255, 100);\n"
"color: rgb(255, 255, 255);"))
        self.logout_button.setObjectName(_fromUtf8("logout_button"))
        self.label_shadow.raise_()
        self.table.raise_()
        self.time_slider.raise_()
        self.time_display.raise_()
        self.label.raise_()
        self.upload_button.raise_()
        self.play_button.raise_()
        self.stop_button.raise_()
        self.delete_button.raise_()
        self.logout_button.raise_()
        self.setCentralWidget(self.centralwidget)

        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self, MainFrame):
        self.setWindowTitle(_translate("HARMONY", "HARMONY", None))
        self.table.setSortingEnabled(False)
        item = self.table.horizontalHeaderItem(0)
        item.setText(_translate("MainFrame", "Title", None))
        item = self.table.horizontalHeaderItem(1)
        item.setText(_translate("MainFrame", "Artist", None))
        item = self.table.horizontalHeaderItem(2)
        item.setText(_translate("MainFrame", "Album", None))
        item = self.table.horizontalHeaderItem(3)
        item.setText(_translate("MainFrame", "Length", None))
        self.label.setText(_translate("MainFrame", "<html><head/><body><p><span style=\" font-size:36pt; font-weight:600; color:#ffffff;\">Hello, 123456789012</span></p></body></html>", None))
        self.label_shadow.setText(_translate("MainFrame", "<html><head/><body><p><span style=\" font-size:36pt; font-weight:600; color:#adadad;\">Hello, 123456789012</span></p></body></html>", None))
        self.upload_button.setText(_translate("MainFrame", "Upload", None))
        self.play_button.setText(_translate("MainFrame", "Play", None))
        self.stop_button.setText(_translate("MainFrame", "Stop", None))
        self.delete_button.setText(_translate("MainFrame", "Delete", None))
        self.logout_button.setText(_translate("MainFrame", "Logout", None))

    def set_label_text(self, text):
        """
        Setting the text in the window requires a few commands that the user of the MainWindow shouldn't deal with.
        Therefore, this method has been made.
        :param text: The text that should be displayed in the main label.
        :return: None
        """
        self.label.setText(_translate("MainFrame", LABEL_TEXT_FORMAT % text, None))
        self.label_shadow.setText(_translate("MainFrame", LABEL_SHADOW_TEXT_FORMAT % text, None))

    def add_song(self, properties):
        """
        This method will add another song to the table.
        :param properties: A dictionary which contains the table's keys. The song will not be added to table if there
        is at least one label which has no key in the dictionary.
        :return: None
        """
        row_pos = self.table.rowCount()
        self.table.insertRow(row_pos)
        for key in TABLE_COLUMN_INDEX.keys():
            value = QtGui.QTableWidgetItem(properties[key])
            value_font = QtGui.QFont()
            value_font.setFamily(_fromUtf8("Gadugi"))
            value_font.setPointSize(15)
            value.setFont(value_font)
            self.table.setItem(row_pos, TABLE_COLUMN_INDEX[key], value)

    def clear_table(self):
        """
        Deletes all the songs from the table.
        :return: None
        """
        for i in range(self.table.rowCount()):
            self.table.removeRow(0)

    def get_selected_tag(self, tag):
        """
        Returns the tag of the selected song.
        :param tag: The wanted tag, for example- 'file_path'
        :return: the value of the tag.
        """
        selected_row = self.get_selected_row()
        if selected_row is not None and tag in TABLE_COLUMN_INDEX.keys():
            return self.table.item(selected_row, TABLE_COLUMN_INDEX[tag]).text()
        else:
            return None

    def get_selected_row(self):
        """
        :return: The index of the selected row.
        """
        try:
            return self.table.selectedRanges()[0].topRow()
        except IndexError:
            return None

    def update_time_display(self, seconds):
        """
        Presents the seconds in the time display and updates the slider accordingly.
        :param seconds: The time which should be displayed.
        :return: None
        """
        song_length = self.get_selected_tag('length')
        if song_length is not None:
            song_length = presentable_to_seconds(str(song_length))
            percent = (100 * seconds) / song_length
            self.time_slider.setValue(int(percent))
        self.time_display.display(presentable_time(seconds))
