import getpass
import shutil
import keyring
import random
import requests
import os
import subprocess

from requests.exceptions import ConnectTimeout, ConnectionError, RequestException
from time import sleep

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

def get_gpg_keys():
    """Lists GPG keys with cryptographic method and key strength."""
    cmd = ["gpg", "--list-keys", "--with-colons"]

    try:
        output = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    except subprocess.CalledProcessError:
        print("Error retrieving GPG keys.")
        return []

    keys = []
    for line in output.splitlines():
        parts = line.split(":")
        if parts[0] == "pub":  # Public key entry
            key_type = parts[3]  # Algorithm type (1=RSA, 16=ElGamal, 17=DSA, 18=ECDSA, 19=Ed25519, 22=Curve25519)
            key_size = int(parts[2])  # Key length in bits
            key_id = parts[4][-8:]  # Last 8 digits of the key fingerprint

            # Determine key type and strength
            if key_type == "1":
                algo = "RSA"
                secure = key_size >= 4096
            elif key_type == "16":
                algo = "ElGamal"
                secure = False  # Not recommended for password storage
            elif key_type == "17":
                algo = "DSA"
                secure = False  # Deprecated
            elif key_type == "18":
                algo = "ECDSA"
                secure = key_size >= 256  # At least 256 bits
            elif key_type == "19":
                algo = "Ed25519"
                secure = True  # Secure by design
            elif key_type == "22":
                algo = "Curve25519"
                secure = True  # Secure by design
            else:
                algo = f"Unknown ({key_type})"
                secure = False

            if secure:
                keys.append((key_id, algo, key_size))

    return keys

home_dir = os.path.expanduser("~")
directory_path = os.path.join(home_dir, "videos_select")

if not os.path.isdir(directory_path):
    try:
        os.makedirs(directory_path, mode=0o755)
        print("Le dossier videos_select a été créé dans votre dossier home.\n")
    except OSError as e:
        print(f"Error creating directory: {e}")

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

user = os.environ.get("USER")

print("Configuration des tâches cron du programme tv-select:\n")

timeout = 6

try:
    response = requests.head("https://tv-select.fr", timeout=timeout)
except ConnectTimeout:
    print(f"Connection to TV-select.fr timed out after {timeout} seconds")
except ConnectionError:
    print(f"Failed to connect to TV-select.fr")
except RequestException as e:
    print(f"Request failed: {e}")

http_response = response.status_code

if http_response != 200:
    print(
        "\nLa box TV-select n'est pas connectée à internet. Veuillez "
        "vérifier votre connection internet et relancer le programme "
        "d'installation.\n\n"
    )
    exit()

answers = ["oui", "non"]

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

heure = random.randint(6, 23)
minute = random.randint(0, 58)
minute_2 = minute + 1
heure_auto_update = heure - 1
minute_auto_update = random.randint(0, 59)

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

params = ["CRYPTED_CREDENTIALS", "CURL_HOUR", "CURL_MINUTE"]

with open("/home/" + user + "/.config/tvselect-fr/config.py", "w") as conf:
    for param in params:
        if "CRYPTED_CREDENTIALS" in param:
            if crypted.lower() == "oui":
                conf.write("CRYPTED_CREDENTIALS = True\n")
            else:
                conf.write("CRYPTED_CREDENTIALS = False\n")
        elif "CURL_HOUR" in param:
            conf.write(f"{param} = {heure}\n")
        elif "CURL_MINUTE" in param:
            conf.write(f"{param} = {minute}\n")

hdmi_screen = "no_se"

if crypted.lower() == "oui":
    ssh_connection = os.environ.get("SSH_CONNECTION")
    display_available = os.environ.get("DISPLAY")
    if ssh_connection is not None or not display_available:
        while hdmi_screen.lower() not in answers:
            hdmi_screen = input("\nVous êtes connecté en SSH à votre machine ou votre système pourrait ne "
                "pas avoir d'interface graphique. Avez-vous accès à une interface graphique? "
                "Répondez 'oui' si vous pouvez connecter un écran et visualiser les applications, "
                "ou 'non' si vous ne pouvez vous connecter que via SSH ou si aucune interface graphique n'est disponible"
                "(exemple: VM, carte Nanopi-NEO, server, OS sans interface graphique): ").strip().lower()
    else:
        hdmi_screen = "oui"
    if hdmi_screen == "non":
        gpg_keys = get_gpg_keys()
        if not gpg_keys:
            print(
                "Aucune clé GPG suffisament sécurisé n'est détectée dans votre système. Vous pouvez ajouter une clé GPG "
                "à votre trousseau de clés pour chiffrer vos identifiants en utilisant "
                "la commande suivante pour générer une nouvelle clé GPG: "
                "\n\ngpg --full-generate-key\nVous pouvez suivre le tutoriel suivant pour ajouter "
                "la clé GPG sécurisé: https://tv-select.fr/advice-gpg puis relancez le programme d'installation."
            )
            exit()
        else:
            print("Voici la liste de vos clés GPG qui sont assez sécurisées pour chiffrer vos identifiants de connexion:")
            for index, (key_id, algo, key_size) in enumerate(gpg_keys, start=1):
                print(f"{index}) Key ID: {key_id}, Algorithm: {algo}, Size: {key_size} bits")
            if len(gpg_keys) > 1:
                selected_key = 0
                while not (1 <= selected_key <= len(gpg_keys)):
                    try:
                        selected_key = int(input(f"Merci de choisir un nombre entre 1 et {len(gpg_keys)} "
                                                "pour sélectionner la clé de chiffrement GPG à utiliser: "))
                    except ValueError:
                        print("Veuillez entrer un nombre valide.")
            else:
                selected_key = 1
            process = subprocess.run(["pass", "init", gpg_keys[selected_key - 1][0]],
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


http_status = 403

if hdmi_screen == "non":
    sleep(1)
    print("Veuillez saisir l'email de votre compte à TV-select.fr. L'email "
          "ne sera pas visible par mesure de sécurité et devra être répété "
          "une 2ème fois pour s'assurer d'avoir saisi l'email correctement. S'"
          "il vous est posé la question 'An entry already exists for "
          "tv-select/email. Overwrite it? [y/N] y', répondez y")
    insert_email = subprocess.run(["pass", "insert", "tv-select/email"])
    sleep(1)
    print("Veuillez saisir le mot de passe de votre compte à TV-select.fr. "
          "Le mot de passe ne sera pas visible par mesure de sécurité et "
          "devra être répété une 2ème fois pour s'assurer d'avoir saisi "
          "l'email correctement. S'il vous est posé la question 'An entry already exists for "
          "tv-select/password. Overwrite it? [y/N] y', répondez y")
    insert_password = subprocess.run(["pass", "insert", "tv-select/password"])
else:
    username_tvselect = input(
        "Veuillez saisir votre identifiant de connexion (adresse "
        "email) sur TV-select.fr: "
    )
    password_tvselect = getpass.getpass(
        "Veuillez saisir votre mot de passe sur TV-select.fr: "
    )


while http_status != 200:

    if hdmi_screen == "non":
        pass_email = subprocess.run(["pass", "tv-select/email"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        username_tvselect = pass_email.stdout.strip()
        pass_password = subprocess.run(["pass", "tv-select/password"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        password_tvselect = pass_password.stdout.strip()

    timeout = 4

    try:
        response = requests.head("https://www.tv-select.fr/api/v1/prog", auth=(username_tvselect, password_tvselect), timeout=timeout)
    except ConnectTimeout:
        print(f"Connection to TV-select.fr timed out after {timeout} seconds")
    except ConnectionError:
        print(f"Failed to connect to TV-select.fr")
    except RequestException as e:
        print(f"Request failed: {e}")

    http_status = response.status_code

    if http_status != 200:
        try_again = input(
            "Le couple identifiant de connexion et mot de passe "
            "est incorrect.\nVoulez-vous essayer de nouveau?(oui ou non): "
        )
        answer_hide = "maybe"
        if try_again.lower() == "oui":
            if hdmi_screen == "oui" or hdmi_screen == "no_se":
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
                sleep(1)
                print("Veuillez saisir l'email de votre compte à TV-select.fr. L'email "
                    "ne sera pas visible par mesure de sécurité et devra être répété "
                    "une 2ème fois pour s'assurer d'avoir saisi l'email correctement.")
                insert_email = subprocess.run(["pass", "insert", "tv-select/email"])
                sleep(1)
                print("Veuillez saisir le mot de passe de votre compte à TV-select.fr. "
                    "Le mot de passe ne sera pas visible par mesure de sécurité et "
                    "devra être répété une 2ème fois pour s'assurer d'avoir saisi l'email correctement.")
                insert_password = subprocess.run(["pass", "insert", "tv-select/password"])
        else:
            exit()

netrc_path = os.path.expanduser("~/.netrc")
if not os.path.exists(netrc_path):
    subprocess.run(["touch", netrc_path], check=True)
    os.chmod(netrc_path, 0o600)

with open(f"/home/{user}/.netrc", "r") as file:
    lines = file.read().splitlines()

username_tvselect = username_tvselect.strip()
password_tvselect = password_tvselect.strip()

try:
    position = lines.index("machine www.tv-select.fr")
    lines[position + 1] = f"  login {username_tvselect}"
    if crypted.lower() == "non":
        lines[position + 2] = f"  password {password_tvselect}"
    else:
        lines[position + 2] = "  password XXXXXXXX"
except ValueError:
    lines.append("machine www.tv-select.fr")
    lines.append(f"  login {username_tvselect}")
    if crypted.lower() == "non":
        lines.append(f"  password {password_tvselect}")
    else:
        lines.append("  password XXXXXXXX")

with open(f"/home/{user}/.netrc", "w") as file:
    for line in lines:
        file.write(line + "\n")

if hdmi_screen == "oui" and crypted.lower() != "non":
    print("Si votre système d'exploitation ne déverrouille pas automatiquement le trousseau de clés "
            "comme sur Raspberry OS, une fenêtre du gestionnaire du trousseau s'est ouverte et il vous "
            "faudra la débloquer en saisissant votre mot de passe. Si c'est la première ouverture "
        "de votre trousseau de clé, il vous sera demandé de créer un mot de passe qu'il faudra renseigner à chaque "
        "nouvelle session afin de permettre l'accès des identifiants chiffrés au programme tvselect-fr.")

    keyring.set_password("tv-select", "username", username_tvselect)
    keyring.set_password("tv-select", "password", password_tvselect)

auto_update = "no_se"

while auto_update.lower() not in answers:
    auto_update = (
        input(
            "\n\nAutorisez-vous l'application à se mettre à jour automatiquement? "
            "Si vous répondez 'non', vous devrez mettre à jour l'application par "
            "vous-même. (répondre par oui ou non) : "
        )
        .strip()
        .lower()
    )

with open("cron_tasks.sh", "w") as cron_file:
    process = subprocess.run(["crontab", "-l"], stdout=cron_file, stderr=subprocess.PIPE, text=True)

if process.returncode != 0:
    print(f"\n Error listing crontab: {process.stderr}")
else:
    print("\n Crontab tasks saved to cron_tasks.sh")

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

cron_auto_update = (
    '{minute_auto_update} {heure_auto_update} * * * /bin/bash -c "$HOME'
    "/tvselect-fr/auto_update.sh >> $HOME/.local/share"
    '/tvselect-fr/logs/auto_update.log 2>&1"\n'.format(
        minute_auto_update=minute_auto_update, heure_auto_update=heure_auto_update
    )
)

if hdmi_screen == "oui" or hdmi_screen == "no_se":
    cron_lines = [curl if "tvselect-fr/curl_tvselect.sh" in cron else cron for cron in cron_lines]
else:
    cron_lines = [cron for cron in cron_lines if "tvselect-fr/curl_tvselect.sh" not in cron]
cron_lines = [cron_launch if "tvselect-fr &&" in cron else cron for cron in cron_lines]

if auto_update.lower() == "oui":
    cron_lines = [
        cron_auto_update if "tvselect-fr/auto_update" in cron else cron
        for cron in cron_lines
    ]
else:
    cron_lines = [cron for cron in cron_lines if "tvselect-fr/auto_update" not in cron]


cron_lines_join = "".join(cron_lines)

if (hdmi_screen == "oui" or hdmi_screen == "no_se") and "tvselect-fr/curl_tvselect.sh" not in cron_lines_join:
    cron_lines.append(curl)
if "cd /home/$USER/tvselect-fr &&" not in cron_lines_join:
    cron_lines.append(cron_launch)

if auto_update.lower() == "oui" and "tvselect-fr/auto_update" not in cron_lines_join:
    cron_lines.append(cron_auto_update)

with open("cron_tasks.sh", "w") as crontab_file:
    for cron_task in cron_lines:
        crontab_file.write(cron_task)

process = subprocess.run(["crontab", "cron_tasks.sh"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
if process.returncode != 0:
    print(f"\n Error loading cron tasks: {process.stderr}")
else:
    print("\n Cron tasks loaded successfully.")

process = subprocess.run(["rm", "cron_tasks.sh"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
if process.returncode != 0:
    print(f"\n Error deleting file: {process.stderr}")
else:
    print("\n File 'cron_tasks.sh' deleted successfully.")

print("\nLes tâches cron de votre box TV-select sont maintenant configurés!\n")
