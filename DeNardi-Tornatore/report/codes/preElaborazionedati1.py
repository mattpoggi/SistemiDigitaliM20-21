self.con_win_size = 9
self.halfwin = con_win_size // 2
		
def load_data(self):
    for i in range(self.n_file):
        self.log("n." + str(i+1))
        inp = np.load(os.path.join(self.data_path, os.listdir(self.data_path)[i]))

        full_x = np.pad(inp["imgs"], [(self.halfwin,self.halfwin), (0,0)], mode='constant')

        for frame_idx in range(len(inp['imgs'])):
            # load a context window centered around the frame index
            sample_x = np.swapaxes(full_x[frame_idx : frame_idx+self.con_win_size],0,1)
            self.training_data.append((sample_x.astype('float64'), inp['labels'][frame_idx][::-1].astype('float64')))