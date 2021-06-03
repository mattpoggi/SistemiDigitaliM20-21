class Defaults:
    """
    Contiene i default per l'esecuzione.
    """

    #MonocularWrapper
    modelsDefPath = "models.json"

    #FeatureTracker
    # - RANSAC
    planeNIterations = 25
    planeThreshold = 0.5

    lowe_threshold = 0.7
    norm_threshold = 0.7
    distance_threshold = 1.0

    #Calibrator
    # - Indica il quanto di spostamento del valore del monoculare
    # - Valori prossimi allo zero indicano scaleFactor più ripidi
    percentualeIncremento = 10  
    scaleFactor = 0.0012
    shiftFactor = -0.01
    # - Seleziona solo la parte inferiore dello schermo per la ricerca dei punti
    cutHalf = True
    # - RANSAC
    scaleNIterations = 25
    scaleNormalizedThreshold = 0.01
    #Sliding Window
    scaleFactorWindowSize = 20
    #Errore depth in metri
    depthErrorThreshold = 2.0
    viewCalibrationImg = False

    #CruiseControl
    cruiseWindowSize = 3
    skipThreshold = 0.5

    #Server
    addr = "127.0.0.1"
    tcpPort = 5050
    udpPort = 5051
    timeout = 60.0