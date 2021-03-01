"""
---Adaptive Cruise Control - Server---
Adaptive Cruise Control using Monocular depth estimation.
"""

"""
Si occupa della gestione della rete:
- Send: accelerazione, velocità, ACK.
- Receive: immagini raw, sensori, configurazioni (listeners, camera config, parametri flow, parametri monoculare)

Doppio canale UDP, TCP a seconda delle esigenze

Select per la gestione della receive.

Formato dei messaggi: 
---------------- HEADER ------------------------------
 - ID:long (8 bytes, BIG ENDIAN)
 - Tipo:(TCP, UDP) (2 bytes, BIG ENDIAN)
 - Timestamp:double (8 bytes, BIG ENDIAN)
 - Dimensione in bytes:int (4 bytes, BIG ENDIAN)
 -------------- FINE HEADER 22 bytes -----------------
 - Contenuto: (BIG ENDIAN)

Uso di listener:
 - Remoto: riceverà le send
 - Locale: riceverà i messaggi dall'altro peer. (Cruise Control)

Comandi:
 - models: Invia i modelli monoculari
 - init: Ricevo i parametri iniziali per avviare il cruise control
 - frame: Invia/Riceve un frame: immagine, sensori, accelerazione, velocità, etc Le immagini sono inviate tramite il canale udp
 - config: Configura il cruise control, si attiva se i parametri sono sufficienti
 - getStatus: Riceve la configurazione e stato del cruise control
 - closeConnection: chiude il flusso TCP

Esempi di comandi:
{'cmd': 'frame', 'image': 'raw:id', accelerometer: '.....'} -> elaborazione -> {'cmd': 'frame', velocity: 12.22, ...}
{'cmd': 'config', 'monocular': {...}, ....} -> elaborazione -> {'cmd': 'config', 'ack': True}
{'cmd': 'getStatus'} -> elaborazione -> {'cmd': 'getStatus', 'monocular': {...}, 'camera': {}, ...}

Classi configurabili:
 - cruise
 - monocular
 - camera
 - calibrator
 - opticalflow
"""
from utils_frame import FrameBuffer
from monocularWrapper import MonocularWrapper
from cruiseControl import CruiseControl
from defaults import Defaults
import logging
import socket
import struct
import pickle
import time
import argparse

class CruiseServer:

    TCP = 0
    UDP = 1

    HEADER_STRUCT = struct.Struct('> Q H d I')
    HEADER_LENGTH = 22

    CMD_KEY = 'cmd'
    CMD_MODELS = 'models'
    CMD_INIT = 'init'
    CMD_FRAME = 'frame'
    CMD_CONFIG = 'config'
    CMD_GET_STATUS = 'getStatus'
    CMD_CLOSE_CONNECTION = 'closeConnection'

    ACK_KEY = 'ack'
    RESULT_KEY = 'result'

    def __init__(self, tcpPort = None, udpPort = None, timeout = None):
        self.loggingName = "CruiseServer"
        
        if tcpPort is None:
            tcpPort = Defaults.tcpPort
        
        if udpPort is None:
            udpPort = Defaults.udpPort

        if timeout is None:
            timeout = Defaults.timeout

        self.cruiseControl = None
        self.remoteAddr = None
        self.remoteSocket = None

        self.udpIP = "127.0.0.1"
        self.udpPort = udpPort
        self.tcpIP = "127.0.0.1"
        self.tcpPort = tcpPort
        self.timeout = timeout

        self.init()
        
    def init(self):
        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpSocket.settimeout(self.timeout)

        self.tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpSocket.settimeout(self.timeout)

        go = False
        while not go:
            try:
                self.bind()
                go = True
            except OSError as o:
                if o.errno != 98:
                    raise o
        
        self.seqNumber = 0

    def bind(self):
        #self.udpSocket.bind((self.udpIP, self.udpPort))
        #self.udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcpSocket.bind((self.tcpIP, self.tcpPort))
        self.tcpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def closeRemote(self):
        if self.remoteSocket is not None:
            self.remoteSocket.close()
            self.remoteSocket = None

    def close(self):
        self.closeRemote()        
        self.tcpSocket.close()
        self.udpSocket.close()

    def run(self):       
        #Se non ho un ricevitore remoto mi metto in ascolto.
        if self.remoteSocket is None:
            self.tcpSocket.listen()

            try:
                conn, addr = self.tcpSocket.accept()
            except socket.timeout:
                logging.debug("{0} timeout accept".format(self.loggingName))
                return

            logging.info("{0} connesso al peer remoto {1}".format(self.loggingName, addr))

            self.remoteSocket = conn
            self.remoteAddr = addr
        
        try:
            cmd = self.receiveCmd()
        except ConnectionResetError:
            logging.debug("{0} connection reset from {1}".format(self.loggingName, self.remoteAddr))
            cmd = None
            
        if not cmd:
            logging.info("{0} {1} ha chiuso".format(self.loggingName, self.remoteAddr))
            self.remoteSocket.close()
            self.remoteSocket = None
            self.remoteAddr = None
            return

        id, tipo, timestamp, content = cmd

        #Decodifico il contenuto
        #Eseguo il comando
        #Restituisco la risposta

        cmd = content[self.CMD_KEY]

        logging.info("{0} ricevuto comando {1}".format(self.loggingName, cmd))

        sendResult = False

        if cmd == self.CMD_MODELS:
            #Richiesta dei modelli monoculari
            models = MonocularWrapper.models
            sendResult = self.sendResult(id, tipo, {self.ACK_KEY: True, self.RESULT_KEY: models})

        elif cmd == self.CMD_INIT:
            #Richiesta di inizializzazione.
            cruiseControl = CruiseControl.fromConfig(content)

            if cruiseControl:
                self.cruiseControl = cruiseControl
                sendResult = self.sendResult(id, tipo, {self.ACK_KEY: True})
            else:
                sendResult = self.sendResult(id, tipo, {self.ACK_KEY: False})

        elif cmd == self.CMD_FRAME and self.cruiseControl:
            #Richiesta di elaborare un frame.
            frame = self.cruiseControl.shiftFrom(content, timestamp)

            #Pulisco un po il frame per renderlo leggero
            if frame:
                frame.pop(FrameBuffer.RGB_IMAGE, None)
                frame.pop(FrameBuffer.BGR_IMAGE, None)
                frame.pop(FrameBuffer.GRAY_IMAGE, None)
                frame.pop(FrameBuffer.GROUND_TRUTH, None)
                frame.pop(FrameBuffer.PREDICTION, None)

            velocitaUscita, accelerazione = self.cruiseControl.previsioneCruise()
            parseTime, inferenceTime, calibrationTime = self.cruiseControl.timing
            sendResult = self.sendResult(id, tipo, {self.ACK_KEY: True, self.RESULT_KEY: {'frame': frame, 'velocitaUscita':velocitaUscita, 'accelerazione': accelerazione, 'parseTime': parseTime, 'inferenceTime': inferenceTime, 'calibrationTime': calibrationTime}})
                
        elif cmd == self.CMD_CONFIG and self.cruiseControl:
            #Richiesta di configurazione.
            self.cruiseControl.config(content['config'])
            sendResult = self.sendResult(id, tipo, {self.ACK_KEY: True})

        elif cmd == self.CMD_GET_STATUS and self.cruiseControl:
            #Richiesta di stato.
            status = self.cruiseControl.status
            sendResult = self.sendResult(id, tipo, {self.ACK_KEY: True, self.RESULT_KEY: status})
        
        elif cmd == self.CMD_CLOSE_CONNECTION:
            self.sendResult(id, tipo, {self.ACK_KEY: True})
            self.closeRemote()

        if not sendResult:
            self.remoteSocket.close()
            self.remoteSocket = None
            self.remoteAddr = None
            return

    def sendResult(self, id, tipo, content):
        """
        Invia un risultato al client remoto.
        id: identificativo della richiesta originale
        tipo: se utilizzare TCP o UDP per la trasmissione del contenuto
        content: risultato della richiesta: deve essere serializzata in pickle.
        """
        
        #Effettuo la serializzazione
        pickleContent = pickle.dumps(content)

        try:
            if not self.sendPacket(id, tipo, pickleContent):
                return False
        except socket.timeout:
            logging.debug("{0} timeout send".format(self.loggingName))
            return False

        return True
        
    def sendPacket(self, id, tipo, content):
        length = len(content)
        timestamp = time.time()
        packet = self.HEADER_STRUCT.pack(id, tipo, timestamp, length)

        try:
            if self.myTcpSend(packet, self.HEADER_LENGTH) != self.HEADER_LENGTH:
                return False
        except BrokenPipeError:
            return False

        logging.debug("{0} sent header: {1}".format(self.loggingName, (id, tipo, timestamp, length)))

        totalSent = 0

        try:
            if tipo == self.TCP:
                totalSent = self.myTcpSend(content, length)
            elif tipo == self.UDP:
                totalSent = self.myUdpSend(content, length)
        except BrokenPipeError:
            return False

        logging.debug("{0} sent content with length: {1}".format(self.loggingName, totalSent))

        return totalSent == length

    def myUdpSend(self, msg, length):
        #TODO: da modificare: c'è limite al pacchetto
        return self.udpSocket.sendto(msg, (self.remoteAddr[0], self.udpPort))

    def myUdpRecv(self, length):
        #TODO: da modificare: c'è limite al pacchetto: mettere identificativo sub-pacchetto: non arrivano in ordine
        content, addr = self.udpSocket.recvfrom(length)
        logging.debug("{0} UDP read from: {1}, remote addr: {2}".format(self.loggingName, addr, self.remoteAddr))
        #Check sull'addr
        if addr != self.remoteAddr:
            return
        return content

    def myTcpSend(self, msg, length):
        totalsent = 0
        while totalsent < length:
            sent = self.remoteSocket.send(msg[totalsent:])
            if sent == 0:
                return totalsent
            totalsent = totalsent + sent
        return totalsent

    def myTcpRecv(self, length):
        content = bytearray(self.remoteSocket.recv(length))
        totalReceived = len(content)

        while totalReceived < length:
            content.extend(bytearray(self.remoteSocket.recv(length-totalReceived)))
            totalReceived = len(content)
        return content

    def receiveCmd(self):
        #Ricevo un comando
        data = self.remoteSocket.recv(self.HEADER_LENGTH)

        #Comando non valido esco
        if not data:
            return

        #Decodifico l'header
        id, tipo, timestamp, length = self.HEADER_STRUCT.unpack(data)

        logging.debug("{0} received header: {1}".format(self.loggingName, (id, tipo, timestamp, length)))

        #Aggiorno il numero di sequenza.
        self.seqNumber = max(id, self.seqNumber)
            
        #Ricavo il contenuto.
        content = None
            
        if tipo == self.UDP:
            #Lettura UDP
            content = self.myUdpRecv(length)
        elif tipo == self.TCP:
            #Lettura TCP
            content = self.myTcpRecv(length)
            
        #Check sul contenuto
        if not content:            
            return

        logging.debug("{0} received content with length: {1}".format(self.loggingName, len(content)))

        #Deserializzazione
        content = pickle.loads(content)

        return id, tipo, timestamp, content
        
def loop(server:CruiseServer):
    try:
        while True:
            server.run()
    finally:
        server.close()

def main():
    argparser = argparse.ArgumentParser(
        description='Adaptive Cruise Control Server')
    
    argparser.add_argument(
        '-v', '--verbose',
        action='store_true',
        dest='debug',
        help='print debug information')

    argparser.add_argument(
        '-pT', '--portTcp',
        metavar='PT',
        default=Defaults.tcpPort,
        type=int,
        help='TCP port to listen to (default: {0})'.format(Defaults.tcpPort))

    argparser.add_argument(
        '-pU', '--portUdp',
        metavar='PU',
        default=Defaults.udpPort,
        type=int,
        help='UDP port to listen to (default: {0})'.format(Defaults.udpPort))

    argparser.add_argument(
        '-t', '--timeout',
        metavar='T',
        default=Defaults.timeout,
        type=int,
        help='Timeout (default: {0})'.format(Defaults.timeout))

    args = argparser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(format='%(levelname)s: %(message)s', level=log_level)

    print(__doc__)

    #Avvio il server e resto in attesa
    server = CruiseServer(args.portTcp, args.portUdp, args.timeout)

    logging.info('listening to TCP %s, UDP %s', args.portTcp, args.portUdp)

    try:
        loop(server)
    except KeyboardInterrupt:
        print('\nCancelled by user. Bye!')


if __name__ == '__main__':
    main()