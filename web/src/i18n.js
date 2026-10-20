export const STRINGS = {
  it: {
    tagline: 'Trascrizione locale di file audio e video',
    dropHere: 'Trascina qui un file audio o video',
    orClick: 'oppure clicca per sceglierlo',
    language: 'Lingua',
    autoDetect: 'Rileva automaticamente',
    model: 'Modello',
    modelHint: 'tiny = veloce · large-v3 = accurato',
    maxSize: 'Dimensione massima',
    demoBanner:
      'Modalità DEMO attiva: gli output non sono trascrizioni reali.',
    jobs: 'Lavori',
    noJobs: 'Nessun lavoro. Carica un file per iniziare.',
    statusQueued: 'In attesa',
    statusProcessing: 'In elaborazione',
    statusDone: 'Completato',
    statusFailed: 'Fallito',
    delete: 'Elimina',
    confirmDelete: 'Eliminare questo lavoro e i suoi file?',
    backToList: '← Tutti i lavori',
    editHint:
      'Clicca su un testo per correggerlo. Clicca su un timestamp per spostare la riproduzione.',
    save: 'Salva modifiche',
    saved: 'Modifiche salvate',
    saving: 'Salvataggio…',
    error: 'Errore',
    playerUnsupported:
      'Il browser non può riprodurre questo formato, ma la trascrizione è disponibile.',
    emptyTranscript: 'Nessun testo trascritto.',
    footerNote: 'i tuoi file restano sul tuo computer',
    retry: 'Riprova',
    close: 'Chiudi',
  },
  en: {
    tagline: 'Local transcription of audio and video files',
    dropHere: 'Drop an audio or video file here',
    orClick: 'or click to choose one',
    language: 'Language',
    autoDetect: 'Detect automatically',
    model: 'Model',
    modelHint: 'tiny = fast · large-v3 = accurate',
    maxSize: 'Max size',
    demoBanner: 'DEMO mode active: outputs are not real transcriptions.',
    jobs: 'Jobs',
    noJobs: 'No jobs yet. Upload a file to start.',
    statusQueued: 'Queued',
    statusProcessing: 'Processing',
    statusDone: 'Completed',
    statusFailed: 'Failed',
    delete: 'Delete',
    confirmDelete: 'Delete this job and its files?',
    backToList: '← All jobs',
    editHint:
      'Click a text to correct it. Click a timestamp to jump playback.',
    save: 'Save changes',
    saved: 'Changes saved',
    saving: 'Saving…',
    error: 'Error',
    playerUnsupported:
      'The browser cannot play this format, but the transcript is available.',
    emptyTranscript: 'No transcribed text.',
    footerNote: 'your files stay on your computer',
    retry: 'Retry',
    close: 'Close',
  },
}

export function formatTime(seconds) {
  const total = Math.max(0, Math.floor(seconds))
  const h = Math.floor(total / 3600)
  const m = Math.floor((total % 3600) / 60)
  const s = total % 60
  const mm = String(m).padStart(2, '0')
  const ss = String(s).padStart(2, '0')
  return h > 0 ? `${h}:${mm}:${ss}` : `${mm}:${ss}`
}
