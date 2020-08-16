import cv2
import torch
import numpy as np
import torchvision.transforms as trans
import matplotlib.pyplot as plt
from PIL import Image
from torchvision import models

class BackgroundRemover:

    SCALED_SIZE = 256
    IMAGENET_MEAN = [0.485, 0.456, 0.406]
    IMAGENET_STD = [0.229, 0.224, 0.225]

    dlab = models.segmentation.deeplabv3_resnet101(pretrained=True).eval()

    def __init__(self, cap):
        """
        :param cap: cv2.VideoCapture
        """
        self.cap = cap

    def process(self, output_name="output", device="cpu", verbose=False):
        if self.cap.isOpened():
            width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            fps = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

        output_name = f"{output_name}.avi"
        fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
        output_dim = self._calculate_output_dim(width, height)

        if verbose:
            print("Video Stats")
            print(f"\t width: {width}")
            print(f"\t height: {height}")
            print(f"\t fps: {fps}")
            print(f"\t output dim: {output_dim}")
        out = cv2.VideoWriter(output_name, fourcc, fps, output_dim)

        iter = 60
        i = 0
        while self.cap.isOpened():
            ret, frame = self.cap.read()

            if ret:
                i += 1
                if i % iter == 0:
                    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    out.write(cv2.cvtColor(self._segment(image, dev=device, show_imgs=verbose), cv2.COLOR_RGB2BGR))
            else:
                break

        self.cap.release()
        out.release()
        return output_name

    def _calculate_output_dim(self, width, height):
        if height > width:
            return (self.SCALED_SIZE, int(self.SCALED_SIZE * height / width))
        else:
            return (int(width / height * self.SCALED_SIZE), self.SCALED_SIZE)

    def _segment(self, image, show_imgs=False, dev="cpu"):
        trf = trans.Compose([
            trans.Resize(self.SCALED_SIZE),
            trans.ToTensor(),
            trans.Normalize(mean = self.IMAGENET_MEAN, std = self.IMAGENET_STD)
        ])
        inp = trf(image).unsqueeze(0).to(dev)
        out = self.dlab.to(dev)(inp)['out']
        om = torch.argmax(out.squeeze(), dim=0).detach().cpu().numpy()
        mask = self._decode_segmap(om)
        result = self._remove_background(image, mask)

        if show_imgs:
            print("Original Image")
            plt.axis('off')
            plt.imshow(image)
            plt.show()
            
            print("Mask")
            plt.axis('off')
            plt.imshow(mask)
            plt.show()

            print("Image w/ Background Removed")
            plt.axis('off')
            plt.imshow(result)
            plt.show()

        return (result * 255).astype(np.uint8)
        
    def _decode_segmap(self, image, nc=21):
        """
        :param image: PIL.image
        """
        label_colors = np.array([(0, 0, 0),  # 0=background
            # 1=aeroplane, 2=bicycle, 3=bird, 4=boat, 5=bottle
            (128, 0, 0), (0, 128, 0), (128, 128, 0), (0, 0, 128), (128, 0, 128),
            # 6=bus, 7=car, 8=cat, 9=chair, 10=cow
            (0, 128, 128), (128, 128, 128), (64, 0, 0), (192, 0, 0), (64, 128, 0),
            # 11=dining table, 12=dog, 13=horse, 14=motorbike, 15=person
            (192, 128, 0), (64, 0, 128), (192, 0, 128), (64, 128, 128), (192, 128, 128),
            # 16=potted plant, 17=sheep, 18=sofa, 19=train, 20=tv/monitor
            (0, 64, 0), (128, 64, 0), (0, 192, 0), (128, 192, 0), (0, 64, 128)])
        
        r = np.zeros_like(image).astype(np.uint8)
        g = np.zeros_like(image).astype(np.uint8)
        b = np.zeros_like(image).astype(np.uint8)

        for l in range(0, nc):
            idx = image == l
            r[idx] = label_colors[l, 0]
            g[idx] = label_colors[l, 1]
            b[idx] = label_colors[l, 2]

        mask = np.stack([r, g, b], axis=2)
        return mask

    def _remove_background(self, original_image, mask):
        """
        :param original_image: PIL.Image
        :param mask: np.ndarray
        """
        # Resize the original image to the size of the mask
        image = cv2.resize(np.asarray(original_image), (mask.shape[1],mask.shape[0]))

        # Create a background array to hold white pixels
        # with the same size as mask output map
        background = np.zeros_like(mask).astype(np.uint8)

        # Convert uint8 to float
        image = image.astype(float)

        # Create a binary mask of the mask output map using the threshold value 0
        th, alpha = cv2.threshold(np.array(mask), 0, 255, cv2.THRESH_BINARY)

        # Apply a slight blur to the mask to soften edges
        alpha = cv2.GaussianBlur(alpha, (7,7), 0)

        # Normalize the alpha mask to keep intensity between 0 and 1
        alpha = alpha.astype(float) / 255

        # Multiply the image with the alpha matte
        image = cv2.multiply(alpha, image)

        # Return a normalized output image for display
        return image / 255
