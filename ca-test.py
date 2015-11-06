#!/usr/bin/env python
from __future__ import print_function

import re
import os
import fnmatch
import sys
import datetime

from PyQt4.QtCore import *
from PyQt4.QtGui import *

def main():
    app = QApplication(sys.argv)
    w = MyWindow()
    w.show()
    sys.exit(app.exec_())

class MyWindow(QMainWindow):
    def __init__(self, *args):
        QMainWindow.__init__(self, *args)

        # create table
        table = self.createTable()

        # layout
        cw = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(table)
        cw.setLayout(layout)
        self.setCentralWidget(cw)

        open_icon = QIcon.fromTheme('folder-open')
        print(open_icon)
        open_action = QAction(open_icon, 'Open Folder', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_neuron)

        self.toolbar = self.addToolBar('Open')
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toolbar.addAction(open_action)
        self.__path = '.'
        self.tv = table

    def open_neuron(self):
        path = QFileDialog.getExistingDirectory(self, "Open Neuron Directory")
        self.path = str(path)

    def createTable(self):
        # create the view
        tv = QTableView()

        # set the table model
        tm = CaImageFiles('.', self)
        tv.setModel(tm)

        self.setMinimumSize(400, 300)

        vh = tv.verticalHeader()
        vh.setVisible(False)

        hh = tv.horizontalHeader()
        hh.setStretchLastSection(True)


        loops = ["Unset", "Loop 1", "Loop 2", "Loop 3"]
        combo = QComboBox()
        [combo.addItem(opt) for opt in loops]

        tv.setSortingEnabled(True)

        tv.setItemDelegateForColumn(2, LoopChooser(tv))
        tv.setSelectionBehavior(QAbstractItemView.SelectRows)

        QObject.connect(tv, SIGNAL("doubleClicked(QModelIndex)"),
                        self, SLOT("ItemDoubleClicked(QModelIndex)"))

        return tv

    @pyqtSlot("QModelIndex")
    def ItemDoubleClicked(self, index):
        print("Hello!","You Double Clicked: \n"+index.data().toString())


    @property
    def path(self):
        return self.__path

    @path.setter
    def path(self, value):
        self.__path = value
        tm = CaImageFiles(value, self)
        self.tv.setModel(tm)
        self.tv.resizeColumnsToContents()


class LoopChooser(QItemDelegate):
    def __init__(self, parent=None):
        super(LoopChooser, self).__init__(parent)

    def createEditor(self, parent, option, index):
        combo = QComboBox(parent)
        li = []
        li.append("Unset")
        li.append("Loop 1")
        li.append("Loop 2")
        li.append("Loop 3")
        combo.addItems(li)
        self.connect(combo, SIGNAL("currentIndexChanged(int)"), self, SLOT("currentIndexChanged()"))
        return combo

    def setEditorData(self, editor, index):
        editor.blockSignals(True)
        data, success = index.model().data(index, Qt.DisplayRole).toInt()
        editor.setCurrentIndex(data)
        editor.blockSignals(False)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentIndex(), Qt.EditRole)

    @pyqtSlot()
    def currentIndexChanged(self):
        self.commitData.emit(self.sender())

class CaImage(object):
    def __init__(self, path, statbuf):
        self.path = path
        self.name = os.path.basename(path)
        self.statbuf = statbuf
        self.loop = 0

    @staticmethod
    def load_images(path):
        print("Loading images from " + path, file=sys.stderr)
        files = os.listdir(path)
        images = filter(lambda file: fnmatch.fnmatch(file, '*.tif'), files)
        paths = map(lambda file: os.path.join(path, file), images)
        infos = map(lambda path: os.lstat(path), paths)
        return [CaImage(*data) for data in zip(paths, infos)]

    def __repr__(self):
        return "CaImage({path}, {buf})".format(path=self.path, buf=self.statbuf)

    @property
    def ctime(self):
        return self.statbuf.st_ctime

class CaImageFiles(QAbstractTableModel):
    def __init__(self, path, parent=None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.images = CaImage.load_images(path)

    def rowCount(self, parent):
        return len(self.images)

    def columnCount(self, parent):
        return 3

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole:
            return QVariant()
        col = index.column()
        row = index.row()
        if col == 0:
            return QVariant(self.images[row].name)
        elif col == 1:
            ctime = datetime.datetime.fromtimestamp(self.images[row].ctime)
            tstr = ctime.strftime("%d. %B %Y %I:%M%p")
            return QVariant(tstr)
        elif col == 2:
            return QVariant(self.images[row].loop)

        return QVariant()

    def setData(self, index, data, int_role=None):
        col = index.column()
        row = index.row()
        if col != 2:
            raise ValueError('Cannot set data of colum ' + col)
        self.images[row].loop = data
        super(CaImageFiles, self).setData(index, data, int_role)

    def flags(self, index):
        res = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        if index.column() == 2:
            res |= Qt.ItemIsEditable
        return res

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            headers = {0: "Name", 1: "Time", 2: "Loop"}
            return headers[col]
        return QVariant()


if __name__ == "__main__":
    main()
