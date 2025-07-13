from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from models import EngagementRequest, EngagementResponse, Nudge
from event_fomo_score import get_event_fomo_insights
import joblib
import json
import os
import numpy as np
import logging
import webbrowser
from datetime import datetime 
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

# ---------------- LOGGING ----------------
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.FileHandler(f"{log_dir}/app.log", mode='a'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ---------------- CONFIG & MODELS ----------------
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
with open(CONFIG_PATH) as f:
    CONFIG = json.load(f)

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
model_resume = joblib.load(os.path.join(MODEL_DIR, "model_resume.pkl"))
model_event = joblib.load(os.path.join(MODEL_DIR, "model_event.pkl"))

# ---------------- FASTAPI APP ----------------
app = FastAPI(
    title="Engagement Insight Engine",
    description="AI-based microservice for profile analysis and engagement nudging",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "service": "Engagement Insight Engine",
        "version": "1.0.0",
        "creator": "YuvarajMadugu",
        "status": "running"
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/version")
def version():
    return {"version": "1.0.0"}

@app.on_event("startup")
async def startup_event():
    webbrowser.open("http://127.0.0.1:8000/docs")

# === GLOBAL ERROR HANDLER FOR UNCAUGHT EXCEPTIONS ===
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error. Check logs for details."}
    )

# === VALIDATION ERROR HANDLER ===
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

@app.post("/analyze-engagement", response_model=EngagementResponse)
def analyze_engagement(payload: EngagementRequest):
    try:
        user = payload.user_data
        profile = user.profile
        activity = user.activity
        peer = payload.peer_snapshot

        nudges = []
        logger.info(f"Analyzing engagement for user: {user.user_id}")

        # === Resume ===
        if not profile.resume_uploaded and peer.batch_resume_uploaded_pct > CONFIG["profile_rules"]["resume_threshold"] * 100:
            logger.info("Triggering resume upload rule-based nudge.")
            nudges.append(Nudge(
                type="profile",
                title=f"{peer.batch_resume_uploaded_pct}% of your peers have uploaded resumes. You haven’t yet!",
                action="Upload resume now",
                priority=CONFIG["priority_labels"]["resume"]
            ))

        # === Projects ===
        if profile.projects_added == 0 and peer.batch_avg_projects >= CONFIG["profile_rules"]["projects_avg_threshold"]:
            logger.info("Triggering project-based rule nudge.")
            nudges.append(Nudge(
                type="profile",
                title="You haven't added any projects. Your peers have a head start!",
                action="Showcase your work by adding a project.",
                priority=CONFIG["priority_labels"]["project"]
            ))

        # === Buddies Attending Events ===
        if len(peer.buddies_attending_events) >= CONFIG["engagement_rules"]["buddies_event_threshold"]:
            logger.info("Triggering buddies attending event nudge.")
            nudges.append(Nudge(
                type="event",
                title="Several of your buddies are attending events!",
                action="Join them and don’t miss the opportunity.",
                priority=CONFIG["priority_labels"]["event_fomo"]
            ))

        # === Large Peer Event Attendance ===
        if any(count >= CONFIG["engagement_rules"]["event_peer_threshold"] for count in peer.batch_event_attendance.values()):
            logger.info("Triggering peer event attendance rule nudge.")
            nudges.append(Nudge(
                type="event",
                title="Many peers are attending trending events.",
                action="Check them out and participate!",
                priority=CONFIG["priority_labels"]["event_fomo"]
            ))

        # === Quiz Inactivity Nudge (quiz_history with dates only) ===
        try:
            quiz_dates = [datetime.strptime(q, "%Y-%m-%d") for q in profile.quiz_history if '-' in q]
            if quiz_dates:
                last_quiz_date = max(quiz_dates)
                if (datetime.now() - last_quiz_date).days > CONFIG["engagement_rules"]["quiz_inactive_days"]:
                    logger.info("Triggering quiz inactivity rule-based nudge.")
                    nudges.append(Nudge(
                        type="profile",
                        title="It’s been a while since your last quiz!",
                        action="Sharpen your skills with a new quiz today.",
                        priority=CONFIG["priority_labels"]["quiz"]
                    ))
        except Exception as e:
            logger.warning(f"Quiz date parse failed: {e}")

        # === Comeback Event Nudge ===
        if activity.last_event_attended:
            last_event_date = datetime.strptime(str(activity.last_event_attended), "%Y-%m-%d")
            if (datetime.now() - last_event_date).days > CONFIG["engagement_rules"]["user_inactive_days"]:
                logger.info("Triggering comeback event nudge.")
                nudges.append(Nudge(
                    type="event",
                    title="You’ve been inactive lately. Time to re-engage!",
                    action="Explore new events and meet like-minded peers.",
                    priority=CONFIG["priority_labels"]["comeback"]
                ))

        # === FOMO ===
        fomo = get_event_fomo_insights(user.dict(), peer.dict())
        days_since_event = 0
        try:
            if activity.last_event_attended:
                last_event = datetime.strptime(str(activity.last_event_attended), "%Y-%m-%d")
                days_since_event = (datetime.now() - last_event).days
        except Exception as e:
            logger.warning(f"Date parse failed: {e}")

        if fomo["fomo_score"] >= CONFIG["profile_rules"]["event_fomo_threshold"] or days_since_event > 30:
            logger.info("Triggering event FOMO rule-based nudge.")
            nudges.append(Nudge(
                type="event",
                title=f"{fomo['fomo_level'].capitalize()} event FOMO detected",
                action=". ".join(fomo["recommendations"]),
                priority=CONFIG["priority_labels"]["event_fomo"]
            ))

        # === Resume ===
        if len(nudges) < 3:
            try:
                features = {
                    "karma": profile.karma,
                    "projects_added": profile.projects_added,
                    "resume_uploaded": int(profile.resume_uploaded),
                    "batch_resume_uploaded_pct": peer.batch_resume_uploaded_pct
                }
                input_array = np.array([features[col] for col in model_resume.feature_names_in_]).reshape(1, -1)
                prob = model_resume.predict_proba(input_array)[0][1]
                logger.info(f"Resume ML model prob: {prob}")

                if prob >= CONFIG["ml_rules"]["nudge_probability_threshold"]:
                    logger.info("ML-based resume nudge triggered.")
                    nudges.append(Nudge(
                        type="profile",
                        title="AI thinks uploading your resume could boost your visibility!",
                        action="Update your profile with a resume.",
                        priority="medium"
                    ))
            except Exception as e:
                logger.error(f"Resume ML model failed: {e}")

        # === Event ===
        if len(nudges) < 3:
            try:
                features = {
                    "karma": profile.karma,
                    "resume_uploaded": int(profile.resume_uploaded),
                    "event_fomo_score": fomo["fomo_score"],
                    "batch_attending_events_count": peer.batch_attending_events_count
                }
                input_array = np.array([features[col] for col in model_event.feature_names_in_]).reshape(1, -1)
                prob = model_event.predict_proba(input_array)[0][1]
                logger.info(f"Event ML model prob: {prob}")

                if prob >= CONFIG["ml_rules"]["nudge_probability_threshold"]:
                    logger.info("ML-based event nudge triggered.")
                    nudges.append(Nudge(
                        type="event",
                        title="AI suggests you may benefit from attending events!",
                        action="Look out for upcoming events to join.",
                        priority="medium"
                    ))
            except Exception as e:
                logger.error(f"Event ML model failed: {e}")

        # === FALLBACK if nufges < 3 ===
        while len(nudges) < 3:
            logger.info("Adding fallback nudge.")
            nudges.append(Nudge(
                type="profile",
                title="Stay active to grow your presence!",
                action="Explore community features and attend events.",
                priority="low"
            ))

        return EngagementResponse(
            user_id=user.user_id,
            nudges=nudges[:3],
            status="generated"
        )

    except Exception as e:
        logger.exception(f"Unexpected failure for user {payload.user_data.user_id}: {e}")
        fallback_nudges = [
            Nudge(
                type="profile",
                title="We encountered an error analyzing your engagement.",
                action="Please try again later or contact support.",
                priority="low"
            )
        ]
        return EngagementResponse(
            user_id=payload.user_data.user_id,
            nudges=fallback_nudges,
            status="generated"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
