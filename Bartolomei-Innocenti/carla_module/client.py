"""
---Adaptive Cruise Control - Client---
Adaptive Cruise Control using Monocular depth estimation.
"""
"""
Si occupa della gestione della rete:
- Receive: accelerazione, velocità, ACK.
- Send: immagini raw, sensori, configurazioni (listeners, camera config, parametri flow, parametri monoculare)

UDP: invio/ricezione di immagini.
TCP: tutto il resto.

Formato dei messaggi: 
---------------- HEADER ------------------------------
 - ID:long (8 bytes, BIG ENDIAN)
 - Tipo:(TCP, UDP) (2 bytes, BIG ENDIAN)
 - Timestamp:double (8 bytes, BIG ENDIAN)
 - Dimensione in bytes:int (4 bytes, BIG ENDIAN)
 -------------- FINE HEADER 22 bytes -----------------
 - Contenuto: (BIG ENDIAN)

Comandi:
 - models: Invia i modelli monoculari
 - init: Ricevo i parametri iniziali per avviare il cruise control
 - frame: Invia/Riceve un frame: immagine, sensori, accelerazione, velocità, etc Le immagini sono inviate tramite il canale udp
 - config: Configura il cruise control, si attiva se i parametri sono sufficienti
 - getStatus: Riceve la configurazione e stato del cruise control

Classi configurabili:
 - cruise
 - monocular
 - camera
 - calibrator
 - opticalflow
"""

from defaults import Defaults
import logging
import socket
import struct
import pickle
import time
import threading
import weakref


class CruiseClient:

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

    ACK_KEY = 'ack'
    RESULT_KEY = 'result'

    SHIFT_KEY = 'shift'
    SHIFT_TYPES = ['carlaRt', 'gnssIMUEncoder']

    def __init__(self, addr = None, tcpPort = None, udpPort = None, timeout = None):
        self.loggingName = "CruiseClient"

        if addr is None:
            addr = Defaults.addr
        
        if tcpPort is None:
            tcpPort = Defaults.tcpPort
        
        if udpPort is None:
            udpPort = Defaults.udpPort

        if timeout is None:
            timeout = Defaults.timeout

        self.udpIP = addr
        self.udpPort = udpPort
        self.tcpIP = addr
        self.tcpPort = tcpPort
        self.timeout = timeout

        self.init()

    def init(self):
        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpSocket.settimeout(self.timeout)
        
        self.tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpSocket.settimeout(self.timeout)
        
        self.seqNumber = 0

    def connect(self):
        logging.info("{0} connessione a {1}:{2}".format(self.loggingName, self.tcpIP, self.tcpPort))
        self.tcpSocket.connect((self.tcpIP, self.tcpPort))

    def close(self):        
        self.tcpSocket.close()
        self.udpSocket.close()

        self.pool.close()
        self.pool.join()

    def sendPacket(self, id, tipo, content):
        length = len(content)
        timestamp = time.time()
        packet = self.HEADER_STRUCT.pack(id, tipo, timestamp, length)

        if self.myTcpSend(packet, self.HEADER_LENGTH) != self.HEADER_LENGTH:
            return False

        logging.debug("{0} sent header: {1}".format(self.loggingName, (id, tipo, timestamp, length)))

        totalSent = 0

        if tipo == self.TCP:
            totalSent = self.myTcpSend(content, length)
        elif tipo == self.UDP:
            totalSent = self.myUdpSend(content, length)

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
            sent = self.tcpSocket.send(msg[totalsent:])
            if sent == 0:
                return totalsent
            totalsent = totalsent + sent
        return totalsent

    def myTcpRecv(self, length):
        content = bytearray(self.tcpSocket.recv(length))
        totalReceived = len(content)

        while totalReceived < length:
            content.extend(bytearray(self.tcpSocket.recv(length-totalReceived)))
            totalReceived = len(content)
        return content

    def receiveResult(self):
        #Ricevo la risposta
        data = self.myTcpRecv(self.HEADER_LENGTH)

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

    def sendCmd(self, tipo, content):
        """
        Invia una richiesta al server remoto.
        tipo: se inviare con UDP o TCP
        content: richiesta: deve essere serializzata in pickle.
        """

        self.seqNumber += 1
        id = self.seqNumber
        
        #Serializzazione
        pickleContent = pickle.dumps(content)

        return self.sendPacket(id, tipo, pickleContent)

    def _cmdModels(self, callback):
        content = {self.CMD_KEY: self.CMD_MODELS}
        self.sendCmd(self.TCP, content)
        result = self.receiveResult()

        if result:
            id,tipo,timestamp,result = result

            if result[self.ACK_KEY]:
                callback(result[self.RESULT_KEY])
            else:
                #callbackErrore
                pass
        else:
            #TODO: restart client
            logging.debug("{0} result empty".format(self.loggingName))
            #callback errore

    def cmdModels(self, callback):
        x = threading.Thread(target=self._cmdModels, args=(callback, ), daemon=True)
        x.start()

    def _cmdInit(self, callback, width, height, fx, fy, cx, cy, D, roi, velocitaCrociera, distanzaMinima = None, distanzaMassima = None):
        content = {self.CMD_KEY: self.CMD_INIT}
        
        content['camera'] = {'width': width, 'height': height,
         'fx': fx, 'fy': fy,
          'cx': cx, 'cy': cy, 'D': D}

        content['roi'] = roi
        content['velocitaCrociera'] = velocitaCrociera
        content['distanzaMinima'] = distanzaMinima
        content['distanzaLimite'] = distanzaMassima
        
        self.sendCmd(self.TCP, content)
        result = self.receiveResult()

        if result:
            id,tipo,timestamp,result = result
            callback(result[self.ACK_KEY])
        else:
            #TODO: restart client
            logging.debug("{0} result empty".format(self.loggingName))

    def cmdInit(self, callback, width, height, fx, fy, cx, cy, D, roi, velocitaCrociera, distanzaMinima = None, distanzaMassima = None):
        x = threading.Thread(target=self._cmdInit, args=(callback, width, height, fx, fy, cx, cy, D, roi, velocitaCrociera, distanzaMinima, distanzaMassima), daemon=True)
        x.start()

    def _cmdFrameCarlaRt(self, callback, transform, imageBGR, imageGT = None):
        content = {self.CMD_KEY: self.CMD_FRAME}
        content[self.SHIFT_KEY] = 'carlaRt'
        content['imageBGR'] = imageBGR

        if imageGT is not None:
            content['imageGT'] = imageGT
        
        content['transform'] = transform

        self.sendCmd(self.TCP, content)
        result = self.receiveResult()

        if result:
            id,tipo,timestamp,result = result
            if result[self.ACK_KEY]:
                result = result[self.RESULT_KEY]
                callback(result['frame'], result['velocitaUscita'], result['accelerazione'], result['parseTime'], result['inferenceTime'], result['calibrationTime'])
            else:
                #callbackErrore
                pass
        else:
            #TODO: restart client
            logging.debug("{0} result empty".format(self.loggingName))

    def cmdFrameCarlaRt(self, callback, transform, imageBGR, imageGT = None):
        x = threading.Thread(target=self._cmdFrameCarlaRt, args=(callback, transform, imageBGR, imageGT), daemon=True)
        x.start()

    def _cmdConfig(self, callback, config):
        content = {self.CMD_KEY: self.CMD_CONFIG}
        content['config'] = config
        self.sendCmd(self.TCP, content)
        result = self.receiveResult()
        if result:
            id,tipo,timestamp,result = result
            callback(result[self.ACK_KEY])
        else:
            #TODO: restart client
            logging.debug("{0} result empty".format(self.loggingName))
    
    def cmdConfig(self, callback, config):
        x = threading.Thread(target=self._cmdConfig, args=(callback, config), daemon=True)
        x.start()

    def _cmdGetStatus(self, callback):
        content = {self.CMD_KEY: self.CMD_GET_STATUS}
        self.sendCmd(self.TCP, content)
        result = self.receiveResult()

        if result:
            id,tipo,timestamp,result = result

            if result[self.ACK_KEY]:
                callback(result[self.RESULT_KEY])
            else:
                #callbackErrore
                pass
        else:
            #TODO: restart client
            logging.debug("{0} result empty".format(self.loggingName))
            #callback errore

    def cmdGetStatus(self, callback):
        x = threading.Thread(target=self._cmdGetStatus, args=(callback, ), daemon=True)
        x.start()
