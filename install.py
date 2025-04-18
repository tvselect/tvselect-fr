import getpass
import shutil
import keyring
import random
import requests
import tempfile
import os
import subprocess

def create_dir_with_permissions(path, mode):
    """
    Creates a directory if it doesn't exist and sets the desired permissions.
    Updates the permissions if the directory already exists.

    Parameters:
        path (str): The directory path to create or check.
        mode (int): The permission mode to set (e.g., 0o740).
    """
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        os.chmod(path, mode)
        print(f"Directory created: {path}")
    else:
        print(f"Directory already exists: {path}")

permission_mode = 0o700

create_dir_with_permissions(os.path.expanduser("~/.local"), permission_mode)
create_dir_with_permissions(os.path.expanduser("~/.local/share"), permission_mode)
create_dir_with_permissions(
    os.path.expanduser("~/.local/share/tvselect-fr"), permission_mode
)
create_dir_with_permissions(
    os.path.expanduser("~/.local/share/tvselect-fr/logs"), permission_mode
)
create_dir_with_permissions(os.path.expanduser("~/.config"), permission_mode)
create_dir_with_permissions(os.path.expanduser("~/.config/tvselect-fr"), permission_mode)
create_dir_with_permissions(
    os.path.expanduser("~/.config/tvselect-fr/iptv_providers"), permission_mode
)

home_dir = os.path.expanduser("~")
cmd = ["ls", home_dir]
ls_home = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
ls_directory = "videos_select" if "videos_select\n" in ls_home.stdout else ""

if ls_directory == "":
    directory_path = os.path.join(home_dir, "videos_select")
    process = subprocess.run(["mkdir", "-p", directory_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if process.returncode != 0:
        print(f"❌ Error creating directory: {process.stderr.decode()}")
    else:
        print("Le dossier videos_select a été créé dans votre dossier home.\n")

user = os.environ.get("USER")

cmd = ["sed", "-i", f"3s|.*|cd /home/{user}/videos_select|", "launch_record.sh"]
result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

print("Configuration des tâches cron du programme tv-select:\n")

response = requests.head("https://tv-select.fr")
http_response = response.status_code

if http_response != 200:
    print(
        "\nLa box TV-select n'est pas connectée à internet. Veuillez "
        "vérifier votre connection internet et relancer le programme "
        "d'installation.\n\n"
    )
    exit()

username_tvselect = input(
    "Veuillez saisir votre identifiant de connexion (adresse "
    "email) sur tv-select.fr: "
)

password_tvselect = getpass.getpass(
    "Veuillez saisir votre mot de passe sur " "tv-select.fr: "
)

answers = ["oui", "non"]
http_status = 403

while http_status != 200:

    response = requests.head("https://www.tv-select.fr/api/v1/prog", auth=(username_tvselect, password_tvselect))
    http_status = response.status_code

    if http_status != 200:
        try_again = input(
            "Le couple identifiant de connexion et mot de passe "
            "est incorrecte\nVoulez-vous essayer de nouveau?(oui ou non): "
        )
        answer_hide = "maybe"
        if try_again.lower() == "oui":
            username_tvselect = input(
                "Veuillez saisir de nouveau votre identifiant de connexion (adresse email) sur TV-select.fr: "
            )
            while answer_hide.lower() not in answers:
                answer_hide = input(
                    "Voulez-vous afficher le mot de passe que vous saisissez "
                    "pour que cela soit plus facile? (répondre par oui ou non): "
                )
            if answer_hide.lower() == "oui":
                password_tvselect = input(
                    "Veuillez saisir de nouveau votre mot de passe sur TV-select.fr: "
                )
            else:
                password_tvselect = getpass.getpass(
                    "Veuillez saisir de nouveau votre mot de passe sur TV-select.fr: "
                )
        else:
            exit()

crypted = "no_se"

while crypted.lower() not in answers:
    crypted = input("\nVoulez vous chiffrer les identifiants de connection à "
                    "l'application web TV-select.fr? Si vous répondez oui, "
                    "il faudra penser à débloquer gnome-keyring (ou tout "
                    "autre backend disponible sur votre système) à chaque "
                    "nouvelle session afin de permettre l'accès aux "
                    "identifiants par l'application TV-select-fr. "
                    "(répondre par oui ou non) : ").strip().lower()

config_path = os.path.join("/home", user, ".config/tvselect-fr/config.py")
template_path = os.path.join("/home", user, "tvselect-fr/config_template.py")

if not os.path.exists(config_path):
    shutil.copy(template_path, config_path)
    os.chmod(config_path, 0o640)

params = ["CRYPTED_CREDENTIALS"]

with open("/home/" + user + "/.config/tvselect-fr/config.py", "w") as conf:
    for param in params:
        if "CRYPTED_CREDENTIALS" in param:
            if crypted.lower() == "oui":
                conf.write("CRYPTED_CREDENTIALS = True\n")
            else:
                conf.write("CRYPTED_CREDENTIALS = False\n")

if crypted.lower() == "non":
    netrc_path = os.path.expanduser("~/.netrc")
    if not os.path.exists(netrc_path):
        subprocess.run(["touch", netrc_path], check=True)
        subprocess.run(["chmod", "go=", netrc_path], check=True)

    with open(f"/home/{user}/.netrc", "r") as file:
        lines = file.read().splitlines()

    try:
        position = lines.index("machine www.tv-select.fr")
        lines[position + 1] = f"  login {username_tvselect}"
        lines[position + 2] = f"  password {password_tvselect}"
    except ValueError:
        lines.append("machine www.tv-select.fr")
        lines.append(f"  login {username_tvselect}")
        lines.append(f"  password {password_tvselect}")

    with open(f"/home/{user}/.netrc", "w") as file:
        for line in lines:
            file.write(line + "\n")

else:
    print("Merci de renseigner le mot de passe de la fenêtre de gnome-keyring qui vient de s'ouvrir "
        "si elle n'est pas déjà été débloquée lors de cette session. Si c'est la première ouverture "
        "de gnome-keyring, il vous sera demandé de créer un mot de passe qu'il faudra renseigner à chaque "
        "nouvelle session afin de permettre l'accès des identifiants chiffrés au programe tvselect-fr.")

    keyring.set_password("tv-select", "username", username_tvselect)
    keyring.set_password("tv-select", "password", password_tvselect)

heure = random.randint(6, 23)
minute = random.randint(0, 58)
minute_2 = minute + 1

if heure < 10:
    heure_print = "0" + str(heure)
else:
    heure_print = str(heure)

if minute < 10:
    minute_print = "0" + str(minute)
else:
    minute_print = str(minute)

answer = input(
    "\nVotre box TV-select va être configuré pour demander "
    "les informations nécessaires aux enregistrements à "
    "{heure}:{minute} . Votre box TV-select n'a besoin d'être "
    "connectée à internet seulement pendant 1 seconde par jour "
    "pour obtenir les informations nécessaires. Si votre box "
    "TV-select ne peut pas être connecté à internet à l'heure proposée, "
    "vous pouvez définir l'horaire manuellement. Voulez-vous changer "
    "l'horaire de téléchargement de vos informations personnalisées "
    "d'enregistrements? Répondez par oui si vous voulez changer l'horaire "
    "de {heure}H{minute} ou non si votre connection internet sera "
    "disponible à cette horaire: \n".format(heure=heure_print, minute=minute_print)
)

while answer.lower() not in answers:
    answer = input("Veuillez répondre par oui ou non: ")

if answer.lower() == "oui":
    heure = 24
    while heure < 6 or heure > 23:
        heure = int(
            input(
                "Choisissez une heure entre 6 et 23 (si vous ne "
                "pouvez avoir une connection internet que entre minuit "
                "et 6 heures du matin, contactez le support de "
                "TV-select afin de contourner cette restriction): "
            )
        )
    minute = 60
    while minute < 0 or minute > 58:
        minute = int(input("Choisissez les minutes entre 0 et 58: "))

    if heure < 10:
        heure_print = "0" + str(heure)
    else:
        heure_print = str(heure)

    if minute < 10:
        minute_print = "0" + str(minute)
    else:
        minute_print = str(minute)

    print(
        "\nVotre box TV-select va être configuré pour demander les "
        "informations nécessaires aux enregistrements à "
        "{heure}H{minute}".format(heure=heure_print, minute=minute_print)
    )
    minute_2 = minute + 1

with open("cron_tasks.sh", "w") as cron_file:
    process = subprocess.run(["crontab", "-l"], stdout=cron_file, stderr=subprocess.PIPE, text=True)

if process.returncode != 0:
    print(f"\n❌ Error listing crontab: {process.stderr}")
else:
    print("\n✅ Crontab tasks saved to cron_tasks.sh")

with open("cron_tasks.sh", "r") as crontab_file:
    cron_lines = crontab_file.readlines()

curl = (
    "{minute} {heure} * * * env DBUS_SESSION_BUS_ADDRESS=unix:path=/run"
    "/user/$(id -u)/bus /bin/bash $HOME/tvselect-fr/curl_"
    "tvselect.sh\n".format(
        minute=minute,
        heure=heure,
    )
)

cron_launch = (
    "{minute_2} {heure} * * * export TZ='Europe/Paris' USER='{user}' && "
    "cd /home/$USER/tvselect-fr && "
    "bash cron_launch_record.sh\n".format(user=user, minute_2=minute_2, heure=heure)
)

cron_lines = [curl if "curl_tvselect.sh" in cron else cron for cron in cron_lines]
cron_lines = [cron_launch if "/tvselect-fr &&" in cron else cron for cron in cron_lines]

cron_lines_join = "".join(cron_lines)

if "curl_tvselect.sh" not in cron_lines_join:
    cron_lines.append(curl)
if "cd /home/$USER/tvselect-fr &&" not in cron_lines_join:
    cron_lines.append(cron_launch)

with open("cron_tasks.sh", "w") as crontab_file:
    for cron_task in cron_lines:
        crontab_file.write(cron_task)

process = subprocess.run(["crontab", "cron_tasks.sh"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
if process.returncode != 0:
    print(f"\n❌ Error loading cron tasks: {process.stderr}")
else:
    print("\n✅ Cron tasks loaded successfully.")

process = subprocess.run(["rm", "cron_tasks.sh"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
if process.returncode != 0:
    print(f"\n❌ Error deleting file: {process.stderr}")
else:
    print("\n✅ File 'cron_tasks.sh' deleted successfully.")

print("\nLes tâches cron de votre box TV-select sont maintenant configurés!\n")
