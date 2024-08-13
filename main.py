import os
from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse
from fastapi.param_functions import File
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import io
from facenet_pytorch import MTCNN, InceptionResnetV1
import torch
from PIL import Image

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set the cache directory to a writable location
os.environ['TORCH_HOME'] = '/tmp/.cache/torch'

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

mtcnn = MTCNN(keep_all=True, device=device)
resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)


@app.get("/", tags=["Home"])
def read_root():
    return {"message": "Welcome to the face embeddings API!"}

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}



@app.post("/extract", tags=["Extract Embeddings"])
async def extract_embeddings(file: UploadFile = File(...)):
    # Load the image
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert('RGB')

    # Preprocess the image
    preprocessed_image = mtcnn(image)

    # Extract the face embeddings
    embeddings = resnet(preprocessed_image.unsqueeze(0)).detach().cpu().numpy().tolist()

    return JSONResponse(content={"embeddings": embeddings})


# @app.post("/extract")
# async def extract_embeddings(file: UploadFile = File(...)):
#     # Load the image
#     contents = await file.read()
#     image = face_recognition.load_image_file(io.BytesIO(contents))

#     # Find all the faces in the image
#     face_locations = face_recognition.face_locations(image)

#     # Initialize an empty list to store the face embeddings
#     embeddings = []

#     # Loop through each face location
#     for face_location in face_locations:
#         # Extract the face encoding
#         face_encoding = face_recognition.face_encodings(image, [face_location])[0]
        
#         # Append the face encoding to the embeddings list
#         embeddings.append(face_encoding.tolist())

#     return JSONResponse(content={"embeddings": embeddings})
