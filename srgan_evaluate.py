#cluster stuff, remove this
import sys
sys.path.append("/home/adamvest/lib/python")

import options, data, models, helpers
from torch import cuda
from torch.autograd import Variable


args = options.SRGANTestOptions().parse()
datasets = data.build_evaluation_dataset(args)
srgan = models.SRGAN(args)

if args.use_cuda:
    cuda.manual_seed(args.seed)
    srgan.to_cuda()

for dataset_name, (hr_imgs, lr_imgs) in datasets.iteritems():
    total_psnr, total_ssim, rgb_psnr = 0.0, 0.0, 0.0
    sr_imgs = []

    for i in range(len(lr_imgs)):
        lr_img = Variable(lr_imgs[i].unsqueeze(0), volatile=True)
        sr_img = srgan.super_resolve(lr_img)
        sr_imgs.append(sr_img.data[0])
        rgb_psnr += helpers.compute_rgb_psnr(sr_img, hr_imgs[i])
        psnr, ssim = helpers.compute_statistics(sr_img, hr_imgs[i])
        total_psnr += psnr
        total_ssim += ssim
        del sr_img

    helpers.save_sr_results(args, dataset_name, sr_imgs)
    print "Dataset " + dataset_name + " PSNR: " + str(total_psnr / len(lr_imgs)) + \
            " SSIM: " + str(total_ssim / len(lr_imgs)) + " RGB PSNR: " + str(rgb_psnr / len(lr_imgs))
