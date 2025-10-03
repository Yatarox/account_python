import requests

url = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/eur.json"
r = requests.get(url, timeout=10)
r.raise_for_status()
data = r.json()

# Exemple : taux EUR → USD
taux_eur_usd = data["eur"]["usd"]
print(f"Taux EUR → USD : {taux_eur_usd}")

# Convertir 100 EUR en USD
montant = 100 * taux_eur_usd
print(f"100 EUR = {montant:.2f} USD")
