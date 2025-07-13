from datetime import datetime
import math

# Calculates a FOMO score based on buddy participation, batch activity, and recency of user participation
def calculate_event_fomo_score(user_data, peer_snapshot):
    BUDDY_WEIGHT = 0.4
    BATCH_WEIGHT = 0.3
    TIME_WEIGHT = 0.3
    MAX_DAYS_SINCE_EVENT = 30  # days

    # Buddy score based on how many buddies are attending events
    buddy_score = 0
    if user_data['profile']['buddy_count'] > 0:
        buddies_attending = len(peer_snapshot['buddies_attending_events'])
        buddy_score = min(buddies_attending / user_data['profile']['buddy_count'], 1.0)

    # Batch score is average normalized attendance across all events
    batch_scores = []
    for event, attendance in peer_snapshot['batch_event_attendance'].items():
        normalized_score = min(attendance / 10, 1.0)
        batch_scores.append(normalized_score)
    batch_score = sum(batch_scores) / len(batch_scores) if batch_scores else 0

    # Time score based on days since last attended event (up to 30 days)
    days_since_event = 999  # default large value if parsing fails
    try:
        if user_data['activity']['last_event_attended']:
            last_event_date = datetime.strptime(user_data['activity']['last_event_attended'], '%Y-%m-%d')
            days_since_event = (datetime.now() - last_event_date).days
    except Exception:
        pass  # keep default days_since_event = 999 if parsing fails

    time_score = min(days_since_event / MAX_DAYS_SINCE_EVENT, 1.0)

    # Weighted FOMO score
    fomo_score = (
        BUDDY_WEIGHT * buddy_score +
        BATCH_WEIGHT * batch_score +
        TIME_WEIGHT * time_score
    )
    fomo_score = 1 / (1 + math.exp(-5 * (fomo_score - 0.5)))  # sigmoid for normalization

    return round(fomo_score, 2), days_since_event  # Also return days_since_event for rule fallback

# Generates insights based on FOMO score and attendance gaps
def get_event_fomo_insights(user_data, peer_snapshot):
    fomo_score, days_since_event = calculate_event_fomo_score(user_data, peer_snapshot)

    insights = {
        'fomo_score': fomo_score,
        'fomo_level': 'low' if fomo_score < 0.3 else 'medium' if fomo_score < 0.7 else 'high',
        'factors': {
            'buddy_attendance': len(peer_snapshot['buddies_attending_events']),
            'total_buddies': user_data['profile']['buddy_count'],
            'days_since_last_event': days_since_event,
            'batch_attendance': peer_snapshot['batch_event_attendance']
        },
        'recommendation': "",
        'recommendations': [],
        'triggered_by_rule': days_since_event > 30
    }

    # Score-based recommendations
    if fomo_score > 0.7:
        insights['recommendations'].append("High FOMO detected! Consider attending upcoming events to stay connected with your peers.")
    elif fomo_score > 0.3:
        insights['recommendations'].append("Moderate FOMO level. Keep an eye on event announcements to maintain engagement.")

    # Explicit rule-based fallback: No event in over 30 days
    if days_since_event > 30:
        insights['recommendations'].append("You haven't attended any events in a while. Reconnect by joining upcoming events!")

    # Buddy presence suggestion
    if len(peer_snapshot['buddies_attending_events']) > 0:
        insights['recommendations'].append(f"Your buddies are attending: {', '.join(peer_snapshot['buddies_attending_events'])}")

    # Combine for rule-based title if needed
    insights['recommendation'] = insights['recommendations'][0] if insights['recommendations'] else "Stay engaged with upcoming events."

    return insights

# for verification that the file runs successfully:
print("event_fomo_score.py generated")
