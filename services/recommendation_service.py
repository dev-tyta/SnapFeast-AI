# recommender_system.py
import pandas as pd
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
import joblib
from datetime import datetime, timedelta
import os
import random
from sqlalchemy.orm import Session
from typing import List
from orders.models import Order, Meal
from users.models import User


class MealRecommender:
    def __init__(self, db: Session):
        self.db = db
        self.model_path = 'recommendation_model.joblib'
        self.last_train_path = 'last_train_time.txt'
        self.retrain_interval = timedelta(days=1)
        self.algo = self.load_or_train_model()

    def fetch_data(self):
        orders = self.db.query(Order).all()
        return pd.DataFrame([(order.user_id, order.meal_id, order.quantity) for order in orders], 
                            columns=['user_id', 'meal_id', 'quantity'])

    def train_model(self):
        data = self.fetch_data()
        if data.empty:
            self.algo = None
            return None
        
        reader = Reader(rating_scale=(1, 5))
        dataset = Dataset.load_from_df(data[['user_id', 'meal_id', 'quantity']], reader)
    
        trainset = dataset.build_full_trainset()
        algo = SVD()
        algo.fit(trainset)
        
        joblib.dump(algo, self.model_path)
        self._update_last_train_time()
        return algo

    def load_or_train_model(self):
        try:
            if self._should_retrain():
                return self.train_model()
            return joblib.load(self.model_path)
        except FileNotFoundError:
            return self.train_model()

    def _should_retrain(self):
        if not os.path.exists(self.last_train_path):
            return True
        with open(self.last_train_path, 'r') as f:
            last_train_time = datetime.fromisoformat(f.read().strip())
        return datetime.now() - last_train_time > self.retrain_interval

    def _update_last_train_time(self):
        with open(self.last_train_path, 'w') as f:
            f.write(datetime.now().isoformat())

    def get_recommendations(self, user: User):
        if self._should_retrain():
            self.algo = self.train_model()

        if self.algo is None:
            return self.get_random_recommendations()

        all_meals = self.db.query(Meal).all()
        meal_ids = [meal.id for meal in all_meals]

        predictions = [self.algo.predict(str(user.id), str(meal_id)) for meal_id in meal_ids]
        sorted_predictions = sorted(predictions, key=lambda x: x.est, reverse=True)
        top_recommendations = self.db.query(Meal).filter(Meal.id.in_([int(pred.iid) for pred in sorted_predictions[:20]])).all()

        top_recommendations = self.adjust_for_preferences(user, top_recommendations)

        return top_recommendations[:5]  # Return top 5 recommendations

    def adjust_for_preferences(self, user: User, recommendations: List[Meal]) -> List[Meal]:
        preferences = user.preferences if user.preferences else []
        preference_scores = {meal.id: 0 for meal in recommendations}

        for meal in recommendations:
            for preferred in preferences:
                if preferred.lower() in meal.name.lower() or preferred.lower() in meal.description.lower():
                    preference_scores[meal.id] += 1

        sorted_recommendations = sorted(recommendations, key=lambda meal: preference_scores[meal.id], reverse=True)

        return sorted_recommendations

    def get_random_recommendations(self):
        all_meals = self.db.query(Meal).all()
        return random.sample(all_meals, min(5, len(all_meals)))
