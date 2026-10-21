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

### Ottimizzazioni per modello

Trascrvibe sceglie automaticamente i parametri migliori per ogni modello:

- **tiny e base**: `beam_size=1` (ricerca greedy) e nessun contesto dal segmento precedente → massima velocità, ideali per bozze e note brevi.
- **small, medium e large-v3**: `beam_size=5` → il modello esplora 5 ipotesi per segmento, per la massima qualità su interviste, lezioni e registrazioni importanti.
- **Tutti**: filtro VAD attivo → i silenzi vengono saltati, evitando lavoro inutile e riducendo le ripetizioni.

## Requisiti

- Python 3.10 o superiore (consigliato 3.13)
- Node.js 18 o superiore (solo per la UI web)
- Windows, macOS o Linux

## Installazione (sviluppo)

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

## Avvio

1. Avvia il backend:

```bash
uvicorn "app.main:create_app" --factory --host 127.0.0.1 --port 8000
```

2. In un secondo terminale, avvia la UI:

```bash
cd web
npm install
npm run dev
```

La UI è disponibile su http://localhost:5173 e usa il backend su http://127.0.0.1:8000.

- L'app ascolta **solo su 127.0.0.1**: nessun accesso dalla rete.
- Modalità demo (senza faster-whisper installato): imposta `TRSV_DEFAULT_PROVIDER=demo` in `.env`. Ogni output sarà marcato `[DEMO]`.
- Con `TRSV_DEFAULT_PROVIDER=faster-whisper` (predefinito) serve `pip install -r requirements.txt`; alla prima trascrizione il modello viene scaricato in locale.

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

The demo provider **does not actually transcribe**: every output is marked `[DEMO]` and exists only for developing and testing without models installed. See the Italian section above for the model guide, setup, test and run commands.
