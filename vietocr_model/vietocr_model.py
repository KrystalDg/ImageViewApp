from PIL import Image as pil
from PIL import Image
from pkg_resources import parse_version
if parse_version(pil.__version__)>=parse_version('10.0.0'):
    Image.ANTIALIAS=Image.LANCZOS

import warnings
warnings.filterwarnings("ignore")

from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg


class OCRModel(object):
    def __init__(self, weight_path=None):
        if weight_path != None:
            self.weight_path = weight_path
        else:
            self.weight_path = "vietocr_model/weights/vgg_transformer_default.pth"

        self.config = Cfg.load_config_from_name('vgg_transformer')
        self.config['weights'] = self.weight_path
        self.config['cnn']['pretrained']=False
        self.config['device'] = 'cpu'
        self.config['predictor'].update({'beamsearch': True})

        self.detector = Predictor(self.config)

    def recognize(self, img):
        s = self.detector.predict(img)
        return s


if __name__ == "__main__":
    ocr = OCRModel("vietocr_model/weights/transformerocr_custom.pth")
    # ocr = OCRModel()
    img = Image.open('test_image/2.jpg')
    s = ocr.recognize(img)
    print(s)
