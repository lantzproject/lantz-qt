

from ..utils.qt import QtGui


class InitializeWindow(QtGui.QWidget):
    """This windows receives the list of drivers to initialize
    and their dependency.
    """

    def __init__(self, drivers=None, dependencies=None, parent=None):
        super(InitializeWindow, self).__init__(parent)

        factory = QtGui.QItemEditorFactory()
        QtGui.QItemEditorFactory.setDefaultFactory(factory)

        self.drivers = drivers
        self.dependencies = dependencies

        self.createGUI()

    @classmethod
    def from_flock(cls, flock):
        return cls(list(flock.values()), flock.dependencies)

    def initialize(self):
        from ..connect import connect_initialize
        self.thread, self.helper = connect_initialize(self.widget, self.drivers,
                                                      dependencies=self.dependencies,
                                                      concurrent=True)

    def createGUI(self):

        # Demonstrate the supported widgets.
        # Uncomment to try others.
        self.widget = self._createGUITable()
        #self.widget = self._createGUILine()
        #self.widget = self._createGUIText()

        button = QtGui.QPushButton()
        button.setText('Initialize')
        button.setEnabled(True)
        button.clicked.connect(self.initialize)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(button)
        layout.addWidget(self.widget)
        self.setLayout(layout)

        self.setWindowTitle("Driver initialization")

    def _createGUIText(self):

        text = QtGui.QTextEdit()
        return text

    def _createGUILine(self):

        text = QtGui.QLineEdit()
        return text

    def _createGUITable(self):

        table = QtGui.QTableWidget(0, 3)
        table.setHorizontalHeaderLabels(["Name", "Class", "Status"])
        table.verticalHeader().setVisible(False)
        table.resize(250, 50)
        table.resizeColumnToContents(0)
        return table


class InitializeDialog(QtGui.QDialog):

    def __init__(self, parent = None, auto_init=False, auto_close=False):
        super(InitializeDialog, self).__init__(parent)

        self.auto_init = auto_init
        self.auto_close = auto_close

        self.createGUI()

    def finished_ok(self):
        self.ok_cancel_buttons.setEnabled(True)
        self.ok_cancel_buttons.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)
        self.ok_cancel_buttons.button(QtGui.QDialogButtonBox.Ok).setFocus()

    def exception_occurred(self):
        self.ok_cancel_buttons.setEnabled(True)
        self.ok_cancel_buttons.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)
        self.ok_cancel_buttons.button(QtGui.QDialogButtonBox.Cancel).setFocus()

    def initialize(self):
        from ..connect import connect_initialize
        self.thread, self.helper = connect_initialize(self.widget, self.drivers,
                                                      dependencies=self.dependencies,
                                                      concurrent=self.concurrent)
        self.helper.finished.connect(self.finished_ok)
        self.helper.exception.connect(self.exception_occurred)

    def exec_(self):
        self.show()

        if self.auto_init:
            self.initialize()

        return super().exec_()

    @staticmethod
    def from_flock(flock, auto_init=True, auto_close=True, concurrent=False, parent=None):
        dialog = InitializeDialog(parent, auto_init, auto_close)

        dialog.drivers = list(flock.values())
        dialog.dependencies = flock.dependencies
        dialog.concurrent = concurrent

        result = dialog.exec_()
        return result == QtGui.QDialog.Accepted

    def createGUI(self):

        self.widget = self._createGUITable()

        layout = QtGui.QVBoxLayout()

        if not self.auto_init:
            button = QtGui.QPushButton()
            button.setText('Initialize')
            button.setEnabled(True)
            button.clicked.connect(self.initialize)

            layout.addWidget(button)

        layout.addWidget(self.widget)

        # OK and Cancel buttons
        buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
            1, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        buttons.setEnabled(False)
        layout.addWidget(buttons)

        self.ok_cancel_buttons = buttons

        self.setLayout(layout)

        self.resize(600, 300)
        self.setWindowTitle("Driver initialization")

    def _createGUITable(self):

        table = QtGui.QTableWidget(0, 3)
        table.setHorizontalHeaderLabels(["Name", "Class", "Status"])
        table.verticalHeader().setVisible(False)
        table.resize(250, 50)
        table.resizeColumnToContents(0)
        return table
