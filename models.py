from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import date

#Nested Models
class Profile(BaseModel):
    resume_uploaded: bool
    goal_tags: List[str]
    karma: int
    projects_added: int
    quiz_history: List[str]
    clubs_joined: List[str]
    buddy_count: int

class Activity(BaseModel):
    login_streak: int
    posts_created: int
    buddies_interacted: int
    last_event_attended: Optional[date]

class PeerSnapshot(BaseModel):
    batch_avg_projects: float
    batch_resume_uploaded_pct: float
    batch_event_attendance: Dict[str, int]
    buddies_attending_events: List[str]

class UserData(BaseModel):
    user_id: str
    profile: Profile
    activity: Activity

class EngagementRequest(BaseModel):
    user_data: UserData
    peer_snapshot: PeerSnapshot

    class Config:
        json_schema_extra = {
            "example": {
                "user_data": {
                    "user_id": "stu_7023",
                    "profile": {
                        "resume_uploaded": False,
                        "goal_tags": ["GRE", "data science"],
                        "karma": 190,
                        "projects_added": 0,
                        "quiz_history": ["2024-06-01"], #yyyy-mm-dd
                        "clubs_joined": [],
                        "buddy_count": 3
                    },
                    "activity": {
                        "login_streak": 2,
                        "posts_created": 1,
                        "buddies_interacted": 0,
                        "last_event_attended": "2024-06-30" #yyyy-mm-dd
                    }
                },
                "peer_snapshot": {
                    "batch_avg_projects": 2,
                    "batch_resume_uploaded_pct": 84,
                    "batch_event_attendance": {
                        "startup-meetup": 5,
                        "coding-contest": 9
                    },
                    "buddies_attending_events": ["coding-contest"]
                }
            }
        }

#Output Model
class Nudge(BaseModel):
    type: str
    title: str
    action: str
    priority: str

class EngagementResponse(BaseModel):
    user_id: str
    nudges: List[Nudge]
    status: str

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "u1234",
                "nudges": [
                    {
                        "type": "profile",
                        "title": "95% of your peers have uploaded resumes. You haven’t yet!",
                        "action": "Upload your resume to stay competitive.",
                        "priority": "high"
                    },
                    {
                        "type": "event",
                        "title": "Most of your buddies are attending events.",
                        "action": "Don’t miss out! Join an upcoming event today.",
                        "priority": "high"
                    },
                    {
                        "type": "profile",
                        "title": "You haven't added any projects. Your peers have a head start!",
                        "action": "Showcase your work by adding a project.",
                        "priority": "medium"
                    }
                ],
                "status": "generated"
            }
        }
