class Defaults:
    """
    Contiene i default per l'esecuzione.
    """

    #Main
    queueLength = 20
    fov = 60.0

    circleRadius = 2
    circleColor0 = (255,0,0)
    circleColor1 = (0,255,0)
    circleColor2 = (255,255,0)

    lineTickness = 1
    lineColor = (0,0,255)
    
    maxRenderingValue = 100

    #World
    roi = (260, 165, 100, 25)
    distanzaMinima = 5.0
    distanzaMassima = 30.0

    #Client
    addr = "127.0.0.1"
    tcpPort = 5050
    udpPort = 5051
    timeout = 60.0

    