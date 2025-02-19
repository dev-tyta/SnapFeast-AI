import numpy as np
import os
import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
import cv2
import logging

logger = logging.getLogger(__name__)


class FacialProcessing:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.model = cv2.dnn.readNetFromTorch('openface.nn4.small2.v1.t7')
        # Set the cache directory to a writable location
        os.environ['TORCH_HOME'] = '/tmp/.cache/torch'

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        self.mtcnn = MTCNN(keep_all=True, device=device)
        self.resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)


    def extract_embeddings(self, image_path):
        try:
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Failed to load image: {image_path}")
                return None
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            if len(faces) == 0:
                logger.warning(f"No face detected in image: {image_path}")
                return None
            
            (x, y, w, h) = faces[0]
            face = image[y:y+h, x:x+w]
            
            faceBlob = cv2.dnn.blobFromImage(face, 1.0 / 255, (96, 96), (0, 0, 0), swapRB=True, crop=False)
            self.model.setInput(faceBlob)
            vec = self.model.forward()
            
            return vec.flatten().tolist()
        except Exception as e:
            logger.error(f"An error occurred while extracting embeddings: {e}")
            return None


    def extract_embeddings_vgg(self, image):
        try:
            # Preprocess the image
            preprocessed_image = self.mtcnn(image)

            if preprocessed_image is None:
                logger.warning(f"No face detected in image")
                return None
            
            # Extract the face embeddings
            embeddings = self.resnet(preprocessed_image.unsqueeze(0)).detach().cpu().numpy().tolist()
            if embeddings:
                return embeddings[0]
            
        except Exception as e:
            logger.error(f"An error occurred while extracting embeddings: {e}")
            return None
