import os,sys
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
from socketIO_client import SocketIO, BaseNamespace
import threading

#
# WebSocket
#


class WebSocket(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "WebSocket" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Examples"]
    self.parent.dependencies = []
    self.parent.contributors = ["Clement Mirabel (UMich)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
    This is an example of scripted loadable module bundled in an extension.
    It performs a simple thresholding on the input volume and optionally captures a screenshot.
    """
    self.parent.acknowledgementText = """
    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
    and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# WebSocketWidget
#

class WebSocketWidget(ScriptedLoadableModuleWidget):

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)
    self.logic = WebSocketLogic(self)

    # Instantiate and connect widgets ...
    #
    # Parameters Area
    #
    websocketCollapsibleButton = ctk.ctkCollapsibleButton()
    websocketCollapsibleButton.text = "Websocket"
    self.layout.addWidget(websocketCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(websocketCollapsibleButton)

    #
    # Apply Button
    #
    self.connectButton = qt.QPushButton("Connect")
    self.connectButton.toolTip = "Run the algorithm."
    parametersFormLayout.addRow(self.connectButton)

    #
    # Disconnect Button
    #
    # self.disconnectButton = qt.QPushButton("Disconnect")
    # parametersFormLayout.addRow(self.disconnectButton)

    #
    # Python Console
    #
    self.pythonConsole = qt.QTextEdit()
    # self.textEdit.setGeometry(QtCore.QRect(10, 300,
    # > self.textEdit.setObjectName(_fromUtf8("textEdit"))
    parametersFormLayout.addRow(self.pythonConsole)

    # connections
    self.connectButton.connect('clicked(bool)', self.onConnectButton)
    # self.disconnectButton.connect('clicked(bool)', self.onDisconnectButton)
    # self.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    # self.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)

    # Add vertical spacer
    self.layout.addStretch(1)


  def onConnectButton(self):
      import thread
      thread.start_new_thread(self.logic.runSocket, ())

  def onDisconnectButton(self):
    pass
#
# WebSocketLogic
#

class WebSocketLogic(ScriptedLoadableModuleLogic):
    def runSocket(self):
        self.socketIO = SocketIO('localhost:8180/suscribe', 8180, Namespace)
        self.socketIO.wait()

class Namespace(BaseNamespace):
    def on_connect(self):
        self.ui = slicer.modules.WebSocketWidget
        self.lock = threading.Lock()

        self.lock.acquire()
        self.ui.pythonConsole.append('[Connected]\n')
        print('[Connected]')
        self.lock.release()

    def on_reconnect(self):
        self.lock.acquire()
        self.ui.pythonConsole.append('[Reconnected]\n')
        print('[Reconnected]')
        self.lock.release()

    def on_connected(self, args):
        self.lock.acquire()
        self.ui.pythonConsole.append('connected')
        self.ui.pythonConsole.append(args)
        print('connected', args)
        self.lock.release()
        self.emit('emit_with_callback', self.callback)

    def callback(self, *args):
        self.lock.acquire()
        self.ui.pythonConsole.append(args)
        print(args)
        self.lock.release()

    def on_disconnect(self):
        self.lock.acquire()
        self.ui.pythonConsole.append('[Disconnected]')
        print('[Disconnected]')
        self.lock.release()

    def on_execute_task(self, *args):
        self.lock.acquire()
        self.ui.pythonConsole.append('executing task')
        self.ui.pythonConsole.append(args)
        print('executing task', args)
        self.lock.release()


class WebSocketTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_WebSocket1()

  def test_WebSocket1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    import urllib
    downloads = (
        ('http://slicer.kitware.com/midas3/download?items=5767', 'FA.nrrd', slicer.util.loadVolume),
        )

    for url,name,loader in downloads:
      filePath = slicer.app.temporaryPath + '/' + name
      if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
        logging.info('Requesting download %s from %s...\n' % (name, url))
        urllib.urlretrieve(url, filePath)
      if loader:
        logging.info('Loading %s...' % (name,))
        loader(filePath)
    self.delayDisplay('Finished with download and loading')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = WebSocketLogic()
    self.delayDisplay('Test passed!')