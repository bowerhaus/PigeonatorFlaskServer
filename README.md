# The Pigeonator ML Server Setup

For the machine learning inferencing we'll use a Debian 10 (Buster) VM running a Flask server to provide the ML API for the Pigeonator client(s). At some point it may be possible to run the models on the RPi client but for the time being we'll take advantage of the higher performance of a dedicated PC VM.

Currently the ML Server provides API endpoints for:
* Tensorflow Classification
* PyTorch Classification
* PyTorch Object Detection (via Detector wrapper)

For my specific implemention, I run this under Proxmox and it's configured with 8Gb memory and 32Gb disk.

## Proxmox Specific Config
If the server will be required to serve up the Tensorflow endpoint(s) then we need to passthrough host CPU features. Without this, TensorFlow may throw an Illegal instruction.

In the Proxmox console edit the VM CONF file and add `args: -cpu host,kvm=off`
  ```bash
  sudo nano /etc/pve/qemu-server/XXX.conf
  ```

## Debian ML Server Setup

From a freshly installed Debian 10 VM, perform the following steps:

* Allow sudo access for user
  ```bash
  su root
  /usr/sbin/usermod -aG sudo bower
  ```

* Install QEMU Guest Agent (Proxmox only)
  ```bash 
  apt-get install qemu-guest-agent
  ```
  Make sure that the agent is enabled in the Proxmox VM options and reboot.

* Install XRDP
  ```bash
  sudo apt update
  sudo apt install xfce4 xfce4-goodies xorg dbus-x11 x11-xserver-utils
  sudo apt install xrdp 
  sudo adduser xrdp ssl-cert
  ```

* Find IP address and setup Remote Desktop login
  ```bash
  ip -c a
  ```

* Fix up XRDP if required (Authentication Required to Create Color Managed Device)
  See this blog post: https://c-nergy.be/blog/?p=12073
  ```bash
  sudo sed -i 's/allowed_users=console/allowed_users=anybody/' /etc/X11/Xwrapper.config

  sudo bash -c "cat >/etc/polkit-1/localauthority/50-local.d/45-allow.colord.pkla" <<EOF
  [Allow Colord all Users]
  Identity=unix-user:*
  Action=org.freedesktop.color-manager.create-device;org.freedesktop.color-manager.create-profile;org.freedesktop.color-manager.delete-device;org.freedesktop.color-manager.delete-profile;org.freedesktop.color-manager.modify-device;org.freedesktop.color-manager.modify-profile
  ResultAny=no
  ResultInactive=no
  ResultActive=yes
  EOF

  sudo bash -c "cat >/etc/polkit-1/localauthority/50-local.d/46-allow-update-repo.pkla" <<EOF
  [Allow Package Management all Users]
  Identity=unix-user:*
  Action=org.freedesktop.packagekit.system-sources-refresh
  ResultAny=yes
  ResultInactive=yes
  ResultActive=yes
  EOF
  ```

* Install VSCode
  Goto  https://code.visualstudio.com/Download and download the appropriate .deb installer.
  ```bash 
  sudo apt install ./code_1.55.2-1618307277_amd64.deb
  ```

* Install Git & Keyring (for GitHub authentication) and fetch Pigeonator Repo
  ```bash
  sudo apt install git # DON'T use git-all - it will hang at boot
  sudo apt install gnome-keyring
  git config --global user.name "Andy Bower"
  git config --global user.email "bower@object-arts.com"

* Set up Samba for file sharing
  Follow basic instructions here: https://vitux.com/debian_samba/

  ```bash
  sudo apt install samba
  sudo mkdir /samba
  sudo chmod 777 /samba
  sudo cp /etc/samba/smb.conf ~/Documents smb_backup.conf
  sudo nano /etc/samba/smb.conf

  # Add to bottom of file:
  [samba-share]
  comment = Samba on Debian
  path = /samba
  read-only = no
  browsable = yes
  writeable = yes
  valid_users = samba, bower

  sudo useradd samba
  sudo smbpasswd -a samba
  sudo smbpasswd -a bower
  sudo systemctl restart smbd.service
  ```

* Set up Python
  ```bash
  sudo apt install python3-pip
  sudo apt-get install python3-venv
  ```

* Set up Firewall
  ```bash
  sudo apt install ufw
  sudo ufw default deny incoming
  sudo ufw default allow outgoing
  sudo ufw allow 38100 # Or whatever
  sudo ufw enable
  ```

* Fetch PigeonatorFlaskServer from GitHub
```bash
  mkdir ~/Projects
  cd ~/Projects
  git clone https://github.com/bowerhaus/PigeonatorFlaskServer.git
```
* Create and activate a virtual environment
```bash
  cd ~/Projects/PigeonatorFlaskServer
  python -m venv .venv
  source .venv/bin/activate
```

* Install Flask, Tensorflow, PyTorch, Detecto and other dependencies
```bash
  python3 -m pip install --upgrade pip
  pip3 install -r requirements.txt
```
## Using Seq for Logging

In my implementation I use a Seq Server (https://datalust.co/) to act as a sink for log messages. Even though this isn't ML specific, I run this on the ML Server inside a Docker container. Installation instructions are here: https://hub.docker.com/r/datalust/seq,

```bash
  sudo docker run --name seq -d --restart unless-stopped -e ACCEPT_EULA=Y -p 5341:80 datalust/seq:latest
  sudo ufw allow 5341
```

## Copy Across Model Files

The ML Server can host several different models simultaneously. The chosen model is identified by name as part of the endpoint name. Simply copy your model into the Model folder and it will be loaded on first access by the Flask server. Note that model names are case sensitive so the filename must exactly match that in the API call.

## Power Up the Flask Server

The server can either be executed directly from a shell or can be debugged using VSCode. With the latter, I've found it is best to start it from the command line in the correct working folder:

```bash
  cd ~/Projects/PigeonatorFlaskServer
  source .venv/bin/activate
  python FlaskServer.py
  # or
  code
```