from app.notifications.sms.base_sms import BaseSMSProvider


class OrangeSMSProvider(BaseSMSProvider):

    def send_sms(self, phone, message):

        # Future Orange API integration

        print(
            f"[ORANGE SMS] Sending SMS to {phone}"
        )

        return True


sms_provider = OrangeSMSProvider()