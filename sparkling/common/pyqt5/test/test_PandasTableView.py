# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
# Tests whether some PyQt5 widget works
# as intended.

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
import os
import sys
# pip install
import pandas as pd
from PyQt5.QtCore import ( QCoreApplication )
from PyQt5.QtWidgets import ( QWidget, QMainWindow, QApplication,
    QMenu, QSystemTrayIcon )
# same project
from sparkling.common.pyqt5.PandasTableView import PandasTableView

# prepare the app
app = QApplication( sys.argv )
mw = QMainWindow()

# gui
w = PandasTableView( parent=mw )
w.setAcceptDrops( True )
w.setDragEnabled( True )

# at this moment grabbing an item and dragging it with a mouse
# results not in multiple selection,
# but in moving the single selected item across the screen

# multiple selection is achieved via keyboard,
# dragging already selected items results in
# moving them across the screen

# TODO
# add keywords to constructor / method
# that explicitly sets drag/drop behavior,
# so that `setDragEnabled` does not interfere with
# intended functionality

# populate gui wuth some data

now = pd.Timestamp.now()
rows = [ {
    'date': now - pd.Timedelta(days=iloc),
    'value': iloc,
    } for iloc in range(50) ]
df = pd.DataFrame( rows )
w.switch_df( df )

# finish and run the app
mw.setCentralWidget( w )
mw.show()

# mainloop
app.exec_()
QCoreApplication.exit()
print()

#---------------------------------------------------------------------------+++
# end 2023.10.20
# restored from old version
