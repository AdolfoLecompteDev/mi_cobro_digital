import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import icon from 'astro-icon';
// CAMBIO AQUÍ: Importa específicamente el servidor de Vercel
import vercel from '@astrojs/vercel/serverless'; 

export default defineConfig({
  output: 'server', 
  
  integrations: [
    tailwind(), 
    icon()
  ],
  
  adapter: vercel({
    webAnalytics: { enabled: true },
    // Eliminamos 'isr: false' por ahora para usar la config más básica y estable
  }),

  build: {
    // IMPORTANTE: Cambia a 'file'. 
    // Vercel a veces se pierde buscando el entry.mjs cuando el formato es 'directory' en subcarpetas
    format: 'file' 
  },

  vite: {
    build: {
      cssCodeSplit: true,
    }
  }
});