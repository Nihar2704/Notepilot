import { useState } from 'react'
import { useSummarize } from './hooks/useSummarize'

function App() {
  const [url, setUrl] = useState('')
  const { summarize, status, error, data } = useSummarize()

  const handleGenerate = () => {
    if (!url) return
    summarize(url)
  }

  return (
    <div className="min-h-screen bg-bg text-text p-8 font-sans">
      <header className="max-w-2xl mx-auto text-center mb-12">
        <h1 className="text-5xl mb-4">✈️ NotePilot</h1>
        <p className="text-muted text-xl italic font-serif">Turn any lecture into smart notes.</p>
      </header>
      
      <main className="max-w-4xl mx-auto">
        <div className="bg-surface p-8 rounded-lg shadow-sm border border-border">
          <div className="flex gap-4">
            <input 
              type="text" 
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="🔗 Paste a YouTube lecture URL..." 
              className="flex-1 p-4 bg-bg border border-border rounded-md focus:outline-none focus:border-accent"
            />
            <button 
              onClick={handleGenerate}
              disabled={status === 'processing'}
              className="bg-accent text-white px-8 py-4 rounded-md font-bold hover:brightness-110 transition-all disabled:opacity-50"
            >
              {status === 'processing' ? 'Processing...' : 'Generate Notes →'}
            </button>
          </div>
          {error && (
            <div className="mt-4 p-4 bg-red-100 border border-red-200 text-red-700 rounded-md">
              {error}
            </div>
          )}
          <p className="mt-4 text-muted text-sm text-center">
            Works with lectures, talks, tutorials, MOOCs
          </p>
        </div>

        {status === 'done' && data && (
          <div className="mt-12 space-y-12">
            <section className="bg-surface p-8 rounded-lg border border-border shadow-sm">
              <h2 className="text-3xl mb-6 text-accent">📋 Summary</h2>
              <p className="leading-relaxed text-lg">{data.notes.summary}</p>
            </section>

            <section className="bg-surface p-8 rounded-lg border border-border shadow-sm">
              <h2 className="text-3xl mb-6 text-accent">🔑 Key Concepts</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {data.notes.key_concepts.map((concept, idx) => (
                  <div key={idx} className="p-4 bg-accent-light rounded-md">
                    <h3 className="font-bold text-accent text-xl mb-2">{concept.term}</h3>
                    <p className="text-muted">{concept.definition}</p>
                  </div>
                ))}
              </div>
            </section>

            <section className="bg-surface p-8 rounded-lg border border-border shadow-sm">
              <h2 className="text-3xl mb-6 text-accent">📝 Detailed Notes</h2>
              <div className="space-y-6">
                {data.notes.detailed_notes.map((note, idx) => (
                  <div key={idx} className="border-b border-border pb-6 last:border-0">
                    <h3 className="text-2xl font-serif mb-4">{note.section}</h3>
                    <p className="leading-relaxed whitespace-pre-wrap">{note.content}</p>
                  </div>
                ))}
              </div>
            </section>

            <section className="bg-surface p-8 rounded-lg border border-border shadow-sm">
              <h2 className="text-3xl mb-6 text-accent">💡 Takeaways</h2>
              <ul className="list-disc pl-6 space-y-3 text-lg">
                {data.notes.takeaways.map((takeaway, idx) => (
                  <li key={idx}>{takeaway}</li>
                ))}
              </ul>
            </section>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
