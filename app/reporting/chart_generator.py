import matplotlib.pyplot as plt


def generate_severity_chart(data, output_file):

    labels = ["Critical", "High", "Medium", "Low"]

    values = [
        data.get("critical_alerts", 0),
        data.get("high_alerts", 0),
        data.get("medium_alerts", 0),
        data.get("low_alerts", 0)
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