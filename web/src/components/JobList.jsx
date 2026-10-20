import React from 'react'

export default function JobList({ t, jobs, onSelect }) {
  const statusKey = {
    queued: 'statusQueued',
    processing: 'statusProcessing',
    done: 'statusDone',
    failed: 'statusFailed',
  }

  return (
    <section>
      <h2>{t('jobs')}</h2>
      {jobs.length === 0 ? (
        <p className="empty">{t('noJobs')}</p>
      ) : (
        <ul className="job-list">
          {jobs.map((job) => (
            <li
              key={job.id}
              className={`job-card status-${job.status}`}
              onClick={() => onSelect(job.id)}
            >
              <strong>{job.original_name}</strong>
              <span className="badge">
                {t(statusKey[job.status] || job.status)}
              </span>
              <span className="meta">
                {job.model} · {job.language || ''}
                {job.is_demo ? ' · DEMO' : ''}
              </span>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
