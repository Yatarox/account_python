import random
import requests
import json 
import hashlib
from datetime import datetime
from PIL import Image
from PIL import ImageDraw

class Account:
    VALID_CURRENCIES = {"usd", "eur", "jpy", "gbp"}
    LIVRET_TAUX = 0.03
    LIVRET_PLAFOND = 22950

    def __init__(self, password=None, account_number=None, role="User", name=None, balance=None, livret=None, balance_livret=None, livret_last_update=None):
        self.__name = name
        self.__account_number = account_number
        self.__balance = balance
        self.__livret = livret
        self.__livret_last_update = livret_last_update
        self.__password = password
        self.__role = role
        self.__balance_livret = balance_livret

    def update(self):
        with open('account.json', 'r', encoding="utf-8") as f:

            data_exist = json.load(f)

            if self.__livret == True:
                self.__livret_last_update = datetime.today().strftime('%Y-%m-%d')
            else:
                self.__livret_last_update = None

            new_data = {"Name": self.__name, "Balance": int(self.__balance), "Password": self.__password,  "Role": self.__role, "Livret": self.__livret, "Balance_livret": int(self.__balance_livret), "Livret_last_update": self.__livret_last_update}

            if isinstance(data_exist, list):
                data_exist.append(new_data)
            else:
                data_exist[self.__account_number] = new_data

            f.close()

            with open('account.json', 'w+', encoding="utf-8") as file:
                json.dump(data_exist, file, indent=4, ensure_ascii=False)

                file.close()
        
        print("Le compte de l'utilisateur a été mis a jour avec succès")
    
    def authentificate(self):
        with open("account.json", 'r', encoding="utf-8") as file:
            data = json.load(file)

            if isinstance(data, dict):
                for account_number, account_data in data.items():
                    if account_data["Name"] == self.__name and account_data["Password"] == self.__password:
                        current_user = {account_number: account_data}
                        print(current_user)
                        return True, current_user
    
    def create(self):
        with open('account.json', 'r', encoding="utf-8") as f:

            data_exist = json.load(f)

            if self.__livret_last_update == None:
                self.__livret_last_update = datetime.today().strftime('%Y-%m-%d')

            self.__account_number = self.generate_account_number()
            if self.__livret == 1:
                self.__livret = True
            else:
                self.__livret = False
                self.__balance_livret = None
            new_data = {"Name": self.__name, "Balance": int(self.__balance), "Password": self.__password,  "Role": self.__role, "Livret": self.__livret, "Balance_livret": int(self.__balance_livret), "Livret_last_update": self.__livret_last_update}

            if isinstance(data_exist, list):
                data_exist.append(new_data)
            else:
                data_exist[self.__account_number] = new_data

            f.close()

            with open('account.json', 'w+', encoding="utf-8") as file:
                json.dump(data_exist, file, indent=4, ensure_ascii=False)

                file.close()
        
        print("L'utilisateur à été enregistré avec succès")

    #Check valide input
    def __validate_currency(self, currency):
        if currency not in self.VALID_CURRENCIES:
            raise ValueError("Devise non autorisée")

    def __validate_amount(self, amount):
        try: 
            if amount <= 0:
                raise ValueError("Montant doit être positif")
        except TypeError:
            return "Le montant ne peut pas être vide"
    
    #Basic feature
    def withdraw(self, amount, currency="eur"):
        self.__validate_currency(currency)
        self.__validate_amount(amount)

        if self.__balance >= amount:
            retire = self.convert("eur", currency, amount)
            self.__balance -= amount
            return self.__balance
        else:
            return "Vous n'avez pas les fonds nécessaires"

    def deposit(self, amount, currency="eur"):
        self.__validate_currency(currency)
        self.__validate_amount(amount)
        try:
            if amount < 0:
                return "Le montant ne peut pas être inférieur à 0"
            elif amount == 0:
                return "Le montant doit être au minimum de 1"
            else:
                add= self.convert(currency, "eur", amount)
                self.__balance += add
                return self.__balance
        except:
            return "Le montant ne peut pas être vide"

    def dump(self):
        print(f"Utilisateur: {self.__name} | N° de compte: {self.__account_number} | Balance : {self.__balance}")
        print(f"   Livret EUR: {self.__livret:.2f} (dernière maj : {self.__livret_last_update})")
    
    #Livret feature 
    def deposit_livret(self,amount):
        self.__validate_amount(amount)

        if self.__balance < amount:
            print("Fonds insuffisants.")
            return

        self.apply_interest()

        if self.__livret + amount > self.LIVRET_PLAFOND:
            print("Dépassement du plafond du livret.")
            return

        self.__livret += amount
        self.__livret_last_update = datetime.today().strftime('%Y-%m-%d')
        print(f"{amount} EUR déposés sur le livret. Nouveau solde livret : {self.__livret:.2f} EUR")

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
        return converted_amount
    

    #save data on json
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
            "Livret_last_update": self.__livret_last_update
        }

        json_str = json.dumps(data, sort_keys=True)
        hash_val = hashlib.sha256(json_str.encode()).hexdigest()
        data["_hash"] = hash_val

        with open('account.json', 'w') as file:
            json.dump(data, file, indent=4)

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
            # elif response == 7:
            #     self.apply_interest()
            #     self.dump_data()
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
        return Account(name, account_number, balance, 0, livret_last_update)

    def generate_card(self):
        image = Image.open("./assets/base.jpg")

        watermark_image = image.copy()

        draw = ImageDraw.Draw(watermark_image)

        draw.text((75, 100), self.__account_number, (255, 255, 255))

        #watermark_image.show()
        path_card = f"./cards/{self.__account_number}.png"
        watermark_image.save(path_card)
        return path_card
        