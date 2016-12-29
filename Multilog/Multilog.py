#!/usr/bin/env python3

# TODO
#   add hotkey support (already reading options for it on cmdline)
#  Add annotation field.
#         text gets inserted in log whenever you hit enter in annotation box or click 'note' button next to annotate box.

import sys
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import *
from time import strftime

import os
srcroot=os.path.abspath(os.path.dirname(os.path.abspath(__file__))+"/..")

# import the MsgApp baseclass, for messages, and network I/O
sys.path.append(srcroot+"/MsgApp")
import MsgGui

from Messaging import Messaging

def removePrefix(text, prefix):
    return text[len(prefix):] if text.startswith(prefix) else text
    
class Multilog(MsgGui.MsgGui):
    def __init__(self, argv, parent=None):
        if(len(argv) < 2):
            exit('''
Invoke like this
    ./path/to/Multilog.py --field=LABEL1 --field=LABEL2 --button=hotkey:X,tag:TAG1,label:LABEL3  --button=hotkey:X,tag:TAG2,label:LABEL4
    
each --field adds a text field named the specified LABEL, and the value of the text field will become part of the filename.
each --button adds a pushbutton named for the specified LABEL, with a hotkey of the specified key, and the tag value will become part of the filename

pressing a button starts/stops a log file
underscores in label or field are replaced with spaces for display (to make entering command-line args easier)

filenames will be composed like so:
    YEAR_MONTH_DAY.TEXT1.TEXT2.TAG1.log
''')

        options = ['field=', 'button=']
        MsgGui.MsgGui.__init__(self, "Multilog 0.1", argv, options, parent)
        
        # event-based way of getting messages
        self.RxMsg.connect(self.LogMessage)

        # tab widget to show multiple messages, one per tab
        widget = QWidget(self)
        vLayout = QtGui.QVBoxLayout(widget)
        self.setCentralWidget(widget)
        self.resize(640, 480)
        self.statusMsg = QLabel("NOT logging")
        vLayout.addWidget(self.statusMsg)

        hLayout = QtGui.QHBoxLayout()
        vLayout.addLayout(hLayout)
        lvLayout = QtGui.QVBoxLayout()
        rvLayout = QtGui.QVBoxLayout()
        hLayout.addLayout(lvLayout)
        hLayout.addLayout(rvLayout)
        
        self.lineEdits = []
        self.buttons = []
        self.activeLogButton = None
        for option in self.optlist:
            if option[0] == '--field':
                label = option[1].replace("_"," ")

                # add text field
                lvLayout.addWidget(QLabel(label))
                lineEdit = QLineEdit()
                rvLayout.addWidget(lineEdit)
                self.lineEdits.append(lineEdit)
            elif option[0] == '--button':
                arg = option[1]
                parts = arg.split(",")
                options = {}
                for option in parts:
                    key, value = option.split(":")
                    options[key] = value

                # add button
                label = options["label"].replace("_"," ")
                button = QPushButton(label)
                # how to set hot key?  do it at window level, or at button level?  or something else?
                #button.hotKey = options["hotkey"]
                button.label = label
                self.buttons.append(button)
                if "tag" in options:
                    button.tag = options["tag"]
                else:
                    button.tag = None
                vLayout.addWidget(button)
                
                button.clicked.connect(self.HandleButtonPress)

        # create a new file
        self.file = None
        
    def LogMessage(self, msg):
        # if user specified allowed messages...
        if self.allowedMessages:
            # read the ID, and get the message name, to check if it's allowed
            id       = hex(Messaging.hdr.GetID(msg))
            msgName = Messaging.MsgNameFromID[id]
        
            # only log this message if it's in that list
            if not msgName in self.allowedMessages:
                return

        if self.file is not None:
            #write to a single binary log file
            self.file.write(msg)

            # if you want to write to multiple CSV files, look at lumberjack for an example of how to do so.
            # for each message, you'll need to
            # 1) open a file (store handles to files in a hash based on msg id)
            # 2) look up the MsgNameFromID
            # 3) look up the MsgClassFromName
            # 4) then iterate through the msgClass.fields and msgClass.bitFields
            #  a. to get() the field value as a string for each field, and write them to the file
            # you might also consider using the --msg option to set allowedMessages
            # then you'd get a csv file for each of the messages you care about (and not for the ones you don't)

    def CreateLogFile(self, tag):
        self.CloseLogFile()

        filename = strftime("%Y_%m_%d")
        for lineEdit in self.lineEdits:
            filename += "." + lineEdit.text().replace(" ","_")
        
        if tag is not None:
            filename += "." + tag
        filename += ".log"
        
        # note this opens one binary file to write all the data to.
        self.file = open(filename, 'wb')
        self.statusMsg.setText("Logging to " + filename)

    def CloseLogFile(self):
        if self.file is not None:
            self.file.close()
            self.file = None
            self.statusMsg.setText("NOT Logging")

    def HandleButtonPress(self):
        # when a button is used to start a log, the text of that button changes to "Stop".
        # starting any other log will stop the current one (changing it's text back to normal)
        button = self.sender()
        if button == self.activeLogButton:
            self.CloseLogFile()
            button.setText(button.label)
            self.activeLogButton = None
        else:
            if self.activeLogButton != None:
                self.activeLogButton.setText(self.activeLogButton.label)
            tag = button.tag
            self.CreateLogFile(tag)
            button.setText("Stop")
            self.activeLogButton = button

# main starts here
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    msgApp = Multilog(sys.argv)
    msgApp.show()
    sys.exit(app.exec_())