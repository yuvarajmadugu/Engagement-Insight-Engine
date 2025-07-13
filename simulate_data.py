import json
import random
from datetime import datetime, timedelta

# Custom tag pools for realistic student interests
learning_goals = ["GRE", "CAT", "GATE", "AI", "UI/UX", "web development", "data science"]
quiz_topics = ["python", "java", "dsa", "ml", "aptitude", "sql"]
student_clubs = ["robotics", "ml-club", "arts", "coding"]
campus_events = ["tech-talk", "coding-contest", "startup-meetup"]

# Generate a past date string within a range
def get_random_past_date(max_days_back):
    return (datetime.today() - timedelta(days=random.randint(0, max_days_back))).strftime("%Y-%m-%d")

# Simulate one student's profile
def generate_student_profile(student_id):
    return {
        "user_id": student_id,
        "profile": {
            "resume_uploaded": random.choice([True, False]),
            "goal_tags": random.sample(learning_goals, k=2),
            "karma": random.randint(40, 500),
            "projects_added": random.randint(0, 6),
            "quiz_history": random.sample(quiz_topics, k=random.randint(0, 3)),
            "clubs_joined": random.sample(student_clubs, k=random.randint(0, 2)),
            "buddy_count": random.randint(0, 5)
        },
        "activity": {
            "login_streak": random.randint(0, 10),
            "posts_created": random.randint(0, 3),
            "buddies_interacted": random.randint(0, 5),
            "last_event_attended": get_random_past_date(90),
            "last_quiz_taken": get_random_past_date(120)
        }
    }

# Generate peer environment snapshot
def generate_peer_context():
    return {
        "batch_avg_projects": random.randint(1, 4),
        "batch_resume_uploaded_pct": random.randint(60, 95),
        "batch_event_attendance": {
            event: random.randint(2, 15) for event in campus_events
        },
        "buddies_attending_events": random.sample(campus_events, k=1)
    }

# Build dataset of 2000 students and 10 context snapshots
# synthetic data generation
student_data = [generate_student_profile(f"student_{7023 + i}") for i in range(2000)]
peer_contexts = [generate_peer_context() for _ in range(10)]

# Save output to files with naming conventions:
with open("simulated_profiles.json", "w") as profile_file:
    json.dump(student_data, profile_file, indent=2)

with open("peer_snapshot.json", "w") as peer_file:
    json.dump(peer_contexts, peer_file, indent=2)

print("Data of student profiles as: simulated_profiles.json")
print("Data of peer context is generated as: peer_snapshot.json ")
print("✅ Student and peer datasets generated.")
