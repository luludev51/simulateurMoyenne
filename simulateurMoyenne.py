import json
import requests
import base64
import time
import os
import colorama
import sys

class Color():
    def __init__(self):
        self.reset = colorama.Fore.RESET
        self.red = colorama.Fore.RED
        self.green = colorama.Fore.GREEN
        self.yellow = colorama.Fore.YELLOW
        self.blue = colorama.Fore.BLUE
        self.magenta = colorama.Fore.MAGENTA
        self.cyan = colorama.Fore.CYAN
        self.white = colorama.Fore.WHITE

color = Color()

print(color.reset)

def afficher_barre_progression(pourcentage):
    longueur_barre = 50  # longueur de la barre de progression en caractères
    rempli = int(pourcentage * longueur_barre / 100)
    barre = "█" * rempli + "-" * (longueur_barre - rempli)
    sys.stdout.write(f"\r|{barre}| {pourcentage}%")
    sys.stdout.flush()

def Login(id, password):
    identification = id

    data={
        "identifiant": id,
        "motdepasse": password,
        "isReLogin": False,
        "uuid": "",
        "fa": []
    }

    headers = {
    "Content-Type": "application/form-data",
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    }

    url = "https://api.ecoledirecte.com/v3/login.awp?v=4.53.4"

    json_data = json.dumps(data)

    response = requests.post(url, data={'data': json_data}, headers=headers)

    if response.status_code == 200:
        json_response = json.loads(response.text)

    if json_response["code"] == 250:
        token = json_response["token"]

        headers = {
            "Content-Type": "application/form-data",
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
            "X-Token": token
        }

        data = {}

        json_data = json.dumps(data)

        url = "https://api.ecoledirecte.com/v3/connexion/doubleauth.awp?verbe=get&v=4.53.4"

        response = requests.post(url, data={'data': json_data}, headers=headers)

        question = response.json()["data"]["question"]
        question = base64.b64decode(question).decode("utf-8")

        propositions = response.json()["data"]["propositions"]

        print(f"{color.blue}Pour des questions de sécurité, veuillez répondre à cette question :{color.reset} \n {question}")

        message = "\n".join(f"{nb}. {base64.b64decode(proposition).decode('utf-8')}" for nb, proposition in enumerate(propositions, start=1))
        print(message)

        message = input(color.green + "Votre choix : ")
        print(color.reset)

        selection = int(message)
        selection = base64.b64decode(propositions[selection - 1]).decode("utf-8") # Getting the answer
        selection = base64.b64encode(selection.encode("utf-8")).decode("utf-8") # Encoding it back to base64

        data = {
            "choix": selection
        }
        json_data = json.dumps(data)

        url = "https://api.ecoledirecte.com/v3/connexion/doubleauth.awp?verbe=post&v=4.53.4"

        response = requests.post(url, data={'data': json_data}, headers=headers)

        if not response.json()["code"] == 200:
            print(color.red + "Mauvaise réponse, merci de reessayer.")
            # write_log(f"Wrong answer at the security question")
            time.sleep(2)
            return False
        else:
            cn = response.json()["data"]["cn"]
            cv = response.json()["data"]["cv"]

            data={
                "identifiant": id,
                "motdepasse": password,
                "isReLogin": False,
                "cn": cn,
                "cv": cv,
                "uuid": "",
                "fa": [
                    {
                        "cn": cn,
                        "cv": cv
                    }
                ]
            }

            json_data = json.dumps(data)

            headers = {
                "Content-Type": "application/form-data",
                "Accept": "application/json, text/plain, */*",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
                "X-Token": token
            }

            url = "https://api.ecoledirecte.com/v3/login.awp?v=4.53.4"

            response = requests.post(url, data={'data': json_data}, headers=headers)
            json_response = response.json()

            # print(f"You're logged as {identifiant}")
            # write_log(f"Client is connected as {identifiant}")
            time.sleep(1)

            id = json_response["data"]["accounts"][0]["id"]
            token = json_response["token"]
            etablissement = json_response["data"]["accounts"][0]["nomEtablissement"]
            credentials_valid = True
            print(f"{color.green}Connected as {identification} !")
            # print(json_response)
            print(color.reset)

            return id, token, identification, etablissement

    else:
        return False

def checkCommand(command, id, token, username, etablissement):

    if command == "help":
        print(color.cyan,"""LIST OF COMMANDS :
            - sim : Simulateur de moyenne
            - help : See the list of commands
            - exit : Exit the program
          """, color.reset)
        command = input(f"{color.green}{username}/{etablissement} >>> {color.reset}")
        checkCommand(command, id, token, username, etablissement)

    elif command == "sim":
        sim(id, token, username, etablissement)
        command = input(f"{color.green}{username}/{etablissement} >>> {color.reset}")
        checkCommand(command, id, token, username, etablissement)

    elif command == "exit":
        exit()

    else:
        print("Command not found.")
        command = input(f"{color.green}{username}/{etablissement} >>> {color.reset}")
        checkCommand(command, id, token, username, etablissement)

def moyenne_ponderee(notes, coefficients):
    # Vérifie que les deux listes ont la même longueur
    if len(notes) != len(coefficients):
        raise ValueError("Les listes de notes et de coefficients doivent avoir la même longueur.")

    # Conversion des notes et coefficients en float pour éviter les erreurs de type
    notes = [float(note) for note in notes]
    coefficients = [float(coef) for coef in coefficients]

    # Calcul de la somme pondérée des notes
    somme_ponderee = sum(note * coef for note, coef in zip(notes, coefficients))

    # Calcul de la somme des coefficients
    somme_coefficients = sum(coefficients)

    # Calcul de la moyenne pondérée et arrondi à 1 chiffre après la virgule
    moyenne = round(somme_ponderee / somme_coefficients, 2) if somme_coefficients != 0 else 0

    return moyenne

def moyenne_ponderee_general(moyennes, coefficients):
    up = 0
    for i in range(len(moyennes)):
        # print(moyennes[i], coefficients[i])
        up += moyennes[i] * coefficients[i]
    down = sum(coefficients)

    return round(up / down, 2)

def calculer_moyennes(subjects, subject_values, subject_coeff, subject_average):
    # Calcul des moyennes par matière en utilisant la fonction calculer_moyenne_matiere

    print("Moyennes par matière :")
    for subject in subjects:
        moy = moyenne_ponderee(subject_values[subject], subject_coeff[subject])
        if subject[1].islower() == False:
            print(f"{subject}: {moy}")
        else:
            print(f"-------{subject}-------")
        subject_average[subject] = moy




    # Demande des coefficients manuels pour chaque matière
    general_coeffs = {}
    general_coeffs["Enseignements de Tronc Commum"] = 0
    general_coeffs["Enseignements de Spécialité"] = 0
    general_coeffs["FRANCAIS"] = 10
    general_coeffs["HISTOIRE-GEOGRAPHIE"] = 6
    general_coeffs["ANGLAIS LV1"] = 6
    general_coeffs["ESPAGNOL LV2"] = 6
    general_coeffs["ENSEIGN.SCIENTIFIQUE"] = 6
    general_coeffs["ED.PHYSIQUE & SPORT."] = 6
    general_coeffs["ENS. MORAL & CIVIQUE"] = 2
    general_coeffs["MATHEMATIQUES"] = 13
    general_coeffs["PHYSIQUE-CHIMIE"] = 13
    general_coeffs["NUMERIQUE SC.INFORM."] = 13

    # print("-------------------------")
    # print(subject_average)
    # print("-------------------------")
    # print(general_coeffs)

    # Calcul de la moyenne générale en utilisant la fonction calculer_moyenne_generale

    temp = []
    temp_coeff = []
    for i in general_coeffs:
        if general_coeffs[i] == 0:
            continue
        elif subject_values[i] == []:
            # print(f"{i} : Pas de note")
            continue
        else:
            temp.append(subject_average[i])
            temp_coeff.append(general_coeffs[i])


    general_average = moyenne_ponderee_general(temp, temp_coeff)

    print(f"\nMoyenne générale : {general_average}/20")

def boucle(subjects, subject_values, subject_coeff, subject_average, id, token, username, etablissement):
    subjectNew = ""
    while subjectNew == "":
        subjectNew = input("Entrez le nom de la matière où vous souhaitez ajouter une note (ou 'quit' pour revenir au menu précedent): ")
        if subjectNew == "quit":
            os.system('cls' if os.name == 'nt' else 'clear')
            command = input(f"{username}/{etablissement} >>> ")
            checkCommand(command, id, token, username, etablissement)
            break
        elif subjectNew not in subjects:
            print("Matière introuvable !")
            print("Veuillez entrer le nom exact de la matière.")
            subjectNew = ""
        else:
            return subjectNew

def sim(id, token, username, etablissement):
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Bienvenue sur le simulateur de moyenne !")
    print("Récupération de vos notes actuelles...")
    print()
    print()
    print()
    print()
    print()
    print()
    print()
    afficher_barre_progression(0)

    url = f"https://api.ecoledirecte.com/v3/eleves/{id}/notes.awp?verbe=get&v=4.46.3"
    data = {"anneeScolaire": ""}
    headers = {
        "Content-Type": "application/form-data",
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "X-Token": token
    }
    json_data = json.dumps(data)
    response = requests.post(url, data={'data': json_data}, headers=headers)
    response = response.json()

    afficher_barre_progression(27)

    subjects = []
    # print(response)
    for periode_data in response["data"]["periodes"][0]["ensembleMatieres"]["disciplines"]:
        discipline = periode_data["discipline"]
        subjects.append(discipline)

    # Stockage des valeurs par matière
    subject_values = {subject: [] for subject in subjects}
    subject_coeff = {subject: [] for subject in subjects}
    subject_average = {subject: [] for subject in subjects}

    time.sleep(0.5)
    afficher_barre_progression(60)

    for note in response["data"]["notes"]:
        subject = note["libelleMatiere"]
        valeur = note["valeur"].replace(",", ".")  # Conversion pour manipulation
        notesure = note["noteSur"]
        coeff = note["coef"]



        # Calcul de la note sur 20
        # print(note)
        noteon20 = (float(valeur) / float(notesure)) * 20


        if coeff != 0 and note["nonSignificatif"] == False:
            # print(coeff)
            subject_values[subject].append(noteon20)
            subject_coeff[subject].append(coeff)

    afficher_barre_progression(86)
    time.sleep(1)

    afficher_barre_progression(100)
    time.sleep(1)

    os.system('cls' if os.name == 'nt' else 'clear')

    calculer_moyennes(subjects, subject_values, subject_coeff, subject_average)


    print()
    print()

    while True:

        subjectNew = boucle(subjects, subject_values, subject_coeff, subject_average, id, token, username, etablissement)



        note = float(input("Entrez la note sur 20 : "))
        coeff = int(input("Entrez le coefficient de la note : "))
        subject_values[subjectNew].append(note)
        subject_coeff[subjectNew].append(coeff)
        calculer_moyennes(subjects, subject_values, subject_coeff, subject_average)






    # os.system('cls' if os.name == 'nt' else 'clear')







def main():
    id = input("Identifiant : ")
    password = input("Mot de passe : ")
    try:id, token, username, etablissement = Login(id, password)
    except:
        print(f"{color.red}Identifiant ou mot de passe invalide !", color.reset)
        exit()
    if id == False:
        exit()
    else:
        command = input(f"{color.green}{username}/{etablissement} >>> {color.reset}")
        checkCommand(command, id, token, username, etablissement)

main()