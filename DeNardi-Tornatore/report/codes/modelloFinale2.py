from tensorflow.keras import backend as K

def softmax_by_string(self, t):
    sh = K.shape(t)
    string_sm = []
    for i in range(self.num_strings):
        string_sm.append(K.expand_dims(K.softmax(t[:,i,:]), axis=1))
    return K.concatenate(string_sm, axis=1)

def catcross_by_string(self, target, output):
    loss = 0
    for i in range(self.num_strings):
        loss += K.categorical_crossentropy(target[:,i,:], output[:,i,:])
    return loss

def avg_acc(self, y_true, y_pred):
    return K.mean(K.equal(K.argmax(y_true, axis=-1), K.argmax(y_pred, axis=-1)))