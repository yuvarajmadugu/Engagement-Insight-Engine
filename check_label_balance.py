# checks the percentage or no.of members whos should_nudge_resume and who shouldn't
import pandas as pd

# Load the processed dataset
df = pd.read_csv("processed_fomo_dataset.csv")

# Display raw value counts
print("🔍 Label Distribution (Raw Counts):")
print(df['should_nudge_resume'].value_counts())

# Display normalized percentages
print("\n📊 Label Distribution (Percentage):")
print(df['should_nudge_resume'].value_counts(normalize=True) * 100)

# Optional: Visual inspection(optional)
try:
    import matplotlib.pyplot as plt

    df['should_nudge_resume'].value_counts().plot(kind='bar', title='Label Balance', xlabel='Should Nudge Resume', ylabel='Count')
    plt.xticks(ticks=[0, 1], labels=["No", "Yes"], rotation=0)
    plt.tight_layout()
    plt.show()
except ImportError:
    print("\n📌 matplotlib not installed. Run 'pip install matplotlib' to view bar chart.")
