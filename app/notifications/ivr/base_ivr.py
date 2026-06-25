class BaseIVRProvider:

    def make_call(self, phone, alert):
        raise NotImplementedError