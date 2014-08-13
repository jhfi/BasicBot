import asynchat
import asyncore
import socket
import time

import config


class AsynchatBot(asynchat.async_chat):
    def __init__(self, host, port):
        asynchat.async_chat.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_terminator('\r\n')
        self.data = ''
        self.remote = (host, port)
        self.connect(self.remote)

    def handle_connect(self):
        self.sendLine("USER " + config.nick + " " + config.nick + " " + config.nick + " :" + config.nick)
        self.sendLine("NICK " + config.nick)

    def get_data(self):
        r = self.data
        self.data = ''
        print("(" + str(time.time()) + ") Recv: " + r)
        return r

    def collect_incoming_data(self, data):
        self.data += data

    def sendLine(self, data):
        print("(" + str(time.time()) + ") Send: " + data)
        self.push(data + '\r\n')

    def found_terminator(self):
        data = self.get_data()
        ds = data.split(" ")
        if data[:4] == 'PING':
            self.sendLine('PONG %s' % data[5:])
        if ds[1] == '376':  # end of MOTD
            if config.nickserv_password is not None:
                self.sendLine(
                    "PRIVMSG NickServ :IDENTIFY " + config.nickserv_username + " + " + config.nickserv_password)
            for channel, password in config.channels.items():
                if password is not None:  # channel requires password
                    self.sendLine('JOIN ' + channel + ' ' + password)
                else:
                    self.sendLine('JOIN ' + channel)
        if ds[1] == "PRIVMSG":
            if config.channels.has_key(ds[2].lower()):
                msg = ' '.join(ds[3:])[1:]
                ms = msg.split(" ")
                msgl = msg.lower()
                if msg[0] == config.command_char:
                    acmd = msg[1:]  # after command char
                    aspl = acmd.split(" ")
                    cmd = aspl[0].upper()


if __name__ == '__main__':
    AsynchatBot('irc.freenode.net', 6667)
    asyncore.loop()