import matplotlib.pyplot as plt

SEVERITY_COLORS = {
    "Critical": "#ff4d4d",
    "High": "#ff9933",
    "Medium": "#ffd11a",
    "Low": "#33cc33"
}

def generate_severity_chart(data, output_file):

    labels = ["Critical", "High", "Medium", "Low"]

    values = [
        data.get("critical_alerts", 0),
        data.get("high_alerts", 0),
        data.get("medium_alerts", 0),
        data.get("low_alerts", 0)
    ]
    colors = [
        SEVERITY_COLORS["Critical"],
        SEVERITY_COLORS["High"],
        SEVERITY_COLORS["Medium"],
        SEVERITY_COLORS["Low"]
    ]

    plt.figure(figsize=(6, 4))

    plt.pie(
        values,
        labels=labels,
        autopct="%1.1f%%"
    )

    plt.title("Alert Severity Distribution")

    plt.savefig(output_file)

    plt.close()
