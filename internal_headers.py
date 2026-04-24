from config import config

def getHeaders():
    headers = {
        "Authorization": f"Bearer {config.FIN_AGENT_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "Intercom-Version": config.INTERCOM_VERSION
    }

    return headers