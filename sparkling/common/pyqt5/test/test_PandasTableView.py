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

# This documentation was created with the aid of
# an AI assistant.

# how drag and drop works (in pyqt5):
# 1) i go to the source widget
# 2) i select some data that i want to drag
# 3) source widget creates `QDrag` with some information (`mime data`, `proposed action`)
# -- only one `QDrag` operation can exist at a time --
# -- all interfering `QDrag` operations are destroyed by pyqt --
# 4) i move this `QDrag` around and see visual feedback
# 5) i give this `QDrag` to destination widget
# 6) it somehow processes this `QDrag` and tells the user `i accept` or `no thank you`.

# more on the steps 4, 5:
    
# - `dragEnterEvent` is fired
# - destination widget starts to think: 'do i need this QDrag'?
# - i move the mouse
# - `dragMoveEvent` is fired
# - destination widget continues to think
#   (maybe if i write 'please' with the mouse cursor it will accept?;
#   more realistic example - reposition inner elements and preview `QDrag` contents position)
# - i move the mouse away
# - `dragLeaveEvent` is fired
# - destination widget stops thinking.
# - alternatively, i release the mouse
# - `dropEvent` is fired
# - destination widget needs to think more (step 6) and finally say
#   `QDrop.accept()` or `QDrop.ignore()`.

# more on the step 6:
    
# - `dropMimeData` is fired
# - `mimeTypes` is automatically checked
# - something happens.

# regarding `internal move` operation:
    
# - this operation is specific to `views`
# - this meas that is does not affect the underlying `model`.
# 1) `view` creates a `QDrag`
# 2) this `QDrag` has lots of data, even a `pixmap` - a picture
# of selected rows; `action = move action`
# 3) `view` says `QDrag.exec()`
# everything is paused until the user finished this drag/drop operation
# 4) user moves his mouse, releases the `QDrag` somewhere within this `view`
# 5) `QDrag` is processed by destination (this `view`)
# 6) destination does something and says `QDrop.accept()` or `QDrop.ignore()`, source widget receives this answer,
# which in this case means 'i sent this to myself, it worked'.

# In my case whenever user reorders items
# in `view`, I want to change the underlying `model`,
# so `internal move` is not applicable.

# populate gui with some data

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
