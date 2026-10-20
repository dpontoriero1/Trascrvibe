import React, { useCallback, useEffect, useRef, useState } from 'react'
import { STRINGS } from './i18n.js'
import UploadForm from './components/UploadForm.jsx'
import JobList from './components/JobList.jsx'
import JobDetail from './components/JobDetail.jsx'

const API = '/api'

async function api(path, options) {
  const response = await fetch(`${API}${path}`, options)
  if (!response.ok) {
    let message = `HTTP ${response.status}`
    try {
      const body = await response.json()
      if (body.detail) {
        message = body.detail.message_it || body.detail.message_en || body.detail
      }
    } catch {
      // risposta non JSON
    }
    throw new Error(message)
  }
  if (response.status === 204) return null
  return response.json()
}

export default function App() {
  const [lang, setLang] = useState(() => localStorage.getItem('trsvLang') || 'it')
  const [config, setConfig] = useState(null)
  const [jobs, setJobs] = useState([])
  const [selectedId, setSelectedId] = useState(null)
  const [uploadError, setUploadError] = useState(null)
  const t = useCallback((key) => STRINGS[lang][key] || STRINGS.it[key] || key, [lang])

  useEffect(() => {
    localStorage.setItem('trsvLang', lang)
    document.documentElement.lang = lang
  }, [lang])

  const refreshJobs = useCallback(async () => {
    try {
      setJobs(await api('/jobs'))
    } catch {
      // server non raggiungibile: si riprova al prossimo tick
    }
  }, [])

  useEffect(() => {
    api('/config').then(setConfig).catch(() => {})
    refreshJobs()
  }, [refreshJobs])

  useEffect(() => {
    const timer = setInterval(() => {
      if (!selectedId) refreshJobs()
    }, 2000)
    return () => clearInterval(timer)
  }, [refreshJobs, selectedId])

  const handleUpload = useCallback(
    async (file, language, model) => {
      setUploadError(null)
      const formData = new FormData()
      formData.append('file', file)
      formData.append('language', language)
      formData.append('model', model)
      try {
        await api('/jobs', { method: 'POST', body: formData })
        await refreshJobs()
      } catch (err) {
        setUploadError(err.message)
      }
    },
    [refreshJobs],
  )

  const handleDelete = useCallback(
    async (jobId) => {
      await api(`/jobs/${jobId}`, { method: 'DELETE' })
      setSelectedId(null)
      refreshJobs()
    },
    [refreshJobs],
  )

  const selectedJob = jobs.find((j) => j.id === selectedId)

  if (selectedJob) {
    return (
      <JobDetail
        job={selectedJob}
        t={t}
        lang={lang}
        onBack={() => setSelectedId(null)}
        onDelete={() => handleDelete(selectedJob.id)}
        api={api}
      />
    )
  }

  return (
    <div className="app">
      <header className="topbar">
        <h1 className="brand">Trascrvibe</h1>
        <div className="lang-switch">
          <button
            className={lang === 'it' ? 'active' : ''}
            onClick={() => setLang('it')}
          >
            IT
          </button>
          <button
            className={lang === 'en' ? 'active' : ''}
            onClick={() => setLang('en')}
          >
            EN
          </button>
        </div>
      </header>
      {config?.is_demo && (
        <div className="banner banner-demo">{t('demoBanner')}</div>
      )}
      <main className="container">
        <UploadForm t={t} config={config} onUpload={handleUpload} />
        {uploadError && <div className="banner banner-error">{uploadError}</div>}
        <JobList t={t} jobs={jobs} onSelect={setSelectedId} />
      </main>
    </div>
  )
}
