import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    watch: {
      usePolling: true,  // 🔄 Active le polling pour détecter les fichiers modifiés
    },
    host: true,  // 🏡 Permet d'accéder au serveur depuis l'extérieur
    port: 3001,  // 📌 Port utilisé par Vite
    strictPort: true,  // ⏳ Évite que Vite change de port si 3001 est occupé
    hmr: {
      clientPort: 3001,  // 🔥 Permet au Hot Reload de bien fonctionner dans Docker
    },
  },
});
