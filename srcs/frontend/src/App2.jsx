import { useState, useEffect } from 'react'
import axios from "axios";
import reactLogo from './assets/react.svg'
import CameraStream from "./components/CameraStream";
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [count, setCount] = useState(0);
  const [message, setMessage] = useState("");

  useEffect(() => {
    axios.get("http://localhost:8000/ws/video/") // Appel à l'API backend FastAPI
      .then((response) => {
        setMessage(response.data.message);
      })
      .catch((error) => {
        console.error("Erreur lors de la récupération des données", error);
      });
  }, []);

  return (
    <>
		<div>
			<h1>Détection de mouvements</h1>
			<CameraStream />
		</div>
      <div>
        <a href="https://vite.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Vite + React</h1>
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
		<div className="p-4">
      		<h1 className="text-2xl font-bold">Bienvenue</h1>
      		<p className="mt-4 text-lg">{message}</p>
    	</div>
        <p>
          Edit <code>src/App.jsx</code> and save to test HMR
        </p>
      </div>
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>
    </>
  )
}

export default App
