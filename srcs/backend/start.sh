#!/bin/bash

# Créer les répertoires nécessaires
mkdir -p /var/run/pulse
mkdir -p /etc/pulse/system.pa.d
mkdir -p /var/lib/pulse

# Créer le fichier de configuration système
cat > /etc/pulse/system.pa << EOF
#!/usr/bin/pulseaudio -nF
load-module module-native-protocol-unix auth-anonymous=1
load-module module-native-protocol-tcp auth-anonymous=1
load-module module-always-sink
load-module module-null-sink
load-module module-suspend-on-idle
EOF

# Définir les permissions
chown -R pulse:pulse /var/run/pulse
chown -R pulse:pulse /var/lib/pulse
chown -R pulse:pulse /etc/pulse

# Démarrer PulseAudio en mode système
pulseaudio --system --disallow-exit --disallow-module-loading --daemonize=no &

# Attendre que PulseAudio démarre
sleep 2

# Lancer FastAPI
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload