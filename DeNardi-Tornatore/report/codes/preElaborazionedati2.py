def prepare_data(self, data):
    inp = []
    out = []
    
    for imgs, labels in data:
        inp.append(imgs)
        out.append(labels)
    return inp, out

def partition_data(self):
    # Randomize training set
    random.shuffle(self.training_data)

    X_train, y_train = self.prepare_data(self.training_data)

    # Calculate validation and test set sizes
    val_set_size = int(len(self.training_data) * 0.1)
    test_set_size = int(len(self.training_data) * 0.1)

    # Break x apart into train, validation, and test sets
    self.X_val = X_train[:val_set_size]
    self.X_test = X_train[val_set_size:(val_set_size + test_set_size)]
    self.X_train = X_train[(val_set_size + test_set_size):]

    # Break y apart into train, validation, and test sets
    self.y_val = y_train[:val_set_size]
    self.y_test = y_train[val_set_size:(val_set_size + test_set_size)]
    self.y_train = y_train[(val_set_size + test_set_size):]

    self.log("Train set size: " + str(len(self.X_train)))
    self.log("Validation set size: " + str(len(self.X_val)))
    self.log("Test set size: " + str(len(self.X_test)))