import customtkinter as ctk
from PIL import Image
from account_class import Account
import hashlib

PRIMARY_COLOR = "#1E3A8A"
SECONDARY_COLOR = "#3B82F6"
BACKGROUND_COLOR = "#111827"
TEXT_COLOR = "white"
PLACEHOLDER_COLOR = "#9CA3AF"

class Header(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=BACKGROUND_COLOR)

        self.configure(width=600, height=80)

        self.ctkImage = ctk.CTkImage(Image.open("assets/bank.png"), size=(60, 60))
        self.image_label = ctk.CTkLabel(self, image=self.ctkImage, text="", fg_color="transparent")
        self.image_label.grid(row=0, column=0, padx=(20, 50))

        self.title = ctk.CTkLabel(self, text="BPE - Banque de proximité de l'EPSI", fg_color="transparent", text_color=TEXT_COLOR, font=('Arial Bold', 22))
        self.title.grid(row=0, column=1, sticky="w", padx=10)

class BaseBody(ctk.CTkFrame):
    def __init__(self, master, switch_body):
        super().__init__(master, fg_color=BACKGROUND_COLOR)

        self.switch_body = switch_body

        self.login = ctk.CTkEntry(self, placeholder_text="Nom d'utilisateur", width=300, height=40, justify='center', text_color=TEXT_COLOR)
        self.login.pack(pady=(120, 15))

        self.password = ctk.CTkEntry(self, placeholder_text="Mot de passe", width=300, height=40, justify='center', show="*", text_color=TEXT_COLOR)
        self.password.pack(pady=(0, 30))

        self.validate = ctk.CTkButton(self, text='Se connecter', width=300, height=40, fg_color=PRIMARY_COLOR, hover_color=SECONDARY_COLOR, text_color=TEXT_COLOR, command=self.connection)
        self.validate.pack(pady=(0, 200))

    def connection(self):
        username = self.login.get()
        clear_pwd = self.password.get()
        clear_pwd = clear_pwd.encode('utf-8')
        hashed_password = hashlib.sha256(clear_pwd)
        pwd = hashed_password.hexdigest()
        print(hashed_password)

        account = Account(name=username, password=pwd)
        account_auth, current_user = account.authentificate()

        number_account_current_user = next(iter(current_user))

        if account_auth and current_user[number_account_current_user]["Role"] == "Admin":
            self.switch_body("AdminBody")
        elif account_auth and current_user[number_account_current_user]["Role"] == "User":
            self.switch_body("UserBody", current_user)

            # Voir pour créer une var current_user et la passer à switch_body
            # puis de switch_body à l'instance de body en cours pour pouvoir garder l'user connecté en cache

class UserBody(ctk.CTkFrame):
    def __init__(self, master, switch_body, current_user):
        super().__init__(master, fg_color=BACKGROUND_COLOR)

        self.switch_body = switch_body
        #self.current_id = current_id
        self.current_user = current_user

        self.name = ctk.CTkLabel(self, text="Bienvenu dans votre espace client", font=('Arial', 20), width=250, height=40, justify='center', text_color=TEXT_COLOR)
        self.name.grid(row=0, column=0, columnspan=2, padx=20, pady=(40, 40), sticky="ew")

        self.dump = ctk.CTkButton(self, text="Afficher les informations du compte", width=250, height=40, fg_color=PRIMARY_COLOR, hover_color=SECONDARY_COLOR, text_color=TEXT_COLOR)
        self.dump.grid(row=1, column=0, pady=(20, 0))

        self.withdraw = ctk.CTkButton(self, text="Retirer de l'argent", width=250, height=40, fg_color=PRIMARY_COLOR, hover_color=SECONDARY_COLOR, text_color=TEXT_COLOR)
        self.withdraw.grid(row=1, column=1, pady=(20, 0))

        self.deposit = ctk.CTkButton(self, text="Déposer de l'argent", width=250, height=40, fg_color=PRIMARY_COLOR, hover_color=SECONDARY_COLOR, text_color=TEXT_COLOR)
        self.deposit.grid(row=2, column=0, pady=(20, 0))

        self.send_money = ctk.CTkButton(self, text="Effectuer un virement", width=250, height=40, fg_color=PRIMARY_COLOR, hover_color=SECONDARY_COLOR, text_color=TEXT_COLOR)
        self.send_money.grid(row=2, column=1, pady=(20, 0))

        self.create_card = ctk.CTkButton(self, text="Créer ma carte bancaire", width=250, height=40, fg_color=PRIMARY_COLOR, hover_color=SECONDARY_COLOR, text_color=TEXT_COLOR, command=self.call_generate_card)
        self.create_card.grid(row=3, column=0, pady=(20, 0))

        self.close_livret = ctk.CTkButton(self, text="Clôturer le livret A", width=250, height=40, fg_color=PRIMARY_COLOR, hover_color=SECONDARY_COLOR, text_color=TEXT_COLOR)
        self.close_livret.grid(row=3, column=1, pady=(20, 0))

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
    
    """def call_dump(self):
        account = Account(self.current_id)
        if account: 
            pass"""

    def call_generate_card(self):
        account_number=next(iter(self.current_user))
        account = Account(account_number=account_number, 
                          password=self.current_user[account_number]["Password"],
                          role=self.current_user[account_number]["Role"],
                          name=self.current_user[account_number]["Name"],
                          balance=self.current_user[account_number]["Balance"],
                          livret=self.current_user[account_number]["Livret"],
                          balance_livret=self.current_user[account_number]["Balance_livret"],
                          livret_last_update=self.current_user[account_number]["Livret_last_update"])
        print(account)
        path_card = account.generate_card()
        print(path_card)
        
        # Envoyer le current user dans la fonction generate_card, puis afficher sa carte grâce à son account_number stocké dans le cache

class AdminBody(ctk.CTkFrame):
    def __init__(self, master, switch_body):
        super().__init__(master, fg_color=BACKGROUND_COLOR)

        self.switch_body = switch_body
        self.epargne_var = ctk.IntVar(value=0)

        self.name = ctk.CTkEntry(self, placeholder_text="Prénom de l'utilisateur", width=250, height=40, justify='center', text_color=TEXT_COLOR)
        self.name.grid(row=0, column=0, padx=20, pady=(40, 15), sticky="ew")

        self.password = ctk.CTkEntry(self, placeholder_text="Mot de passe de l'utilisateur", show="*", width=250, height=40, justify='center', text_color=TEXT_COLOR)
        self.password.grid(row=1, column=0, padx=20, pady=15, sticky="ew")

        self.balance = ctk.CTkEntry(self, placeholder_text="Montant en €", width=250, height=40, justify='center', text_color=TEXT_COLOR)
        self.balance.grid(row=1, column=1, padx=20, pady=15, sticky="ew")

        self.options = ["User", "Admin"]
        self.role = ctk.CTkOptionMenu(self, values=self.options, width=250, height=40, fg_color=PRIMARY_COLOR, button_color=SECONDARY_COLOR, text_color=TEXT_COLOR)
        self.role.set("-- Sélectionnez un rôle --")
        self.role.grid(row=2, column=0, padx=20, pady=15, sticky="ew")

        self.epargne = ctk.CTkCheckBox(self, text="Ouvrir un livret A", variable=self.epargne_var, width=250, height=40, text_color=TEXT_COLOR, fg_color=PRIMARY_COLOR, hover_color=SECONDARY_COLOR)
        self.epargne.grid(row=2, column=1, padx=20, pady=15, sticky="w")

        self.balance_epargne = ctk.CTkEntry(self, placeholder_text="Montant épargne initial", width=250, height=40, justify='center', text_color=TEXT_COLOR)
        self.balance_epargne.grid(row=3, column=0, columnspan=2, padx=20, pady=(15, 30), sticky="ew")

        self.validate = ctk.CTkButton(self, text="Valider l'inscription", width=250, height=40, fg_color=PRIMARY_COLOR, hover_color=SECONDARY_COLOR, text_color=TEXT_COLOR, command=self.validate_user)
        self.validate.grid(row=4, column=0, columnspan=2, pady=(0, 20))

        self.logout_btn = ctk.CTkButton(self, text="Se déconnecter", width=250, height=40, fg_color="#DC2626", hover_color="#EF4444", text_color=TEXT_COLOR, command=self.logout)
        self.logout_btn.grid(row=5, column=0, columnspan=2, pady=(0, 20))

    def validate_user(self):
        name = self.name.get()
        clear_password = self.password.get()
        clear_password = clear_password.encode("utf-8")
        hashed_password = hashlib.sha256(clear_password)
        password = hashed_password.hexdigest()
        balance = self.balance.get()
        role = self.role.get()
        epargne = self.epargne_var.get()
        print(f"La valeur de la checkbox est : {epargne}")

        self.name.delete(0, "end")
        self.password.delete(0, "end")
        self.balance.delete(0, "end")
        self.role.set("-- Sélectionnez un rôle --")
        self.epargne_var.set(0)

        if epargne == 1:
            balance_epargne = self.balance_epargne.get()
            self.balance_epargne.delete(0, "end")
            account = Account(password=password, name=name, balance=balance, role=role, livret=epargne, balance_livret=balance_epargne)
            account.create()
        else:
            account = Account(password=password, name=name, balance=balance, role=role)
            account.create()

    def logout(self):
        self.switch_body("BaseBody")


class Footer(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=BACKGROUND_COLOR)

        self.separator = ctk.CTkFrame(self, height=2, fg_color=PLACEHOLDER_COLOR)
        self.separator.pack(fill="x", side="top", pady=(0))

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="x", pady=(5, 5))

        self.credits = ctk.CTkLabel(container, text="© BPE - Banque de Proximité de l'EPSI", font=('Calibri Light', 10), text_color=PLACEHOLDER_COLOR, fg_color='transparent')
        self.credits.pack(side="left", padx=(20, 0))

        self.links = ctk.CTkLabel(container, text="CGU   |   Contact   |   Aide", font=('Calibri Light', 12), text_color=PLACEHOLDER_COLOR, fg_color='transparent')
        self.links.pack(side="right", padx=(0, 20))

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry('600x600')
        self.maxsize(600, 600)
        self.minsize(600, 600)
        self.title("Page d'accueil")

        self.configure(fg_color=BACKGROUND_COLOR)

        self.header = Header(master=self)
        self.header.pack(side="top", fill="x")

        self.current_body = None
        self.show_body("BaseBody")

        self.footer = Footer(master=self)
        self.footer.pack(side="bottom", fill="x")

    def show_body(self, body, current_user=None):
        if self.current_body is not None:
            self.current_body.pack_forget()

        if body == "BaseBody":
            self.current_body = BaseBody(self, self.show_body)
        elif body == "AdminBody":
            self.current_body = AdminBody(self, self.show_body)
        elif body == "UserBody":
            self.current_body = UserBody(self, self.show_body, current_user)

        self.current_body.pack(fill="both", expand=True)