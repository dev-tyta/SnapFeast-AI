from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sqlalchemy.orm import Session
from users.models import UserEmbeddings
from core.config import get_settings

settings = get_settings()

class FaceMatch:
    def __init__(self, db: Session):
        self.db = db
        self.threshold = settings.FACE_RECOGNITION_THRESHOLD

    def load_embeddings_from_db(self):
        user_embeddings = self.db.query(UserEmbeddings).all()
        return {ue.user_id: np.array(ue.embeddings) for ue in user_embeddings}

    def match_faces(self, new_embeddings, saved_embeddings):
        new_embeddings = np.array(new_embeddings)
        max_similarity = 0
        identity = None

        for user_id, stored_embeddings in saved_embeddings.items():
            similarity = cosine_similarity(new_embeddings.reshape(1, -1), stored_embeddings.reshape(1, -1))[0][0]
            if similarity > max_similarity:
                max_similarity = similarity
                identity = user_id

        return identity, max_similarity if max_similarity > self.threshold else (None, 0)

    def new_face_matching(self, new_embeddings):
        embeddings_dict = self.load_embeddings_from_db()
        if not embeddings_dict:
            return {'status': 'Error', 'message': 'No embeddings available in the database'}

        identity, similarity = self.match_faces(new_embeddings, embeddings_dict)
        if identity:
            return {
                'status': 'Success',
                'message': 'Match Found',
                'user_id': identity,
                'similarity': float(similarity)  # Convert numpy float to Python float
            }
        return {
            'status': 'Error',
            'message': 'No matching face found'
        }