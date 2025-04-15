import { useEffect, useState } from "react";

const CameraStream = ({ setIsStreaming }) => {
  const [imageSrc, setImageSrc] = useState(null);
  const [ws, setWs] = useState(null);

  const startStream = () => {
    const socket = new WebSocket("ws://localhost:8000/ws/video");
    socket.onmessage = (event) => {
		const data = JSON.parse(event.data);
		if (data.image) {
		setImageSrc(`data:image/jpeg;base64,${data.image}`);
		}
		if (data.audio) {
			const audioBlob = new Blob(
			[new Uint8Array(atob(data.audio).split("").map(c => c.charCodeAt(0)))],
			{ type: "audio/mp3" }
			);
			const audioURL = URL.createObjectURL(audioBlob);
			const audio = new Audio(audioURL);
			audio.play();
		}
    };
    setWs(socket);
  };

  const stopStream = () => {
    if (ws) {
		ws.send(JSON.stringify({ action: "close" })); // ✅ Envoi du message de fermeture au serveur
		setTimeout(() => {
		  ws.close();
		  setWs(null);
		  setIsStreaming(false); // ✅ Revenir à l'écran par défaut après l'arrêt du stream
		}, 500);
    }
  };

  return (
    <div>
      <button onClick={startStream}>Activer la caméra</button>
      <button onClick={stopStream}>Désactiver</button>
      {imageSrc && <img src={imageSrc} alt="Flux vidéo" />}
    </div>
  );
};

export default CameraStream;
