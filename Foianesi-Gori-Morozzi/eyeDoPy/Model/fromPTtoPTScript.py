import torch
import torch.nn as nn
from torchvision.transforms import functional as F
from torchvision import transforms
import numpy as np
from PIL import Image
from loss import my_loss
from torch.utils.mobile_optimizer import optimize_for_mobile
from LYTNet import LYTNet

MODEL_PATH = '/home/user/Desktop/eyeDoPy/Model/_final_weights'
save_path = '/home/user/Desktop/eyeDoPy/Model/'


# Load the trained model from file
net = LYTNet()
net.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu'))) 
net.eval()

input_tensor = torch.rand(1, 3, 576, 768)
# conversion
script_model = torch.jit.trace(net,input_tensor)

# OPTIONAL: uncomment to switch on the optimizations for mobile
#script_model = optimize_for_mobile(script_model)

# saving
script_model.save(save_path + "not_optimized_float32.pt")


#SANITY CHECK
script_model.eval()
image = Image.open("testImage.JPG")
image = image.resize((768,576))

image = np.transpose(image, (2, 0, 1)) # Comment in case of normalization
        
#normalize image
#image = transforms.functional.to_tensor(image)
#image = transforms.functional.normalize(image, mean = [120.56737612047593, 119.16664454573734, 113.84554638827127], std=[66.32028460114392, 65.09469952002551, 65.67726614496246])

image = torch.FloatTensor([image]) # Comment in case of normalization

#Quantization (int-8) Dynamic
#net = torch.quantization.quantize_dynamic(net, {torch.nn.Linear,torch.nn.Sequential,net.modules}, dtype=torch.qint8)  # the target dtype for quantized weights

# Uncomment the following line for normalization
#image = image.unsqueeze(0)
pred_classes, pred_direc = net(image)
_, predicted = torch.max(pred_classes, 1)

print(pred_classes)
print(pred_direc)
print(predicted)
