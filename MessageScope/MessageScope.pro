#-------------------------------------------------
#
# Project created by QtCreator 2014-06-12T18:21:56
#
#-------------------------------------------------

QT += core gui network

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

TARGET = MessageScope
TEMPLATE = app

SOURCES += main.cpp \
           messagescopeguiapplication.cpp \
           ../MsgApp/MessageGuiApp.cpp

HEADERS  += messagescopeguiapplication.h \
            ../MsgApp/MessageGuiApp.h

FORMS    += messagescopeguiapplication.ui