from app.notifications.sms.base_sms import BaseSMSProvider


class SimulatedSMSProvider(BaseSMSProvider):

    def send_sms(self, phone, message):

        print("\n========== SMS ALERT ==========")
        print(f"TO: {phone}")
        print(message)
        print("===============================\n")

        return True


sms_provider = SimulatedSMSProvider()