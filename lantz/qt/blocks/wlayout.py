

from ..utils.qt import QtGui, QtCore

QtWidgets = QtGui

from ..app import Frontend


class BorderUi(Frontend):
    """The Loop frontend provides a GUI for the Rich Backend"""

    auto_connect = False

    #: Tuple with the columns
    #: Each element can be:
    #:   - Frontend class: will be connected to the default backend.
    #:   - Front2Back(Frontend class, backend name): will be connect to a specific backend.
    #:   - tuple: will be iterated to obtain the rows.
    north = ()
    west = ()
    south = ()
    east = ()
    center = ()

    def __add(self, layout, parts):
        """Add widgets in parts to layout.

        Parameters
        ----------
        layout :

        parts :


        Returns
        -------

        """
        for part_name in parts:
            if part_name is True:
                layout.addStretch()
                continue

            part = getattr(self, part_name)

            if isinstance(part, Frontend):
                layout.addWidget(part)

            elif isinstance(part, tuple):
                # A tuple found in parts is considered nesting
                if isinstance(layout, self._inner):
                    sublayout = self._outer()
                elif isinstance(layout, self._outer):
                    sublayout = self._inner()
                else:
                    raise ValueError('Unknown parent layout %s' % layout)

                self.__add(sublayout, part)

                layout.setLayout(sublayout)

            else:
                raise ValueError('Only Frontend or tuple are valid values '
                                 'valid for parts not %s (%s)' % (part, type(part)))

        return layout

    def __build_layout(self, content):
        if not content:
            return None
        layout_type, *names = content
        layout = layout_type()
        for name in names:
            if name is True:
                layout.addStretch()
                continue

            part = getattr(self, name)

            if isinstance(part, Frontend):
                layout.addWidget(part)
            else:
                raise ValueError('Only Frontend are valid values '
                                 'valid for parts not %s (%s)' % (part, type(part)))
        return layout

    def setupUi(self):
        super().setupUi()

        center = self.__build_layout(self.center)
        east = self.__build_layout(self.east)
        west = self.__build_layout(self.west)
        south = self.__build_layout(self.south)
        north = self.__build_layout(self.north)
        self.widget = BorderWidget(center, north, south, east, west)
        self.setCentralWidget(self.widget)


class ItemWrapper(object):
    def __init__(self, i, p):
        self.item = i
        self.position = p


class BorderLayout(QtWidgets.QLayout):
    West, North, South, East, Center = range(5)
    MinimumSize, SizeHint = range(2)

    def __init__(self, parent=None, margin=None, spacing=-1):
        super(BorderLayout, self).__init__(parent)

        if margin is not None:
            self.setContentsMargins(margin, margin, margin, margin)

        self.setSpacing(spacing)
        self.list = []

    def __del__(self):
        l = self.takeAt(0)
        while l is not None:
            l = self.takeAt(0)

    def addItem(self, item):
        self.add(item, self.West)

    def addWidget(self, widget, position):
        self.add(QtWidgets.QWidgetItem(widget), position)

    def addLayout(self, layout, position):
        w = QtWidgets.QWidget()
        w.setLayout(layout)
        self.addWidget(w, position)

    def expandingDirections(self):
        return QtGui.Horizontal | QtGui.Vertical

    def hasHeightForWidth(self):
        return False

    def count(self):
        return len(self.list)

    def itemAt(self, index):
        if index < len(self.list):
            return self.list[index].item

        return None

    def minimumSize(self):
        return self.calculateSize(self.MinimumSize)

    def setGeometry(self, rect):
        center = None
        eastWidth = 0
        westWidth = 0
        northHeight = 0
        southHeight = 0
        centerHeight = 0

        super(BorderLayout, self).setGeometry(rect)

        for wrapper in self.list:
            item = wrapper.item
            position = wrapper.position

            if position == self.North:
                item.setGeometry(QtCore.QRect(rect.x(), northHeight,
                        rect.width(), item.sizeHint().height()))

                northHeight += item.geometry().height() + self.spacing()

            elif position == self.South:
                item.setGeometry(QtCore.QRect(item.geometry().x(),
                        item.geometry().y(), rect.width(),
                        item.sizeHint().height()))

                southHeight += item.geometry().height() + self.spacing()

                item.setGeometry(QtCore.QRect(rect.x(),
                        rect.y() + rect.height() - southHeight + self.spacing(),
                        item.geometry().width(), item.geometry().height()))

            elif position == self.Center:
                center = wrapper

        centerHeight = rect.height() - northHeight - southHeight

        for wrapper in self.list:
            item = wrapper.item
            position = wrapper.position

            if position == self.West:
                item.setGeometry(QtCore.QRect(rect.x() + westWidth,
                        northHeight, item.sizeHint().width(), centerHeight))

                westWidth += item.geometry().width() + self.spacing()

            elif position == self.East:
                item.setGeometry(QtCore.QRect(item.geometry().x(),
                        item.geometry().y(), item.sizeHint().width(),
                        centerHeight))

                eastWidth += item.geometry().width() + self.spacing()

                item.setGeometry(QtCore.QRect(rect.x() + rect.width() - eastWidth + self.spacing(),
                        northHeight, item.geometry().width(),
                        item.geometry().height()))

        if center:
            center.item.setGeometry(QtCore.QRect(westWidth, northHeight,
                    rect.width() - eastWidth - westWidth, centerHeight))

    def sizeHint(self):
        return self.calculateSize(self.SizeHint)

    def takeAt(self, index):
        if index >= 0 and index < len(self.list):
            layoutStruct = self.list.pop(index)
            return layoutStruct.item

        return None

    def add(self, item, position):
        self.list.append(ItemWrapper(item, position))

    def calculateSize(self, sizeType):
        totalSize = QtGui.QSize()

        for wrapper in self.list:
            position = wrapper.position
            itemSize = QtGui.QSize()

            if sizeType == self.MinimumSize:
                itemSize = wrapper.item.minimumSize()
            else: # sizeType == self.SizeHint
                itemSize = wrapper.item.sizeHint()

            if position in (self.North, self.South, self.Center):
                totalSize.setHeight(totalSize.height() + itemSize.height())

            if position in (self.West, self.East, self.Center):
                totalSize.setWidth(totalSize.width() + itemSize.width())

        return totalSize


class BorderWidget(QtWidgets.QWidget):

    def __init__(self, center, north, south, east, west):
        super(BorderWidget, self).__init__()

        layout = BorderLayout()
        layout.addLayout(center, BorderLayout.Center)

        # Because BorderLayout doesn't call its super-class addWidget() it
        # doesn't take ownership of the widgets until setLayout() is called.
        # Therefore we keep a local reference to each label to prevent it being
        # garbage collected too soon.

        if north:
            layout.addLayout(north, BorderLayout.North)

        if west:
            layout.addLayout(west, BorderLayout.West)

        if east:
            layout.addLayout(east, BorderLayout.East)

        if south:
            layout.addLayout(south, BorderLayout.South)

        self.setLayout(layout)

