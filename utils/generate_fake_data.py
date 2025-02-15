import random
from datetime import datetime, timedelta
import pymongo
from faker import Faker

from settings import settings

fake = Faker()

# Connect to MongoDB
client = pymongo.MongoClient(settings.DATABASE_HOST)
db = client[settings.DATABASE_NAME]
collection = db["user_data"]

# Generate 60 days of synthetic data
base_date = datetime(2025, 1, 1)
num_days = 60

synthetic_users = []

for _ in range(50):  # Generate 50 synthetic users
    user_id = fake.uuid4()
    entry_date = base_date
    
    for _ in range(num_days):
        # Generate daily mood data
        moods = []
        for _ in range(random.randint(1, 3)):  # 1-3 mood entries per day
            moods.append({
                "timestamp": entry_date + timedelta(hours=random.randint(8, 20)),
                "mood": random.choice(["Happy", "Neutral", "Anxious", "Sad", "Depressed"])
            })
        
        # Generate panic episodes
        panic_episodes = []
        if random.random() < 0.3:  # 30% chance of panic episodes
            for _ in range(random.randint(1, 3)):
                panic_episodes.append(entry_date + timedelta(hours=random.randint(0, 23)))
        
        # Generate chat durations
        chat_durations = []
        if random.random() < 0.4:  # 40% chance of chat sessions
            for _ in range(random.randint(1, 2)):
                chat_durations.append(random.randint(5, 45))
        
        # Generate stressor data
        stressors = {
            "work": random.randint(0, 10),
            "relationships": random.randint(0, 8),
            "health": random.randint(0, 6),
            "financial": random.randint(0, 5)
        }
        
        # Create activity impact data
        activity_impact = {
            "Exercise": {"positive": random.randint(60, 85), "neutral": random.randint(10, 30), "negative": random.randint(0, 10)},
            "Meditation": {"positive": random.randint(50, 75), "neutral": random.randint(15, 35), "negative": random.randint(0, 15)},
            "Social Activities": {"positive": random.randint(55, 80), "neutral": random.randint(10, 30), "negative": random.randint(0, 15)}
        }
        
        # Create document structure
        document = {
            "user_id": user_id,
            "date": entry_date,
            "mood_history": moods,
            "panic_episodes": panic_episodes,
            "chat_durations": chat_durations,
            "stressors": stressors,
            "activity_impact": activity_impact,
            "device_type": random.choice(["mobile", "desktop", "tablet"]),
            "location": fake.country_code()
        }
        
        synthetic_users.append(document)
        entry_date += timedelta(days=1)

# Insert into MongoDB
collection.insert_many(synthetic_users)
