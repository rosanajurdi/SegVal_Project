#!/usr/bin/env python3.6
'''
Script to compute metrics : Dice accuracy, hausdorf distance and the error on the number of connected components.
'''
import sys
import os, sys

from skimage.measure import label, regionprops
import torch.nn.functional as F
import matplotlib.pyplot as plt
from pathlib import Path

import numpy as np
import torch
from torch.autograd import Variable
import sys
import os
import csv

from utils import dice_coef, dice_batch, save_images, tqdm_, haussdorf, probs2one_hot, class2one_hot, numpy_haussdorf

root='/network/lustre/iss02/aramis/users/rosana.eljurdi/Validation_Project/BrainTumor/test_npy'
net_path = '/network/lustre/iss02/aramis/users/rosana.eljurdi/Validation_Project/BrainTumor/fold_1/results_500_3/best2.pkl'

net = torch.load(net_path, map_location=torch.device('cpu'))
n_classes = 4
n = 3

fieldnames = ['SLICE_ID', 'dice', 'haus']
fold_nb = net_path.split('/')[-2]
# assert os.path.exists(os.path.join(net_path.split(os.path.basename(net_path))[0], 'predictions'))== False

exp_path = net_path.split('/best2.pkl')[0]  # Include the name of the checkpoint you want to use
name = os.path.basename(exp_path)
folder_path = Path(exp_path, 'Patient_RESULTS')

# create the directory you want your result text files to be stored in
folder_path.mkdir(parents=True, exist_ok=True)
fold_all_H1 = open(os.path.join(folder_path, 'results.csv'.format(fold_nb)), "w")

fold_all_H1.write(f"file, dice, haussdorf,connecterror \n")

path = os.path.join(net_path.split(os.path.basename(net_path))[0])

savedir_npy = Path(folder_path, 'predictions_npyy')
savedir_img = Path(folder_path, 'predictions_imgy')
gt_savedir_img = Path(folder_path, 'gt_imgy')
gt_savedir_npy = Path(folder_path, 'gt_npyy')

savedir_npy.mkdir(parents=True, exist_ok=True)
savedir_img.mkdir(parents=True, exist_ok=True)
gt_savedir_img.mkdir(parents=True, exist_ok=True)
gt_savedir_npy.mkdir(parents=True, exist_ok=True)

for _, _, files in os.walk(os.path.join(root, 'in_npy')):

    print('walking into', os.path.join(root, 'in_npy'))
    for file in files:
        print(file)
        image = np.load(os.path.join(root, 'in_npy', file))
        gt = np.load(os.path.join(root, 'gt_npy', file))
        if len(np.unique(gt)) > 0:
            # print('infering {} of shape {} and classes {}, max {} and min {} '.format( file, image.shape, np.unique(gt), image.max(), image.min()))
            image = image.reshape(-1, 4, 240, 240)
            image = torch.tensor(image, dtype=torch.float)
            image = Variable(image, requires_grad=True)
            pred = net(image)
            pred = F.softmax(pred, dim=1).to('cpu')

            predicted_output = probs2one_hot(pred.detach())

            np.save(Path(savedir_npy, f"{file}"), pred.cpu().detach().numpy())

            plt.imsave(os.path.join(savedir_img, '{}.png'.format(file.split('.npy')[0])),
                       np.argmax(predicted_output, 1)[0])

            np.save(Path(gt_savedir_npy, f"{file}"), gt)

            plt.imsave(os.path.join(gt_savedir_img, '{}.png'.format(file.split('.npy')[0])),gt)


            # folders.write("hi")
            fold_all_H1.flush()










