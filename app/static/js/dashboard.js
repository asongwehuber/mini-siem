// =========================================
// AUDIO SYSTEM (FIXED + STABLE)
// =========================================

let alarmMuted = false;
let lastTriggeredAlertId = null;
let alarmUnlocked = false;
let alarmInstance = null;

// Get audio element safely
function getAlarm() {
    if (!alarmInstance) {
        alarmInstance = document.getElementById("alert-sound");
    }
    return alarmInstance;
}

// Unlock audio (browser autoplay policy fix)
document.addEventListener("click", () => {

    const alarm = getAlarm();

    if (alarm && !alarmUnlocked) {

        alarm.play()
            .then(() => {
                alarm.pause();
                alarm.currentTime = 0;
                alarmUnlocked = true;
                console.log("Audio unlocked");
            })
            .catch(err => console.log("Unlock failed:", err));
    }
});

// Start alarm (safe, no spam)
function startAlarm(alertId) {

    if (alarmMuted) return;

    const alarm = getAlarm();
    if (!alarm) return;

    if (lastTriggeredAlertId === alertId) return;

    lastTriggeredAlertId = alertId;
    alarm.currentTime = 0;

    const playPromise = alarm.play();

    if (playPromise !== undefined) {
        playPromise.catch(err => {
            console.log("Audio blocked:", err);
        });
    }
}

// Stop alarm
function stopAlarm() {

    const alarm = getAlarm();
    if (!alarm) return;

    alarm.pause();
    alarm.currentTime = 0;

    lastTriggeredAlertId = null;
}

// Stop all alarm effects
function stopAllAlarmEffects() {

    const alarm = getAlarm();

    if (alarm) {
        alarm.pause();
        alarm.currentTime = 0;
    }

    lastTriggeredAlertId = null;
    alarmMuted = false;
}

// =========================================
// HANDLE ALARM LOGIC (FIXED CORE)
// =========================================
function handleAlarmSystem(alerts) {

    const openCritical = alerts.filter(alert =>
        alert.status &&
        alert.status.toLowerCase() === 'open' &&
        alert.severity &&
        alert.severity.toLowerCase() === 'critical'
    );

    if (openCritical.length > 0) {
        startAlarm(openCritical[0].id);
    } else {
        stopAlarm();
    }
}

// =========================================
// LOAD DASHBOARD
// =========================================
async function loadDashboard() {

    try {

        const logsResponse = await fetch('/logs');
        const logs = await logsResponse.json();

        const alertsResponse = await fetch('/alerts');
        const alerts = await alertsResponse.json();

        const attackersResponse = await fetch('/top-attackers');
        const attackers = await attackersResponse.json();

        // =========================================
        // COUNTERS
        // =========================================
        document.getElementById('total-logs').innerText = logs.length;
        document.getElementById('total-alerts').innerText = alerts.length;

        const criticalAlerts = alerts.filter(alert =>
            alert.severity &&
            alert.severity.toLowerCase() === 'critical' &&
            alert.status &&
            alert.status.toLowerCase() === 'open'
        ).length;

        document.getElementById('critical-alerts').innerText = criticalAlerts;

        // =========================================
        // LOG TABLE
        // =========================================
        const logsTable = document.getElementById('logs-table');
        logsTable.innerHTML = '';

        logs.slice(0, 10).forEach(log => {
            logsTable.innerHTML += `
                <tr>
                    <td>${log.id}</td>
                    <td>${log.source_ip}</td>
                    <td>${log.event_type}</td>
                    <td>${log.severity}</td>
                    <td>${log.message}</td>
                </tr>
            `;
        });

        // =========================================
        // TOP ATTACKERS
        // =========================================
        const attackersTable = document.getElementById('attackers-table');
        attackersTable.innerHTML = '';

        attackers.forEach(attacker => {
            attackersTable.innerHTML += `
                <tr>
                    <td>${attacker.source_ip}</td>
                    <td>${attacker.count}</td>
                </tr>
            `;
        });

        // =========================================
        // ALERT PANEL
        // =========================================
        const alertsList = document.getElementById('alerts-list');
        const criticalWarning = document.getElementById('critical-warning');

        alertsList.innerHTML = '';

        const openAlerts = alerts.filter(alert =>
            alert.status &&
            alert.status.toLowerCase() === 'open'
        );

        if (openAlerts.length === 0) {

            alertsList.innerHTML = `
                <div class="alert-card alert-low">
                    No active security alerts.
                </div>
            `;

            criticalWarning.classList.add('hidden');

        } else {

            openAlerts.forEach(alert => {

                const div = document.createElement('div');
                div.classList.add('alert-card');

                const severity = (alert.severity || '').toLowerCase();
                div.classList.add(`alert-${severity}`);

                div.innerHTML = `
                    <strong>${alert.severity}</strong>
                    — ${alert.alert_name}

                    <br><br>
                    ${alert.description}
                    <br><br>

                    <small>Source IP: ${alert.source_ip}</small><br>
                    <small>Event Count: ${alert.event_count || 1}</small><br>
                    <small>Status: ${alert.status}</small><br>
                    <small>${alert.timestamp}</small>

                    <br><br>

                    <button onclick="resolveAlert(${alert.id})">
                        Resolve Alert
                    </button>

                    <button onclick="explainAlert(${alert.id})">
                        🧠 Explain with AI
                    </button>
                `;

                alertsList.appendChild(div);
            });

            if (criticalAlerts > 0) {
                criticalWarning.classList.remove('hidden');
            } else {
                criticalWarning.classList.add('hidden');
            }
        }

        // =========================================
        // HANDLE ALARM (ONLY PLACE ALARM IS CONTROLLED)
        // =========================================
        handleAlarmSystem(alerts);

        // =========================================
        // CHART DATA
        // =========================================
        const severityCounts = {
            low: 0,
            medium: 0,
            high: 0,
            critical: 0
        };

        logs.forEach(log => {
            if (!log.severity) return;

            const severity = log.severity.toLowerCase();

            if (severityCounts[severity] !== undefined) {
                severityCounts[severity]++;
            }
        });

        const ctx = document.getElementById('severityChart').getContext('2d');

        if (window.severityChartInstance) {
            window.severityChartInstance.destroy();
        }

        window.severityChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Low', 'Medium', 'High', 'Critical'],
                datasets: [{
                    label: 'Logs by Severity',
                    data: [
                        severityCounts.low,
                        severityCounts.medium,
                        severityCounts.high,
                        severityCounts.critical
                    ],
                    backgroundColor: [
                        '#3498db', // Low = Blue
                        '#f39c12', // Medium = Orange
                        '#e74c3c', // High = Red
                        '#8e0000'  // Critical = Dark Red
                    ],
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true
            }
        });

    } catch (error) {
        console.error('Dashboard Error:', error);
    }
}

// =========================================
// INIT
// =========================================
document.addEventListener("DOMContentLoaded", () => {

    loadDashboard();
    loadQuarantinedHosts();

    setInterval(loadDashboard, 3000);
    setInterval(loadQuarantinedHosts, 3000);

});

// =========================================
// RESOLVE ALERT
// =========================================
async function resolveAlert(alertId) {

    try {
        await fetch(`/resolve-alert/${alertId}`, {
            method: 'POST'
        });

        stopAllAlarmEffects();

        loadDashboard();

    } catch (error) {
        console.error('Resolve alert error:', error);
    }
}

// =========================================
// MUTE BUTTON
// =========================================
function toggleAlarm() {

    const alarm = getAlarm();
    if (!alarm) return;

    alarmMuted = !alarmMuted;

    if (alarmMuted) {
        alarm.pause();
        alarm.currentTime = 0;
    }
}

// =========================================
// QUARANTINE LOADING
// =========================================
async function loadQuarantinedHosts() {

    try {

        const response = await fetch('/quarantined-hosts-summary');

        if (!response.ok) return;

        const data = await response.json();

        const container = document.getElementById('quarantined-hosts');

        if (!container) return;

        container.innerHTML = '';

        const hosts = data.hosts || [];
        const totalHosts = data.total_quarantined || 0;

        if (hosts.length === 0) {

            container.innerHTML =
                "<p>No quarantined hosts.</p>";

            return;
        }

        hosts.forEach(host => {

            const div = document.createElement('div');

            div.className =
                "alert-card alert-high";

            div.innerHTML = `
                <strong>${host.source_ip}</strong><br>
                Hostname: ${host.hostname || 'N/A'}<br>
                Reason: ${host.reason || 'N/A'}<br>
                Status: quarantined<br>
                <small>
                    Quarantined At:
                    ${host.quarantined_at || ''}
                </small>
            `;

            container.appendChild(div);
        });

        // Show remaining hosts count
        if (totalHosts > 3) {

            const moreDiv =
                document.createElement('div');

            moreDiv.style.marginTop = "10px";
            moreDiv.style.fontWeight = "bold";
            moreDiv.style.color = "#f39c12";

            moreDiv.innerHTML =
                `+ ${totalHosts - 3} more quarantined host(s)`;

            container.appendChild(moreDiv);
        }

    } catch (error) {

        console.error(
            "Quarantine load error:",
            error
        );
    }
}

// =========================================
// CHAT SYSTEM for ai
// =========================================

async function sendChat() {

    const input = document.getElementById("chat-input");
    const message = input.value.trim();

    if (!message) return;

    // render USER bubble
    addChatMessage("user", message);

    input.value = "";

    // typing indicator
    showTyping(true);

    try {

        const response = await fetch("/ai/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message })
        });

        const data = await response.json();

        showTyping(false);

        // render AI bubble
        addChatMessage("ai", data.response);

    } catch (error) {

        showTyping(false);

        addChatMessage("ai", "⚠ AI service unavailable.");
    }
}

//New message rendering bubble

function addChatMessage(sender, text) {

    const box = document.getElementById("chat-messages");

    const wrapper = document.createElement("div");
    wrapper.classList.add("message", sender);

    const bubble = document.createElement("div");
    bubble.classList.add("bubble");
    bubble.innerText = text;

    wrapper.appendChild(bubble);
    box.appendChild(wrapper);

    box.scrollTop = box.scrollHeight;
}




//adding typing indicator

function showTyping(show) {

    const typing = document.getElementById("typing-indicator");

    if (!typing) return;

    if (show) {
        typing.classList.remove("hidden");
    } else {
        typing.classList.add("hidden");
    }
}

//enter key support
function handleEnter(event) {
    if (event.key === "Enter") {
        sendChat();
    }
}




// =========================================
// REPORTS CENTER
// =========================================

function downloadDailyReport() {
    window.location.href = "/reports/download";
}

function downloadWeeklyReport() {
    window.location.href = "/report/pdf?type=weekly";
}
function downloadMonthlyReport() {
    window.location.href = "/report/pdf?type=monthly";
}

async function loadReportStats() {

    try {

        const response = await fetch("/report");

        const data = await response.json();

        document.getElementById("report-stats").innerHTML = `
            <p><strong>Total Logs:</strong> ${data.total_logs}</p>
            <p><strong>Total Alerts:</strong> ${data.total_alerts}</p>
            <p><strong>Critical Alerts:</strong> ${data.critical_alerts}</p>
            <p><strong>High Alerts:</strong> ${data.high_alerts}</p>
            <p><strong>Medium Alerts:</strong> ${data.medium_alerts}</p>
            <p><strong>Low Alerts:</strong> ${data.low_alerts}</p>
            <p><strong>Quarantined Hosts:</strong> ${data.quarantined_hosts}</p>
        `;

    } catch (error) {

        console.error("Report stats error:", error);

        document.getElementById("report-stats").innerHTML =
            "Failed to load report statistics.";
    }
}

// Load stats when dashboard opens
loadReportStats();


async function explainAlert(alertId) {

    document.getElementById("aiModal").style.display = "block";

    document.getElementById("aiAnalysis").innerHTML =
        "🧠 Analyzing alert...";

    try {

        const response = await fetch(
            `/ai/alert/${alertId}/explain`
        );

        const data = await response.json();

        document.getElementById("aiAnalysis").innerText =
            data.explanation;

    } catch (error) {

        document.getElementById("aiAnalysis").innerText =
            "Failed to get AI analysis.";

        console.error(error);
    }
}


function closeModal() {
    document.getElementById("aiModal").style.display = "none";
}


