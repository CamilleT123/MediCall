FROM python:3.11

WORKDIR /backend

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y libsm6 libxext6 libxrender-dev && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y libgl1-mesa-glx
# RUN apt-get update && apt-get install -y \
#     ffmpeg \
#     && rm -rf /var/lib/apt/lists/*
# RUN apt-get update && apt-get install -y \
#     pulseaudio \
#     pulseaudio-utils \
#     alsa-utils \
#     libasound2 \
#     libasound2-plugins \
#     && rm -rf /var/lib/apt/lists/*


COPY . .

# Copier le script de démarrage
COPY start.sh /start_backend.sh
RUN chmod +x /start_backend.sh
RUN mkdir -p /etc/pulse
RUN mkdir -p /run/dbus
# # Créer l'utilisateur pulse si nécessaire
# # RUN useradd -r -g audio pulse

# # Installation de D-Bus
# RUN apt-get update && apt-get install -y \
#     dbus \
#     && rm -rf /var/lib/apt/lists/*

# # Configuration de PulseAudio
# RUN mkdir -p /var/run/pulse /var/lib/pulse /etc/pulse/system.pa.d
# RUN chown -R pulse:pulse /var/run/pulse /var/lib/pulse


# Exécuter le script au démarrage du conteneur
CMD ["/start_backend.sh"]


# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
