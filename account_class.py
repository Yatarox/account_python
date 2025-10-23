import random
import requests
import json 
import hashlib
from datetime import datetime
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

class Account:
    VALID_CURRENCIES = {"usd", "eur", "jpy", "gbp"}
    LIVRET_TAUX = 0.03
    LIVRET_PLAFOND = 22950

    def __init__(self, name, account_number, balance, livret, livret_last_update, transaction_history=None):
        self.__name = name
        self.__account_number = account_number
        self.__balance = balance
        self.__livret = livret
        self.__livret_last_update = livret_last_update
        self.__transaction_history = transaction_history if transaction_history is not None else []
    
    def __validate_currency(self, currency):
        if currency not in self.VALID_CURRENCIES:
            raise ValueError("Devise non autorisée")

    def __validate_amount(self, amount):
        if amount <= 0:
            raise ValueError("Montant doit être positif")
    
    def __add_transaction(self, transaction_type, currency, amount, details=""):
        """
        Ajoute une transaction à l'historique
        transaction_type: type d'opération (ex: "Dépôt", "Retrait", "Conversion")
        currency: devise concernée
        amount: montant de l'opération
        details: informations supplémentaires (optionnel)
        """
        from datetime import datetime
        transaction = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Date et heure actuelles
            "type": transaction_type,                              # Type d'opération
            "currency": currency.upper(),                         # Devise en majuscules
            "amount": amount,                                     # Montant
            "details": details                                    # Détails supplémentaires
        }
        self.__transaction_history.append(transaction)           # Ajoute à la liste
        
        if len(self.__transaction_history) > 10:
            self.__transaction_history = self.__transaction_history[-10:]
    #Basic feature
    def withdraw(self, currency, amount):
        self.__validate_currency(currency)
        self.__validate_amount(amount)

        if self.__balance.get(currency, 0) >= amount:
            self.__balance[currency] -= amount
            self.__add_transaction("Retrait", currency, amount, f"Solde restant: {self.__balance[currency]:.2f}")
            print(f"Nouveau solde en {currency.upper()}: {self.__balance[currency]:.2f}")
        else:
            print("Fonds insuffisants.")

    def deposit(self, currency, amount):
        self.__validate_currency(currency)
        self.__validate_amount(amount)

        self.__balance[currency] = self.__balance.get(currency, 0) + amount
        self.__add_transaction("Dépôt", currency, amount, f"Nouveau solde: {self.__balance[currency]:.2f}")
        print(f"Nouveau solde en {currency.upper()}: {self.__balance[currency]:.2f}")

    def dump(self):
        print(f"Utilisateur: {self.__name} | N° de compte: {self.__account_number}")
        for cur, val in self.__balance.items():
            print(f"   {cur.upper()}: {val:.2f}")
        print(f"   Livret EUR: {self.__livret:.2f} (dernière maj : {self.__livret_last_update})")
    
    def show_transaction_history(self):
        """Affiche les 10 dernières transactions"""
        if not self.__transaction_history:
            print("Aucune transaction enregistrée.")
            return
        
        print("\n=== Historique des transactions ===")
        print(f"Affichage des {len(self.__transaction_history)} dernières opérations :\n")
        
        for i, transaction in enumerate(reversed(self.__transaction_history), 1):
            print(f"{i}. {transaction['date']} - {transaction['type']}")
            print(f"   {transaction['amount']:.2f} {transaction['currency']}")
            if transaction['details']:
                print(f"   {transaction['details']}")
            print()  # Ligne vide pour la lisibilité
    
    #Livret feature 
    def deposit_livret(self, currency, amount):
        self.__validate_currency(currency)
        self.__validate_amount(amount)

        if self.__balance.get(currency, 0) < amount:
            print("Fonds insuffisants.")
            return

        self.apply_interest()

        if currency != "eur":
            print(f"Conversion de {currency.upper()} en EUR pour le livret...")
            before_eur = self.__balance.get("eur", 0)
            self.convert(currency, "eur", amount)
            amount_to_livret = self.__balance.get("eur", 0) - before_eur
        else:
            self.__balance["eur"] -= amount
            amount_to_livret = amount

        if self.__livret + amount_to_livret > self.LIVRET_PLAFOND:
            print("Dépassement du plafond du livret.")
            return

        self.__livret += amount_to_livret
        self.__livret_last_update = datetime.today().strftime('%Y-%m-%d')
        self.__add_transaction("Dépôt livret", "eur", amount_to_livret, f"Nouveau solde livret: {self.__livret:.2f}")
        print(f"{amount_to_livret:.2f} EUR déposés sur le livret. Nouveau solde livret : {self.__livret:.2f} EUR")

    def calculate_interest(self):
        last_update = datetime.strptime(self.__livret_last_update, "%Y-%m-%d")
        today = datetime.today()
        if today <= last_update:
            return 0.0
        days = (today - last_update).days
        interest = self.__livret * self.LIVRET_TAUX * (days / 365)
        return interest

    def apply_interest(self):
        interest = self.calculate_interest()
        last_update = datetime.strptime(self.__livret_last_update, "%Y-%m-%d")
        today = datetime.today()
        if (today - last_update).days >= 365:
            if interest > 0:
                self.__livret += interest
                self.__livret_last_update = today.strftime('%Y-%m-%d')
                print(f"Intérêts appliqués : {interest:.2f} EUR | Nouveau solde livret : {self.__livret:.2f} EUR")

    def withdraw_livret(self, amount):
        self.__validate_amount(amount)
        self.apply_interest()

        if amount > self.__livret:
            print(f"Fonds insuffisants dans le livret. Solde actuel : {self.__livret:.2f} EUR")
            return

        self.__livret -= amount
        self.__balance["eur"] = self.__balance.get("eur", 0) + amount
        self.__livret_last_update = datetime.today().strftime('%Y-%m-%d')
        
        self.__add_transaction("Retrait livret", "eur", amount, f"Solde livret: {self.__livret:.2f}")

        print(f"Vous avez retiré {amount:.2f} EUR du livret et il a été ajouté au compte courant.")
        print(f"Nouveau solde livret : {self.__livret:.2f} EUR")
        print(f"Nouveau solde compte courant EUR : {self.__balance['eur']:.2f} EUR")

    #convert feature
    def convert(self, from_currency, to_currency, amount):
        self.__validate_currency(from_currency)
        self.__validate_currency(to_currency)
        self.__validate_amount(amount)

        url = f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/{from_currency}.json"
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            print(f"Erreur API : {e}")
            return

        rates = data.get(from_currency, {})
        if to_currency not in rates:
            print(f"Taux introuvable pour {from_currency.upper()} → {to_currency.upper()}")
            return

        rate = rates[to_currency]
        converted_amount = amount * rate
        self.__balance[from_currency] -= amount
        self.__balance[to_currency] = self.__balance.get(to_currency, 0) + converted_amount

        self.__add_transaction("Conversion", from_currency, amount, f"→ {to_currency.upper()}: {converted_amount:.2f}")

        print(f"{amount} {from_currency.upper()} = {converted_amount:.2f} {to_currency.upper()}")
        print(f"Nouveau solde : {self.__balance}")
    


    def dump_data(self):
        try:
            with open('account.json', 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {}

        data.pop("_hash", None)

        data[self.__account_number] = {
            "Name": self.__name,
            "Balance": self.__balance,
            "Livret": self.__livret,
            "Livret_last_update": self.__livret_last_update,
            "Transaction_history": self.__transaction_history
        }

        json_str = json.dumps(data, sort_keys=True)
        hash_val = hashlib.sha256(json_str.encode()).hexdigest()
        data["_hash"] = hash_val

        with open('account.json', 'w') as file:
            json.dump(data, file, indent=4)

    def print_receipt(self, op_type: str, currency: str, amount: float):
        """Crée/affiche un mini reçu de l'opération et l'enregistre dans last_receipt.txt"""
        now = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        # solde current pour la devise (0 si inexistante)
        cur_balance = self.__balance.get(currency, 0.0)
        lines = [
            f"--- Reçu bancaire ---",
            f"Date : {now}",
            f"Opération : {op_type}",
            f"Montant : {amount:.2f} {currency.upper()}",
            f"Solde après opération ({currency.upper()}) : {cur_balance:.2f}",
            f"Livret (EUR) : {self.__livret:.2f}",
            "---------------------\n"
        ]
        receipt = "\n".join(lines)
        print(receipt)  # affiche dans la console

        try:
            with open("last_receipt.txt", "w", encoding="utf-8") as f:
                f.write(receipt)
        except Exception as e:
            print(f"Erreur écriture reçu : {e}")


    #process user
    def process(self):
        while True:
            print("""
            === Menu principal ===
            1 : Voir vos informations
            2 : Déposer de l'argent
            3 : Retirer de l'argent
            4 : Convertir de l'argent
            5 : Déposer sur livret
            6 : Retirer du livret
            7 : Historique des transactions
            8 : Quitter
            """)
            try:
                response = int(input("Choix : "))
            except ValueError:
                print("Entrée invalide.")
                continue

            if response == 1:
                self.dump()
            elif response == 2:
                currency = self.choose_currency()
                try:
                    amount = float(input(f"Montant à déposer en {currency.upper()} : "))
                    self.deposit(currency, amount)
                    self.print_receipt("Dépôt", currency, amount)  
                    self.dump_data()  
                except ValueError as e:
                    print(f"Erreur : {e}")

            elif response == 3:
                currency = self.choose_currency()
                try:
                    amount = float(input(f"Montant à retirer en {currency.upper()} : "))
                    self.withdraw(currency, amount)
                    self.dump_data()
                except ValueError as e:
                    print(f"Erreur : {e}")
            elif response == 4:
                print("Source devise")
                currency = self.choose_currency()
                print("Convertir pour la devise")
                futur_currency = self.choose_currency()
                try:
                    amount = float(input(f"Combien de {currency.upper()} voulez-vous convertir : "))
                    self.convert(currency, futur_currency, amount)
                    self.dump_data()
                except ValueError as e:
                    print(f"Erreur : {e}")
            elif response == 5:
                currency = self.choose_currency()
                try:
                    amount = float(input(f"Montant à déposer sur le livret (en {currency.upper()}) : "))
                    self.deposit_livret(currency, amount)
                    self.dump_data()
                except ValueError as e:
                    print(f"Erreur : {e}")
            elif response == 6:
                try:
                    amount = float(input("Montant à retirer du livret (EUR) : "))
                    self.withdraw_livret(amount)
                    self.dump_data()
                except ValueError as e:
                    print(f"Erreur : {e}")
            elif response == 7:
                self.show_transaction_history()
            elif response == 8:
                self.dump_data()
                print(f"Pour votre prochaine connection utiliser votre numero de compte {self.__account_number}")
                print("Au revoir.")
                break
            else:
                print("Option invalide.")

    #def only use for the account 
    @staticmethod
    def generate_account_number():
        return "".join(str(random.randint(0, 9)) for _ in range(10))

    @staticmethod
    def choose_currency():
        options = {1: "usd", 2: "eur", 3: "jpy", 4: "gbp"}
        print("""
        Choisissez une devise :
        1 : USD
        2 : EUR
        3 : JPY
        4 : GBP
        """)
        while True:
            try:
                response = int(input("Réponse : "))
                if response in options:
                    return options[response]
                else:
                    print("Choix invalide.")
            except ValueError:
                print("Entrée invalide. Donnez un chiffre.")

    @staticmethod
    def create_account():
        balance = {"usd": 0, "eur": 0, "jpy": 0, "gbp": 0}
        name = input("Nom du propriétaire du compte : ")
        livret_last_update = datetime.today().strftime('%Y-%m-%d')
        while True:
            currency = Account.choose_currency()
            try:
                amount = float(input(f"Montant à déposer en {currency.upper()} (0 pour ignorer): "))
                if amount < 0:
                    print("Pas de valeur négative.")
                else:
                    balance[currency] += amount
            except ValueError:
                print("Veuillez entrer un nombre valide.")

            cont = input("Ajouter une autre devise ? (o/n): ").lower()
            if cont != "o":
                break
        account_number = Account.generate_account_number()
        return Account(name, account_number, balance, 0, livret_last_update, [])
    
    @staticmethod
    def load_account():
        numero_de_compte = input("Numéro de compte du propriétaire du compte : ")

        try:
            with open('account.json', 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            print("Aucun fichier de compte trouvé.")
            return None

        saved_hash = data.pop("_hash", None)
        if not saved_hash:
            print("Fichier invalide : aucun hash")
            return None

        recalculated_hash = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
        if saved_hash != recalculated_hash:
            print("⚠️ Le fichier a été modifié !")
            return None
        
        for account_number, account_data in data.items():
            if account_number == numero_de_compte:
                balance = account_data["Balance"]
                livret = account_data["Livret"]
                livret_last_update = account_data["Livret_last_update"]
                name = account_data["Name"]
                transaction_history = account_data.get("Transaction_history", [])
                print(f"Bienvenue {account_data["Name"]} !")
                return Account(name, account_number, balance, livret, livret_last_update, transaction_history)

        print("Compte introuvable")
        return None



# class Card(Account):
#     def __init__(self, __account_number):
#         super().__init__(__account_number)
#         self.img = ""

    
#     def create_card(self):
#         image = Image.open("./assets/base.jpg")
#         watermark_image = image.copy()
#         draw = ImageDraw.Draw(watermark_image)
#         draw.text((0, 0), "GeeksforGeeks", (255, 255, 255))
#         pass
