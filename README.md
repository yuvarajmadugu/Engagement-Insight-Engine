# 🚀 Engagement Insight Engine
An AI-powered microservice that analyzes user engagement, compares peer behavior, and delivers smart nudges to help users glow up their profile and avoid missing out on key activities. Built with FastAPI, rule-based logic, and ML models — all fully offline and Docker-deployable.

Task1:
  Python Script – "simulate_data.py"
  Generates:
  2000 user profiles in simulate_profile.json
  10 peer snapshots  in peer_snapshot.json
  Fully offline and reproducible(avoids dataleakage)
  Note: The data is synthetic and generated using your custom logic.

Task2:
  Create - "generate_training_data.py"
  Generates:
  processed_fomo_dataset.csv
  Calculate - "event_fomo_score.py"
  Config - "config.json"
    project_rules,
    event_rules,
    priority_labels,
    thresholds.

Task3:
  Training model - "train_model.py"
  Generates:
  models/
    model_event.pkl
    model_resume.pkl
  Testing models - "train_model.py"
  Generates:
  *reports/
    classification_report.txt
    feature_importance_resume.png
    feature-importance_resume.csv
    final_feature.txt

Task4:
  Create "model.py"
    from pydantic importing BaseModels
    Creates: Example schema for Requestbody
    Creates: Example schema for Responsebody
  FastAPI Interface - "main.py"
    Rule based logic integrated,
    imports all the models
    Generates: "logfile" in root folder 
      All major API hits are logged to console (INFO level)
    Created all the requested Endpoints in (projectinfo.pdf provided by turtil)

Task5:
  Generate output messages and test cases in FastAPI's SwaggerUI

Task6:
  Containerized all the components of this project are into bundled into a single container:
  Ultimate "Dockerfie"
  Runs isolatedly in user space (Same or shared Operating System)
  Finalizied all requirements in "requirements.txt"
  Wrote final README:
    Explained all the tasks of this project and added all the bashes required and API guide

# Project Structure
projectCode/
├── main.py
├── models.py
├── config.json
├── event_fomo_score.py
├── generate_training_dataset.py
├── processed_fomo_dataset.csv
├── simulate_data.py
├── simulated_profile.json, peer_snapshot.json
├── train_model.py
├── models/
│   └── model_resume.pkl
│   └── model_event.pkl
├── reports/
│   └── *.csv, *.png
├── requirements.txt
├── Dockerfile
└── README.md

# 📌 Features
- ✅ Hybrid rule-based + ML engine
- ✅ Smart nudging system (Resume, Projects, Quizzes, Events)
- ✅ Peer comparison for FOMO detection
- ✅ Customizable via config.json
- ✅ Fully offline & Dockerized FastAPI microservice
- ✅ Is configurable, deterministic, offline, and served via FastAPI
- ✅ Swagger UI support for easy testing

# FastAPI Guide:
  Intially run "mains1.py" (that will redirect to web-browser)
  Click on "GET/health"
    "status":"ok"
  Click on "GET/version"
    "status":"1.0.0"
  Click on "POST/analyze-engagement"
    Example/Sample schema for Requestbody and Responsebody is visible.
  Click on "Try it out"
    Define your input payload as requested body:
    Note: Follow Datatype rules.
  Click on "Execute"
    On Execution, Analyze engagement and get nudges for the user on bases of defined input payload.

# Input Schema
{
  "user_data": {
    "user_id": "yuvi",
    "profile": {
      "resume_uploaded": true,
      "goal_tags": [
        "DSA","Java Developer"
      ],
      "karma": 286,
      "projects_added": 3,
      "quiz_history": [
        "string"
      ],
      "clubs_joined": [
        "dsa-java"
      ],
      "buddy_count": 10
    },
    "activity": {
      "login_streak": 10,
      "posts_created": 0,
      "buddies_interacted": 4,
      "last_event_attended": "2025-04-30"
    }
  },
  "peer_snapshot": {
    "batch_avg_projects": 3,
    "batch_resume_uploaded_pct": 88,
    "batch_event_attendance": {
      "additionalProp1": 0,
      "additionalProp2": 0,
      "additionalProp3": 0
    },
    "buddies_attending_events": [
      "coding context"
    ]
  }
}

# Output Schema
json:
{
  "status": "success",
  "nudges": [
    {
      "type": "profile",
      "title": "Upload Your Resume",
      "action": "Add your resume to improve visibility.",
      "priority": 1
    },
    {
      "type": "event_fomo",
      "title": "You Might Be Missing Out",
      "action": "Attend upcoming events to stay in sync with your peers.",
      "priority": 2
    }
  ]
}

# Running the API
# Local (with virtualenv)
bash/command: 
  uvicorn main:app --reload
Access API docs at:  
 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

 # Build Image in 🐳Docker
bash/command: 
  docker build -t engagement-insight-engine,
# Run Container
bash/command: 
  docker run -d -p 8000:8000 engagement-insight-engine

# Requirements
bash/command: 
  pip install -r requirements.txt

# Sample cURL Request
bash/command:
  curl -X POST "http://127.0.0.1:8000/analyze-engagement" \
       -H "Content-Type: application/json" \
      -d @sample_input.json

#  Acknowledgment
Special mention to ChatGPT and LLM's for end-to-end mentorship on this project.
Credits:
  Some explanations and code suggestions were refined using AI tools(llm's), but the final implementation and interpretation are entirely original.

# License
This project is developed for academic and non-commercial use under Turtil internship guidelines.

# Contributions
For questions, contact:  
  Work mail:`yuvarajm@turtilintern.com`
  Personal mail: `yuvarajmadugu@gmail.com`