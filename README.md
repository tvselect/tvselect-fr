# tvselect-fr v2.0.0

## Instructions d'installations:

sudo apt update && sudo apt install jq dvb-apps w-scan at curl

mkdir ~/.tzap

### La commande suivante demande entre 20 et 30 minutes avant d'être terminée:
w_scan -f t -c FR -X > ~/.tzap/channels.conf

### La commande suivante supprime le nommage des multiplexes (à lancer après la fin de la commande w_scan):
sed -i -e 's/(.*)//g' /home/$USER/.tzap/channels.conf

### Les 2 commandes précédentes (commençant pas w_scan et sed) sont à lancer de nouveau si vous déménagez loin de votre résidence ou si les fréquences de diffusion des chaînes ont changé.

cd ~ && curl https://github.com/tvselect/tvselect-fr/archive/refs/heads/master.zip -L -o tvselect-fr.zip

unzip tvselect-fr.zip && mv tvselect_fr-master tvselect-fr && rm tvselect-fr.zip

python3 install.py
