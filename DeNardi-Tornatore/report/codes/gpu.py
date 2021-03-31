def gpu():
    config = ConfigProto()
    config.gpu_options.allow_growth = True
    sess = Session(config=config)
    
    if tf.test.gpu_device_name():
        log("GPU found")
    else:
        log("No GPU found")