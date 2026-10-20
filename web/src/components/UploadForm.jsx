import React, { useRef, useState } from 'react'

const AUDIO_EXT = ['mp3', 'wav', 'm4a', 'aac', 'ogg', 'oga', 'flac', 'opus']
const VIDEO_EXT = ['mp4', 'webm', 'mov', 'mkv', 'avi', 'wmv']

export function isPlayable(filename) {
  const match = /\.([a-z0-9]+)$/i.exec(filename || '')
  const ext = match ? match[1].toLowerCase() : ''
  if (VIDEO_EXT.includes(ext)) return 'video'
  if (AUDIO_EXT.includes(ext)) return 'audio'
  return null
}

export default function UploadForm({ t, config, onUpload }) {
  const [dragging, setDragging] = useState(false)
  const [language, setLanguage] = useState('auto')
  const [model, setModel] = useState(config?.default_model || 'base')
  const [uploading, setUploading] = useState(false)
  const inputRef = useRef(null)

  const handleFile = async (file) => {
    if (!file || uploading) return
    setUploading(true)
    try {
      await onUpload(file, language, model)
    } finally {
      setUploading(false)
    }
  }

  return (
    <section className="card">
      <p className="tagline">{t('tagline')}</p>
      <div
        className={`drop-zone${dragging ? ' drag' : ''}`}
        role="button"
        tabIndex={0}
        onClick={() => inputRef.current?.click()}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') inputRef.current?.click()
        }}
        onDragOver={(e) => {
          e.preventDefault()
          setDragging(true)
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault()
          setDragging(false)
          handleFile(e.dataTransfer.files[0])
        }}
      >
        <p className="drop-main">{uploading ? '…' : t('dropHere')}</p>
        <p className="hint">{t('orClick')}</p>
      </div>
      <input
        ref={inputRef}
        type="file"
        hidden
        accept=".mp3,.wav,.m4a,.aac,.ogg,.oga,.flac,.opus,.mp4,.mkv,.mov,.avi,.webm,.wmv,.mpga"
        onChange={(e) => {
          handleFile(e.target.files[0])
          e.target.value = ''
        }}
      />
      <div className="options">
        <label>
          <span>{t('language')}</span>
          <select value={language} onChange={(e) => setLanguage(e.target.value)}>
            <option value="auto">{t('autoDetect')}</option>
            <option value="it">Italiano</option>
            <option value="en">English</option>
            <option value="es">Español</option>
            <option value="fr">Français</option>
            <option value="de">Deutsch</option>
          </select>
        </label>
        <label>
          <span>{t('model')}</span>
          <select value={model} onChange={(e) => setModel(e.target.value)}>
            {(config?.models || ['base']).map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
        </label>
      </div>
      <p className="hint">
        {t('modelHint')}
        {config ? ` · ${t('maxSize')}: ${config.max_upload_mb} MB` : ''}
      </p>
    </section>
  )
}
