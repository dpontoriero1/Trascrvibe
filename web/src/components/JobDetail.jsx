import React, { useEffect, useRef, useState } from 'react'
import { formatTime, isPlayable } from '../i18n.js'

export default function JobDetail({ job, t, lang, onBack, onDelete, api }) {
  const [segments, setSegments] = useState(job.segments || [])
  const [saveState, setSaveState] = useState('')
  const [error, setError] = useState('')
  const playerRef = useRef(null)
  const [activeIdx, setActiveIdx] = useState(-1)

  useEffect(() => {
    let cancelled = false
    const load = async () => {
      try {
        const data = await api(`/jobs/${job.id}`)
        if (cancelled) return
        setSegments(data.segments || [])
      } catch {
        /* polling: si riprova */
      }
    }
    load()
    if (job.status === 'processing' || job.status === 'queued') {
      const timer = setInterval(load, 2000)
      return () => {
        cancelled = true
        clearInterval(timer)
      }
    }
    return () => {
      cancelled = true
    }
  }, [job.id, job.status, api])

  const playable = isPlayable(job.original_name)

  const handleTimeUpdate = () => {
    const player = playerRef.current
    if (!player) return
    const now = player.currentTime
    let idx = -1
    for (let i = 0; i < segments.length; i++) {
      if (segments[i].start <= now) idx = i
      else break
    }
    setActiveIdx(idx)
  }

  const seekTo = (start) => {
    const player = playerRef.current
    if (player) {
      player.currentTime = start
      player.play()
    }
  }

  const save = async () => {
    setSaveState('saving')
    setError('')
    try {
      await api(`/jobs/${job.id}/segments`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ segments }),
      })
      setSaveState('saved')
      setTimeout(() => setSaveState(''), 2500)
    } catch (err) {
      setError(err.message)
      setSaveState('')
    }
  }

  const updateText = (idx, text) => {
    setSegments((prev) =>
      prev.map((s, i) => (i === idx ? { ...s, text } : s)),
    )
  }

  return (
    <div className="app">
      <header className="topbar">
        <button className="back" onClick={onBack}>
          {t('backToList')}
        </button>
      </header>
      <main className="container">
        <h2>{job.original_name}</h2>
        <p className="meta">
          {job.model} · {job.language || ''}
          {job.is_demo ? ' · DEMO' : ''}
        </p>
        {job.error && <div className="banner banner-error">{job.error}</div>}
        {playable ? (
          playable === 'video' ? (
            <video
              ref={playerRef}
              controls
              src={`/api/jobs/${job.id}/media`}
              onTimeUpdate={handleTimeUpdate}
            />
          ) : (
            <audio
              ref={playerRef}
              controls
              src={`/api/jobs/${job.id}/media`}
              onTimeUpdate={handleTimeUpdate}
            />
          )
        ) : (
          <p className="hint">{t('playerUnsupported')}</p>
        )}
        {job.status === 'done' && (
          <>
            <p className="hint">{t('editHint')}</p>
            <div className="toolbar">
              <button onClick={save} disabled={saveState === 'saving'}>
                {saveState === 'saving' ? t('saving') : t('save')}
              </button>
              {saveState === 'saved' && (
                <span className="save-status">{t('saved')}</span>
              )}
            </div>
            {error && <div className="banner banner-error">{error}</div>}
            <div className="segments">
              {segments.length === 0 ? (
                <p className="empty">{t('emptyTranscript')}</p>
              ) : (
                segments.map((seg, idx) => (
                  <div
                    key={idx}
                    className={`segment${idx === activeIdx ? ' active' : ''}`}
                  >
                    <button
                      className="ts"
                      onClick={() => seekTo(seg.start)}
                      title={formatTime(seg.start)}
                    >
                      {formatTime(seg.start)}
                    </button>
                    <div
                      className="seg-text"
                      contentEditable
                      suppressContentEditableWarning
                      onBlur={(e) => updateText(idx, e.target.textContent)}
                    >
                      {seg.text}
                    </div>
                  </div>
                ))
              )}
            </div>
          </>
        )}
        <div className="danger-zone">
          <button
            className="danger"
            onClick={() => {
              if (window.confirm(t('confirmDelete'))) onDelete()
            }}
          >
            {t('delete')}
          </button>
        </div>
      </main>
    </div>
  )
}
