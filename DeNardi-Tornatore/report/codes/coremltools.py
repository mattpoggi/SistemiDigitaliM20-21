import coremltools
coreml_model = coremltools.converters.keras.convert(model)

coreml_model.author = 'De Nardi-Tornatore'
coreml_model.short_description = 'Recognition guitar music'

coreml_model.save("Stock.mlmodel")
