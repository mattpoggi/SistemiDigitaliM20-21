def load_data(self):
    # Load features sets
    features_sets = np.load(os.path.join("data/", self.feature_sets_file))

    # Assign feature sets
    X_train = features_sets['X_train']
    X_val = features_sets['X_val']

    self.y_train = features_sets['y_train']
    self.y_val = features_sets['y_val']

    # CNN for TF expects (batch, height, width, channels)
    # So we reshape the input tensors with a "color" channel of 1
    self.X_train = X_train.reshape(X_train.shape[0], 
                                   X_train.shape[1], 
                                   X_train.shape[2], 
                                   1)
    self.X_val = X_val.reshape(X_val.shape[0], 
                               X_val.shape[1], 
                               X_val.shape[2], 
                               1)