# app/notifications/sms/base_sms.py

class BaseSMSProvider:
    def send_sms(self, phone_number: str, message: str):
        raise NotImplementedError