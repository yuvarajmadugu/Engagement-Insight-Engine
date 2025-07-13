import json
import pandas as pd
import random
from event_fomo_score import calculate_event_fomo_score

#Load simulated user profiles
with open("simulated_profiles.json", "r") as user_file:
    user_profiles = json.load(user_file)

# Load peer-related behavioral context
with open("peer_snapshot.json", "r") as peer_file:
    peer_data = json.load(peer_file)

# Defensive check
if not isinstance(peer_data, list):
    raise ValueError("'peer_snapshot.json' must contain a list of peer context snapshots.")

#Container for the final dataset
training_records = []

#Process each user profile with a randomly selected peer context
for user in user_profiles:
    peer_context = random.choice(peer_data)

    #Compute FOMO score using utility function
    try:
        fomo_value, _ = calculate_event_fomo_score(user, peer_context)
    except Exception as e:
        print(f"Error in FOMO score calculation for user {user.get('user_id')}: {e}")
        continue

    #Extract relevant profile and peer features
    has_resume = int(user.get("profile", {}).get("resume_uploaded", False))
    user_karma = user.get("profile", {}).get("karma", 0)
    project_count = user.get("profile", {}).get("projects_added", 0)
    resume_upload_percent = peer_context.get("batch_resume_uploaded_pct", 0)

    #Generate labels using deterministic rules
    label_nudge_resume = int(not has_resume and resume_upload_percent > 80)
    label_nudge_event = int(fomo_value >= 0.5)

    #Append processed record
    training_records.append({
        "resume_uploaded": has_resume,
        "karma": user_karma,
        "projects_added": project_count,
        "batch_resume_uploaded_pct": resume_upload_percent,
        "event_fomo_score": fomo_value,
        "should_nudge_resume": label_nudge_resume,
        "should_nudge_event": label_nudge_event
    })

# 🧾 Convert to DataFrame and export as CSV
df = pd.DataFrame(training_records)
df.to_csv("processed_fomo_dataset.csv", index=False)

# 📊 Show label distribution for verification
print("\n🔍 Label Value Counts:")
print("should_nudge_resume:")
print(df["should_nudge_resume"].value_counts())
print("\nshould_nudge_event:")
print(df["should_nudge_event"].value_counts())

print("\n✅ Training dataset saved as 'processed_fomo_dataset.csv'")
