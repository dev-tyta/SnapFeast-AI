from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sqlalchemy.orm import Session
from users.models import UserEmbeddings

class FaceMatch:
    def __init__(self, db: Session):
        self.db = db

    def load_embeddings_from_db(self):
        user_embeddings = self.db.query(UserEmbeddings).all()
        return {ue.user_id: np.array(ue.embeddings) for ue in user_embeddings}

    def match_faces(self, new_embeddings, saved_embeddings, threshold=0.6):
        new_embeddings = np.array(new_embeddings)
        max_similarity = 0
        identity = None

        for user_id, stored_embeddings in saved_embeddings.items():
            similarity = cosine_similarity(new_embeddings.reshape(1, -1), stored_embeddings.reshape(1, -1))[0][0]
            if similarity > max_similarity:
                max_similarity = similarity
                identity = user_id

        return identity, max_similarity if max_similarity > threshold else (None, 0)

    def new_face_matching(self, new_embeddings):
        embeddings_dict = self.load_embeddings_from_db()
        if not embeddings_dict:
            return {'status': 'Error', 'message': 'No embeddings available'}

        identity, similarity = self.match_faces(new_embeddings, embeddings_dict)
        if identity:
            return {
                'status': 'Success',
                'message': 'Match Found',
                'user_id': identity,
                'similarity': similarity
            }
        return {
            'status': 'Error',
            'message': 'No matching face found'
        }

