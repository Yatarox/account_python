from account_class import Account

def main():

    try:
        choix = int(input(""" 
                          1: Crée un nouveau compte
                          2: Se connecter (Avec le nom du user)
                          Choix : """))
        print(choix)
        if choix not in [1,2]:
            return("Mauvais choxi")
        elif choix == 1:
            user = Account.create_account()
        elif choix == 2:
            user = Account.load_account()
        user.process()
    except:
        print("Erreur")

    # user = Account("prout","1234554566",{"usd":60000},6,"2025-01-01")
    # card = Card(user, user.__account_number)
    # card.create_card()
if __name__ == '__main__':
    main()