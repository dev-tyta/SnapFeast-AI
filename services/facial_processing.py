import numpy as np
import os
import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
import logging
from PIL import Image

logger = logging.getLogger(__name__)

class FacialProcessing:
    def __init__(self):
        os.environ['TORCH_HOME'] = '/tmp/.cache/torch'
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.mtcnn = MTCNN(keep_all=True, device=self.device)
        self.resnet = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)

    def extract_embeddings_vgg(self, image_path):
        try:
            img = Image.open(image_path)
            img = img.convert('RGB')
            
            # Detect faces
            boxes, _ = self.mtcnn.detect(img)
            
            if boxes is None:
                logger.warning(f"No face detected in image: {image_path}")
                return None
            
            # Get the largest face
            largest_box = max(boxes, key=lambda box: (box[2] - box[0]) * (box[3] - box[1]))
            face = self.mtcnn(img, return_prob=False)
            
            if face is None:
                logger.warning(f"Failed to align face in image: {image_path}")
                return None
            
            # Extract embeddings
            embeddings = self.resnet(face).detach().cpu().numpy().flatten()
            return embeddings.tolist()
            
        except Exception as e:
            logger.error(f"An error occurred while extracting embeddings: {e}")
            return None

