# Trascrvibe

Trascrvibe trascrive file audio e video **in locale**, sul tuo computer, e restituisce un testo modificabile esportabile in TXT, SRT e VTT.

- **Privacy**: i file restano sul tuo computer. Nessun dato viene inviato a servizi esterni (al primo avvio il modello Whisper viene scaricato da Hugging Face; poi tutto avviene in locale).
- **UI bilingue**: italiano e inglese.
- **Provider astratto**: motore reale (`faster-whisper`) o modalità demo esplicitamente marcata.
- **Limite di caricamento**: 5 GB per file (configurabile).

## Stato del progetto — MVP completo

| Area | Stato |
|---|---|
| Configurazione + interfaccia provider | Implementato |
| Provider demo marcato [DEMO] | Implementato |
| Motore locale faster-whisper | Implementato (richiede `pip install -r requirements.txt`; alla prima esecuzione scarica il modello) |
| Upload, validazione, coda lavori, API REST | Implementato e testato (con provider demo) |
| UI web bilingue IT/EN (upload, stati, editor, player) | Implementata |
| Export TXT/SRT/VTT | Implementato e testato |
| Riconoscimento parlanti | Fase successiva all'MVP |
| Traduzione | Fase successiva all'MVP |

Il provider demo **non trascrive davvero**: ogni suo output è marcato `[DEMO]` e serve solo a sviluppare e testare senza modelli installati.

## Modelli disponibili

I nomi (tiny, base, small, medium, large-v3) indicano la **dimensione del modello Whisper**: più è grande, più è accurato ma più è lento e occupa memoria.

| Modello | Peso scaricato | Velocità | Qualità | RAM consigliata | Quando usarlo |
|---|---|---|---|---|---|
| `tiny` | ~75 MB | ⚡⚡⚡ Molto veloce | Base | ~1 GB | Note veloci, bozze, PC poco potenti |
| `base` | ~145 MB | ⚡⚡⚡ Veloce | Buona | ~1 GB | Uso quotidiano, buon compromesso (**predefinito**) |
| `small` | ~500 MB | ⚡⚡ Medio | Molto buona | ~2 GB | Interviste, lezioni, podcast |
| `medium` | ~1,5 GB | ⚡ Lento | Ottima | ~5 GB | Registrazioni importanti |
| `large-v3` | ~3 GB | 🐢 Molto lento | Massima | ~10 GB | Massima accuratezza, PC potente |

Note pratiche:

- La qualità dipende molto anche dalla **pulizia dell'audio**: un file chiaro con `base` può superare un file rumoroso con `medium`.
- Tutti i modelli funzionano **offline** dopo il primo download.
- Su un PC senza scheda video potente, `base` o `small` sono la scelta consigliata.

### Ottimizzazioni di efficienza

Trascrvibe applica automaticamente queste ottimizzazioni:

- **Calcolo int8 sulla CPU** (invece di float32): tipicamente 2-4 volte più veloce, con perdita di qualità trascurabile. Con scheda video NVIDIA usa automaticamente `float16`.
- **Elaborazione a lotti (batching)**: il modello elabora più pezzi di audio insieme invece di uno alla volta; se il batching non è disponibile, ripiega automaticamente sul metodo classico.
- **Filtro VAD**: i silenzi vengono saltati, evitando lavoro inutile e riducendo le ripetizioni.
- **Parametri per modello**: `tiny` e `base` usano `beam_size=1` (massima velocità); `small`, `medium` e `large-v3` usano `beam_size=5` (massima qualità).

## Requisiti

- Python 3.10 o superiore (consigliato 3.13)
- Node.js 18 o superiore (solo per la UI web)
- Windows, macOS o Linux

## Installazione (sviluppo, una volta sola)

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
```

## Esecuzione dei test

```bash
pytest
```

I test usano il provider demo: non richiedono modelli installati e non toccano file reali.

## Avvio: due finestre

Trascrvibe è composto da due programmi che vanno avviati **insieme**, ciascuno nella sua finestra del terminale:

- **Finestra 1 — il backend (il "cervello")**: gestisce upload, code e trascrizione.
- **Finestra 2 — la UI web (la "faccia")**: è la pagina con i bottoni che apri nel browser.

### Finestra 1 — avvia il backend

Apri una finestra del terminale (su Windows: tasto Windows → scrivi `cmd` → Invio) e dai questi comandi, uno alla volta:

```bash
cd C:\Users\TUO_NOME\Desktop\Trascrvibe
.venv\Scripts\activate
uvicorn "app.main:create_app" --factory --host 127.0.0.1 --port 8000
```

(Sostituisci `TUO_NOME` con il tuo nome utente Windows. Su macOS/Linux usa `source .venv/bin/activate` al posto del secondo comando.)

Quando vedi la scritta `Uvicorn running on http://127.0.0.1:8000`, il backend è acceso. **Non chiudere questa finestra** finché usi Trascrvibe.

Verifica rapida: apri nel browser http://127.0.0.1:8000/api/health — devi vedere `{"status":"ok",...}`.

### Finestra 2 — avvia la UI web

Apri una **seconda** finestra del terminale e dai:

```bash
cd C:\Users\TUO_NOME\Desktop\Trascrvibe\web
npm install
npm run dev
```

(`npm install` serve solo la **prima volta**: dalle volte successive basta `npm run dev`.)

Quando vedi `VITE ready` e `Local: http://localhost:5173/`, apri nel browser:

**http://localhost:5173**

Da lì trascini un file audio/video, scegli lingua e modello, e attendi che lo stato diventi **Completato**. Alla prima trascrizione vera il modello Whisper viene scaricato (qualche minuto): è normale.

### Spegnere tutto

In ciascuna delle due finestre premi `Ctrl+C` (e conferma con `S` se richiesto). Puoi anche chiudere le finestre con la X.

### Se riapri una finestra nuova

Ricorda: ogni nuova finestra parte dalla cartella personale. Prima di dare i comandi, entra sempre nella cartella giusta con `cd` (come mostrato sopra) e, per la Finestra 1, riattiva la busta con `.venv\Scripts\activate`.

## Modalità demo (senza modelli installati)

Nel file `.env` dentro la cartella Trascrvibe, imposta:

```
TRSV_DEFAULT_PROVIDER=demo
```

Riavvia la Finestra 1: ogni output sarà marcato `[DEMO]` (non è una trascrizione reale). Per tornare alla trascrizione vera: `TRSV_DEFAULT_PROVIDER=faster-whisper`.

## GPU NVIDIA (opzionale)

Per usare una GPU NVIDIA (es. GeForce MX150): installa il driver NVIDIA aggiornato, **CUDA Toolkit 12.x** e **cuDNN 9 per CUDA 12** (copiando i `.dll` dalla cartella `bin` di cuDNN dentro la cartella `bin` di CUDA). Poi nel `.env`:

```
TRSV_DEVICE=cuda
TRSV_COMPUTE_TYPE=float16
```

Riavvia la Finestra 1. Per tornare alla CPU: `TRSV_DEVICE=auto` e `TRSV_COMPUTE_TYPE=auto`.

## Esportazione

Dalla pagina del lavoro completato: pulsanti TXT, SRT e VTT (endpoint `GET /api/jobs/{id}/export?format=txt|srt|vtt`). Le esportazioni partono sempre dai segmenti correnti, incluse le modifiche salvate.

## Configurazione

Copia `.env.example` in `.env` e modifica i valori. Trascrvibe **non richiede alcuna chiave API**. Il limite di caricamento predefinito è 5 GB (`TRSV_MAX_UPLOAD_MB=5120`).

## Licenze

Il codice di Trascrvibe è rilasciato sotto licenza MIT. Le dipendenze mantengono le rispettive licenze: FastAPI e Uvicorn (MIT), faster-whisper (MIT), React e Vite (MIT), modelli Whisper originali di OpenAI (MIT).

---

# Trascrvibe (English)

Trascrvibe transcribes audio and video files **locally**, on your computer, and returns editable text exportable as TXT, SRT and VTT.

- **Privacy**: files stay on your computer. No data is sent to external services (on first run the Whisper model is downloaded from Hugging Face; everything after that is local).
- **Bilingual UI**: Italian and English.
- **Abstract provider**: real engine (`faster-whisper`) or an explicitly marked demo mode.
- **Upload limit**: 5 GB per file (configurable).

The demo provider **does not actually transcribe**: every output is marked `[DEMO]` and exists only for developing and testing without models installed.

## Starting the app: two windows

Trascrvibe runs as two programs that must be started **together**, each in its own terminal window:

- **Window 1 — the backend (the "brain")**: handles uploads, the job queue and transcription.
- **Window 2 — the web UI (the "face")**: the page you open in your browser.

### Window 1 — start the backend

```bash
cd C:\Users\YOUR_NAME\Desktop\Trascrvibe
.venv\Scripts\activate
uvicorn "app.main:create_app" --factory --host 127.0.0.1 --port 8000
```

(On macOS/Linux use `source .venv/bin/activate` instead.) When you see `Uvicorn running on http://127.0.0.1:8000`, the backend is up. Keep this window open while using Trascrvibe.

### Window 2 — start the web UI

```bash
cd C:\Users\YOUR_NAME\Desktop\Trascrvibe\web
npm install
npm run dev
```

(`npm install` is only needed the first time.) When you see `VITE ready`, open **http://localhost:5173** in your browser.

### Stopping everything

Press `Ctrl+C` in both windows (confirm with `S` if asked), or close the windows.

See the Italian section above for the full model guide, GPU setup, demo mode and configuration.
