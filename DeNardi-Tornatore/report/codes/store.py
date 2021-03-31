def store(self, n, num_frames):
    save_path = self.save_path
    filename = self.get_filename(n)
	
    self.output["imgs"] = self.imgs
    self.output["labels"] = self.labels

    if not os.path.exists(save_path):
        os.makedirs(save_path)
    self.save_data(save_path + filename + ".npz")