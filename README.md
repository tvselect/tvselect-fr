# 📺 tvselect-fr v4.0.0

> 🔍 Turn TV into a discovery engine
> 📼 Automatically record TNT programs based on your interests

<!-- ![Demo](docs/demo.gif) -->

---

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Platform](https://img.shields.io/badge/Platform-Linux-green)
![Architecture](https://img.shields.io/badge/Arch-ARM%20%7C%20Raspberry%20Pi-orange)
![Status](https://img.shields.io/badge/Status-Active-success)
![Self-hosted](https://img.shields.io/badge/Self--Hosted-Yes-blueviolet)

---

## 🍿 How TV Select works

TV Select turns TV into a **personal discovery engine**.

You define what you care about:

* a documentary about wine 🍷
* a history episode 🏛️
* a space report 🚀
* that rare movie you couldn’t find anywhere 🎬
* a tennis documentary your son will love 🎾

Then the system works for you:

1. 🔍 Your searches are analyzed
2. 🧠 TV programs are continuously scanned
3. 🎯 When a match is found:

   * 📧 You receive a notification
   * 📼 A recording is triggered automatically

👉 No manual searching. No scheduling.

---

## 📖 TV Select Ecosystem

This project is part of the **TV Select ecosystem**.

👉 Overview & setup guide:

[![TV Select Ecosystem](https://img.shields.io/badge/TV%20Select-Ecosystem-blue)](https://github.com/tv-select)

## 📡 About tvselect-fr

tvselect-fr records **TNT (DVB-T) programs** using a tuner connected to your device.

👉 Ideal for:

* Raspberry Pi
* ARM boards
* Linux machines with DVB-T support

---

## 🧩 Architecture

```bash id="archtv"
Search → Match → Record → Watch
```

---

## 📦 What to expect

After installation:

* ❌ No immediate results
* ⏳ Wait for matches
* ✅ Videos appear automatically

---

## 📺 Watch your recordings anywhere

Videos are stored locally:

```bash id="pathvid"
~/videos_select
```

Accessible from:

* 💻 PC
* 📱 Smartphone
* 📺 TV
* 📲 Tablet

💡 Optional: share via Samba (see documentation)

---

## ⚡ Installation

### Requirements

* Linux (Raspberry Pi / Armbian)
* Python 3
* DVB-T tuner
* Account on https://www.tv-select.fr

---

### Install

```bash id="install1"
sudo apt update && sudo apt install jq dvb-apps w-scan at curl virtualenv seahorse
```

```bash id="install2"
cd ~
curl -L -o tvselect-fr.zip https://github.com/tvselect/tvselect-fr/archive/refs/tags/v4.0.0.zip
unzip tvselect-fr.zip
mv tvselect-fr-4.0.0 tvselect-fr
```

---

### Channel scan

```bash id="scan"
mkdir ~/.tzap
w_scan -f t -c FR -X -t 3 > ~/.tzap/channels.conf
sed -i -e 's/(.*)//g' ~/.tzap/channels.conf
```

---

### Setup

```bash id="setup"
mkdir -p ~/.local/share/tvselect-fr ~/.config/tvselect-fr

cd ~/.local/share/tvselect-fr
virtualenv -p python3 .venv
source .venv/bin/activate
pip install -r ~/tvselect-fr/requirements.txt

cd ~/tvselect-fr
python3 install.py
```

---

## ❓ FAQ

### Nothing happens?

Normal. Wait for a match.

---

### How long?

It depends on your search.

- Popular topics → results can appear within a day
- Rare content → may take longer

Set it once.
Forget it.

You'll be notified when something matches.

---

### No videos?

* No match yet
* Channel not available
* Signal issue

---

### Does it run all the time?

Yes.

---

## ⭐ Support

If you like this project:

👉 Star the repo
👉 Share it

---

## ⚠️ Disclaimer

For personal use only.
