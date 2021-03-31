self.batch_size = 128
self.epochs = 500

def train(self):
    self.hist = History()
    self.model.fit(self.X_train, 
                   self.y_train, 
                   batch_size=self.batch_size, 
                   epochs=self.epochs, 
                   verbose=1, 
                   validation_data=(self.X_val, self.y_val), 
                   callbacks=[self.hist])