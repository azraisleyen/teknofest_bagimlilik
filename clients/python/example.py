# Supply credentials from a secret manager, never source code.
from sentra_qr_client import SentraQrClient

client = SentraQrClient("https://sentra.example.invalid", credential="EXTERNAL_SECRET")
print(client.health_check().data)
