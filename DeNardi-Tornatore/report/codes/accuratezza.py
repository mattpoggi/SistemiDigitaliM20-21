def test(self):
    # TEST: Load model and run it against test set
    r = random.randint(0, len(self.X_test))
    for i in range (r, r + 10):
        print("Answer:", self.y_test[i], "Prediction:", 
              self.model.predict(np.expand_dims(self.X_test[i], 0)))

    self.y_pred = self.model.predict(self.X_test)

def evaluate(self):
    # Evaluate model with test set
    results = self.model.evaluate(x=self.X_test, y=self.y_test)
    self.log("Test loss, Test acc: " + str(results))