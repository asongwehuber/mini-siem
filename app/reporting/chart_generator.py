import matplotlib.pyplot as plt

SEVERITY_COLORS = {
    "Critical": "#ff4d4d",
    "High": "#ff9933",
    "Medium": "#ffd11a",
    "Low": "#33cc33"
}


def generate_severity_chart(data, output_file):

    labels = [
        "Critical",
        "High",
        "Medium",
        "Low"
    ]

    values = [
        data.get("critical_alerts", 0),
        data.get("high_alerts", 0),
        data.get("medium_alerts", 0),
        data.get("low_alerts", 0)
    ]


    # Handle days with no alerts
    if sum(values) == 0:

        labels = ["No Alerts"]
        values = [1]


    colors = [
        SEVERITY_COLORS.get(label, "#999999")
        for label in labels
    ]


    plt.figure(figsize=(6, 4))


    plt.pie(
        values,
        labels=labels,
        colors=colors,
        autopct="%1.1f%%"
    )


    plt.title(
        "Alert Severity Distribution"
    )


    plt.savefig(
        output_file,
        bbox_inches="tight"
    )


    plt.close()