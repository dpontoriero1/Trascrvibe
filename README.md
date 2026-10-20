# Trascrvibe

Trascrvibe trascrive file audio e video **in locale**, sul tuo computer, e restituisce un testo modificabile esportabile in TXT, SRT e VTT.

- **Privacy**: i file restano sul tuo computer. Nessun dato viene inviato a servizi esterni (al primo avvio il modello Whisper viene scaricato da Hugging Face; poi tutto avviene in locale).
- **UI bilingue**: italiano e inglese.
- **Provider astratto**: motore reale (`faster-whisper`) o modalità demo esplicitamente marcata.

## Stato del progetto

| Area | Stato |
|---|---|
| Configurazione + interfaccia provider | Implementato |
| Provider demo marcato [DEMO] | Implementato |
| Motore locale faster-whisper | Implementato (richiede `pip install -r requirements.txt`; alla prima esecuzione scarica il modello) |
| Upload, validazione, coda lavori, API REST | Implementato e testato (con provider demo) |
| UI bilingue IT/EN | Pianificato (prossimo commit) |
| Export TXT/SRT/VTT | Pianificato |
| Riconoscimento parlanti | Fase successiva all'MVP |
| Traduzione | Fase successiva all'MVP |

Il provider demo **non trascrive davvero**: ogni suo output è marcato `[DEMO]` e serve solo a sviluppare e testare senza modelli installati.

## Requisiti

- Python 3.10 o superiore
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

## Avvio (API; la UI web arriva nel prossimo commit)

```bash
uvicorn "app.main:create_app" --factory --host 127.0.0.1 --port 8000
```

- Documentazione interattiva delle API: http://127.0.0.1:8000/docs
- L'app ascolta **solo su 127.0.0.1**: nessun accesso dalla rete.
- Modalità demo (senza faster-whisper installato): imposta `TRSV_DEFAULT_PROVIDER=demo` in `.env`. Ogni output sarà marcato `[DEMO]`.
- Con `TRSV_DEFAULT_PROVIDER=faster-whisper` (predefinito) serve `pip install -r requirements.txt`; alla prima trascrizione il modello viene scaricato in locale.

## Configurazione

Copia `.env.example` in `.env` e modifica i valori. Trascrvibe **non richiede alcuna chiave API**.

## Licenze

Il codice di Trascrvibe è rilasciato sotto licenza MIT. Le dipendenze mantengono le rispettive licenze: FastAPI e Uvicorn (MIT), faster-whisper (MIT), modelli Whisper originali di OpenAI (MIT).

---

# Trascrvibe (English)

Trascrvibe transcribes audio and video files **locally**, on your computer, and returns editable text exportable as TXT, SRT and VTT.

- **Privacy**: files stay on your computer. No data is sent to external services (on first run the Whisper model is downloaded from Hugging Face; everything after that is local).
- **Bilingual UI**: Italian and English.
- **Abstract provider**: real engine (`faster-whisper`) or an explicitly marked demo mode.

The demo provider **does not actually transcribe**: every output is marked `[DEMO]` and exists only for developing and testing without models installed. See the Italian section above for setup, test and run commands.
