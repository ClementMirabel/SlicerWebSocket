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

    # Websocket
    self.host = "localhost"
    self.port = 8180
    self.socket = None



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
    self.disconnectButton = qt.QPushButton("Disconnect")
    parametersFormLayout.addRow(self.disconnectButton)

    #
    # Python Console
    #
    self.pythonConsole = qt.QTextEdit()
    self.pythonConsole.readOnly = True
    parametersFormLayout.addRow(self.pythonConsole)

    # connections
    self.connectButton.connect('clicked(bool)', self.onConnectButton)
    self.disconnectButton.connect('clicked(bool)', self.onDisconnectButton)
    # self.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    # self.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)

    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # =-=-=-=-=-=-=-=-=-= QT SOCKET =-=-=-=-=-=-=-=-=-=
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # Doc: http://pyqt.sourceforge.net/Docs/PyQt4/qabstractsocket.html

    self.socket = qt.QTcpSocket()
    self.socket.connect('connected()', self.on_connect)
    self.socket.connect('disconnected()', self.on_disconnect)
    self.socket.connect('hostFound()', self.on_hostFound)
    self.socket.connect('readyRead()', self.handleRead)

    # Need to be fixed
    self.socket.connect("error( ::QAbstractSocket::SocketError)", self.on_error)
    # self.socket.connect('bytesWritten()', self.on_written)

    # Add vertical spacer
    self.layout.addStretch(1)


  def onConnectButton(self):
      self.socket.connectToHost(self.host,self.port)

  def onDisconnectButton(self):
      self.socket.abort()
      self.socket.close()

  def on_connect(self):
      self.pythonConsole.append('[Connected]')
      if self.socket.isValid():
          self.socket.write('Hello')

  def on_hostFound(self):
      self.pythonConsole.append('[Host found]')

  def handleRead(self):
      while self.socket.canReadLine():
          m = str(self.socket.readLine()).rstrip('\r\n')
          self.pythonConsole.append('> ' + m)
          if m == "connected":
              self.socket.write('emit_with_callback')

  # def on_written(self):
  #     print "Something written"

  def on_error(self):
      self.pythonConsole.append('[Error]\n')
      print('[Error]')
      print self.socket.error()

  def on_disconnect(self):
      self.pythonConsole.append('[Disconnected]\n\n')

#
# WebSocketLogic
#

class WebSocketLogic(ScriptedLoadableModuleLogic):
    def run(self):
        pass

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
