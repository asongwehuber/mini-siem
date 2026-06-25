from app.notifications.ivr.base_ivr import BaseIVRProvider


class SimulatedIVRProvider(BaseIVRProvider):

    def make_call(self, phone, alert):

        print("\n========== IVR CALL ==========")
        print(f"CALLING: {phone}")

        print(
            f"""
Critical Security Alert

Alert:
{alert.alert_name}

Source IP:
{alert.source_ip}

Severity:
{alert.severity.upper()}

Options:
Press 1 - Acknowledge Alert
Press 2 - Quarantine Host
Press 3 - Repeat Message
"""
        )

        print("==============================")

        return True


ivr_provider = SimulatedIVRProvider()