import pandas as pd
import joblib
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
import os

# Load dataset
df = pd.read_csv("processed_fomo_dataset.csv")

# Features and labels
X = df.drop(columns=["should_nudge_resume", "should_nudge_event"])
y_resume = df["should_nudge_resume"]
y_event = df["should_nudge_event"]

# Split data
X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(X, y_resume, test_size=0.2, random_state=42)
X_train_e, X_test_e, y_train_e, y_test_e = train_test_split(X, y_event, test_size=0.2, random_state=42)

# Train resume model (no feature filtering)
model_resume = LogisticRegression(max_iter=1000)
model_resume.fit(X_train_r, y_train_r)

# Train event model
model_event = LogisticRegression(max_iter=1000)
model_event.fit(X_train_e, y_train_e)

# Make directories
os.makedirs("models", exist_ok=True)
os.makedirs("reports", exist_ok=True)

# Save models
joblib.dump(model_resume, "models/model_resume.pkl")
joblib.dump(model_event, "models/model_event.pkl")

# Evaluate resume model
y_pred_r = model_resume.predict(X_test_r)
report_r = classification_report(y_test_r, y_pred_r)
accuracy_r = accuracy_score(y_test_r, y_pred_r)
cv_scores_r = cross_val_score(model_resume, X, y_resume, cv=5)

# Evaluate event model
y_pred_e = model_event.predict(X_test_e)
report_e = classification_report(y_test_e, y_pred_e)
accuracy_e = accuracy_score(y_test_e, y_pred_e)
cv_scores_e = cross_val_score(model_event, X, y_event, cv=5)

# Save reports
with open("reports/classification_report.txt", "w") as f:
    f.write("Resume Nudge Model:\n")
    f.write(report_r)
    f.write(f"\nAccuracy: {accuracy_r:.2%}\n")
    f.write(f"5-Fold CV Accuracy: {cv_scores_r.mean():.2%}\n")

    f.write("\n\nEvent Nudge Model:\n")
    f.write(report_e)
    f.write(f"\nAccuracy: {accuracy_e:.2%}\n")
    f.write(f"5-Fold CV Accuracy: {cv_scores_e.mean():.2%}\n")

# Feature importance plot (resume)
resume_importance = pd.Series(model_resume.coef_[0], index=X.columns).sort_values()
resume_importance.to_csv("reports/feature_importance_resume.csv")
resume_importance.plot(kind='barh', title="Resume Nudge Model - Feature Importance", color='lightgreen')
plt.tight_layout()
plt.grid(True, linestyle='--', alpha=0.5)
plt.savefig("reports/feature_importance_resume.png")
plt.close()

print("✅ Models trained and saved in 'models/' folder.")
print("📊 Reports and plots saved in 'reports/' folder.")


train_acc = model_resume.score(X_train_r, y_train_r)
test_acc = model_resume.score(X_test_r, y_test_r)

print(f"Train Accuracy: {train_acc:.2%}")
print(f"Test Accuracy: {test_acc:.2%}")
