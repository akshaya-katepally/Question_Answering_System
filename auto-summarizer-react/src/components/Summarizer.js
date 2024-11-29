import React, { useState, useEffect, useRef } from 'react';
import './Summarizer.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPaste, faCopy, faDownload, faTrash, faFilePdf } from '@fortawesome/free-solid-svg-icons';
import * as THREE from 'three';
import BIRDS from 'vanta/dist/vanta.birds.min';

const SummarizationComponent = () => {
  const [text, setText] = useState('');
  const [summary, setSummary] = useState('');
  const [summaryLevel, setSummaryLevel] = useState('summary');
  const [pdfFiles, setPdfFiles] = useState([]);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const vantaRef = useRef(null);

  useEffect(() => {
    const vantaEffect = BIRDS({
      el: vantaRef.current,
      mouseControls: true,
      touchControls: true,
      gyroControls: false,
      minHeight: 200.00,
      minWidth: 200.00,
      scale: 1.00,
      scaleMobile: 1.00
    });

    return () => {
      if (vantaEffect) vantaEffect.destroy();
    };
  }, []);

  const handleSummarize = async () => {
    setError('');
    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append('texts', text);
      formData.append('summary_level', summaryLevel);
      pdfFiles.forEach((file) => {
        formData.append('pdf_files', file);
      });

      const response = await fetch('http://127.0.0.1:5003/summarizes', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Network response was not ok');
      }

      const data = await response.json();
      setSummary(data.summary);
    } catch (error) {
      console.error('Failed to fetch:', error.message || error);
      setError(`Error: ${error.message || error}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(summary);
  };

  const handleDownload = () => {
    const element = document.createElement('a');
    const file = new Blob([summary], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = 'summary.txt';
    document.body.appendChild(element);
    element.click();
  };

  const handlePaste = () => {
    navigator.clipboard.readText().then((clipText) => setText(clipText));
  };

  const handleClearText = () => {
    setText('');
    setPdfFiles([]);
  };

  const handleClearSummary = () => {
    setSummary('');
  };

  const handlePdfUpload = (event) => {
    const files = Array.from(event.target.files);
    setPdfFiles(files);
    setText((prevText) => {
      const fileNames = files.map(file => file.name).join(', ');
      return `${prevText}\n${fileNames}`;
    });
  };

  return (
    <div className="summarizer-container">
      <div ref={vantaRef} className="vanta-background"></div>
      <div className="summarizer-content">
        <div className="controls">
          <label>
            Summary Level:
            <select
              value={summaryLevel}
              onChange={(e) => setSummaryLevel(e.target.value)}
            >
              <option value="abstract">Abstract</option>
              <option value="summary">Summary</option>
              <option value="article">Article</option>
            </select>
          </label>
          <button onClick={handleSummarize} disabled={isLoading}>
            {isLoading ? 'Summarizing...' : 'SUMMARIZE'}
          </button>
        </div>
        <div className="content">
          <div className="text-section">
            <h3>Your text</h3>
            <textarea
              rows="20"
              cols="50"
              value={text}
              onChange={(e) => setText(e.target.value)}
            />
            <div className="input-buttons">
              <FontAwesomeIcon icon={faPaste} onClick={handlePaste} className="icon-button" />
              <FontAwesomeIcon icon={faTrash} onClick={handleClearText} className="icon-button" />
              <label htmlFor="pdf-upload" className="icon-button">
                <FontAwesomeIcon icon={faFilePdf} />
              </label>
              <input
                id="pdf-upload"
                type="file"
                accept="application/pdf"
                onChange={handlePdfUpload}
                multiple
                style={{ display: 'none' }}
              />
            </div>
          </div>
          <div className="summary-section">
            <h3>Summary</h3>
            {error && <div className="error">{error}</div>}
            <div className="summary">{summary}</div>
            <div className="output-buttons">
              <FontAwesomeIcon icon={faCopy} onClick={handleCopy} className="icon-button" />
              <FontAwesomeIcon icon={faTrash} onClick={handleClearSummary} className="icon-button" />
              <FontAwesomeIcon icon={faDownload} onClick={handleDownload} className="icon-button" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SummarizationComponent;
