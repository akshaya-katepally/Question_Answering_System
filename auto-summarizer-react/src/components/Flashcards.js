import React, { useEffect, useRef, useState } from 'react';
import './Flashcards.css';
import * as THREE from 'three';
import HALO from 'vanta/dist/vanta.halo.min';
import axios from 'axios';

const Flashcards = () => {
  const vantaRef = useRef(null);
  const [file, setFile] = useState(null);
  const [summary, setSummary] = useState([]);

  useEffect(() => {
    const vantaEffect = HALO({
      el: vantaRef.current,
      mouseControls: true,
      touchControls: true,
      gyroControls: false,
      minHeight: 200.00,
      minWidth: 200.00,
      scale: 1.00,
      scaleMobile: 1.00,
      THREE
    });

    return () => {
      if (vantaEffect) vantaEffect.destroy();
    };
  }, []);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:5001/uploads', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      setSummary(response.data.summary);
    } catch (error) {
      console.error('Error uploading file:', error);
    }
  };

  return (
    <div className="flashcards-container">
      <div ref={vantaRef} className="vanta-background"></div>
      <div className="flashcards-content">
        <h1>Flashcards</h1>
        <p>Create and review your flashcards here...</p>
        <form onSubmit={handleSubmit}>
          <input type="file" onChange={handleFileChange} />
          <button type="submit">Generate Flashcards</button>
        </form>
        {summary.length > 0 && (
          <div className="summary">
            <h2>Flashcards</h2>
            {summary.map((point, index) => (
              <div key={index} className="card">
                <p>{point}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Flashcards;
