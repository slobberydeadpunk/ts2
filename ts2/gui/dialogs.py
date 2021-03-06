#
#   Copyright (C) 2008-2013 by Nicolas Piganeau
#   npi@m4x.org
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the
#   Free Software Foundation, Inc.,
#   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#

import sys
import traceback

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt

from ts2.gui import servicelistview

translate = QtGui.QApplication.translate

class ExceptionDialog:
    """A Dialog box for displaying exception information
    """

    @staticmethod
    def popupException(parent, exception=None):
        """Displays a dialog with all the information about the exception and
        the traceback."""
        title = translate("ExceptionDialog", "Error")
        message = ""
        if exception is not None:
            message = str(exception) + "\n\n"
            message += message.join(traceback.format_tb(sys.exc_info()[2]))
        else:
            message += message.join(traceback.format_exc())
            return QtGui.QMessageBox.critical(parent, title, message)


class PropertiesDialog(QtGui.QDialog):
    """Dialog box for editing simulation properties during the game."""

    def __init__(self, parent, simulation):
        """Constructor for the PropertiesDialog class."""
        super().__init__(parent)
        self.simulation = simulation
        self.setWindowTitle(self.tr("Simulation properties"))
        titleLabel = QtGui.QLabel(self)
        titleLabel.setText("<u>" +
                           self.tr("Simulation title:") +
                           "</u>")
        titleText = QtGui.QLabel(simulation.option("title"), self)
        hlayout = QtGui.QHBoxLayout()
        hlayout.addWidget(titleLabel)
        hlayout.addWidget(titleText)
        hlayout.addStretch()
        descriptionLabel = QtGui.QLabel(self)
        descriptionLabel.setText("<u>" +
                                 self.tr("Description:") +
                                 "</u>")
        descriptionText = QtGui.QTextEdit(self)
        descriptionText.setReadOnly(True)
        descriptionText.setText(simulation.option("description"))
        optionsLabel = QtGui.QLabel(self)
        optionsLabel.setText("<u>" + self.tr("Options:") + "</u>")
        tibOptionCB = QtGui.QCheckBox(self)
        tibOptionCB.stateChanged.connect(self.changeTIB)
        tibOptionCB.setChecked(
                            int(simulation.option("trackCircuitBased")) != 0)
        optionLayout = QtGui.QFormLayout()
        optionLayout.addRow(self.tr("Play simulation with track circuits"),
                            tibOptionCB)
        buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok)
        layout = QtGui.QVBoxLayout()
        layout.addLayout(hlayout)
        layout.addWidget(descriptionLabel)
        layout.addWidget(descriptionText)
        layout.addWidget(optionsLabel)
        layout.addLayout(optionLayout)
        layout.addWidget(buttonBox)
        self.setLayout(layout)
        buttonBox.accepted.connect(self.accept)

    @QtCore.pyqtSlot(int)
    def changeTIB(self, checkState):
        """Changes the trackItemBased Option."""
        if checkState == Qt.Checked:
            self.simulation.setOption("trackCircuitBased", 1)
        else:
            self.simulation.setOption("trackCircuitBased", 0)


class ServiceAssignDialog(QtGui.QDialog):
    """TODO Document ServiceAssignDialog"""

    def __init__(self, parent, simulation):
        super().__init__(parent)
        self.setWindowTitle(self.tr(
                                "Choose a service to assign to this train"))
        self.serviceListView = servicelistview.ServiceListView(self)
        self.serviceListView.setupServiceList(simulation)
        buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok|
                                           QtGui.QDialogButtonBox.Cancel)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.serviceListView)
        layout.addWidget(buttonBox)
        self.setLayout(layout)
        self.resize(600, 300)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def getServiceCode(self):
        index = self.serviceListView.selectionModel().selection().indexes()[0]
        if index.isValid():
            return index.data()
        else:
            return ""

    @staticmethod
    def reassignServiceToTrain(simulation, trainId):
        """Reassigns a service to the train given by trainId by poping-up a
        reassignServiceDialog."""
        sad = ServiceAssignDialog(simulation.simulationWindow, simulation)
        if sad.exec_() == QtGui.QDialog.Accepted:
            newServiceCode = sad.getServiceCode()
            if newServiceCode != "":
                train = simulation.trains[trainId]
                train.serviceCode = newServiceCode

