import { useState, useEffect } from 'react';

const API_BASE_URL = 'http://localhost:8000';

export function useSummarize() {
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  const summarize = async (url) => {
    setJobId(null);
    setStatus('processing');
    setError(null);
    setData(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/summarize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to start summarization');
      }

      const { job_id } = await response.json();
      setJobId(job_id);
    } catch (err) {
      setError(err.message);
      setStatus('error');
    }
  };

  useEffect(() => {
    if (!jobId || status === 'done' || status === 'error') return;

    const pollStatus = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/status/${jobId}`);
        const result = await response.json();

        if (result.status === 'done') {
          setData(result.data);
          setStatus('done');
        } else if (result.status === 'error') {
          setError(result.message);
          setStatus('error');
        } else {
          setStatus(result.status);
          // Update the job step/progress if needed for UI
        }
      } catch (err) {
        console.error('Polling error:', err);
      }
    };

    const interval = setInterval(pollStatus, 2000);
    return () => clearInterval(interval);
  }, [jobId, status]);

  return { summarize, status, error, data, jobId };
}
