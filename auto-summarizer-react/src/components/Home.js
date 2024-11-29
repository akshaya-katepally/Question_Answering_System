// import React from 'react';
// import { Link } from 'react-router-dom';
// import './Home.css';
// import summarizerImage from '../images/summarizer-image.png';
// import qnaGeneratorImage from '../images/qna-generator-image.png';
// import flashcardsImage from '../images/flashcards-image.png';

// const Home = () => {
//   return (
//     <div className="home">
//       <div className="video-container">
//         <video autoPlay loop muted>
//           <source src="/video.mp4" type="video/mp4" />
//         </video>
//       </div>

//       <div className="options-container">
//         <Link to="/summarizer" className="option summarizer">
//           <div className="content">
//             <h2>Summarizer</h2>
//             <p>Quickly summarize text with ease.</p>
//           </div>
//           <img src={summarizerImage} alt="Summarizer" />
//         </Link>

//         <Link to="/qandagenerator" className="option qna-generator">
//           <img src={qnaGeneratorImage} alt="Q&A Generator" />
//           <div className="content">
//             <h2>Q&A Generator</h2>
//             <p>Generate questions and answers effortlessly.</p>
//           </div>
//         </Link>

//         <Link to="/flashcards" className="option flashcards">
//           <div className="content">
//             <h2>Flashcards</h2>
//             <p>Create flashcards for effective learning.</p>
//           </div>
//           <img src={flashcardsImage} alt="Flashcards" />
//         </Link>
//       </div>
//     </div>
//   );
// };

// export default Home;

import React, { useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import './Home.css';
import summarizerImage from '../images/summarizer-image.png';
import qnaGeneratorImage from '../images/qna-generator-image.png';
import flashcardsImage from '../images/flashcards-image.png';

const Home = () => {
  const optionsRef = useRef([]);

  useEffect(() => {
    const options = {
      threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
        } else {
          entry.target.classList.remove('visible');
        }
      });
    }, options);

    optionsRef.current.forEach(option => {
      if (option) {
        observer.observe(option);
      }
    });

    return () => {
      optionsRef.current.forEach(option => {
        if (option) {
          observer.unobserve(option);
        }
      });
    };
  }, []);

  return (
    <div className="home">
      <div className="video-container">
        <video autoPlay loop muted>
          <source src="/video.mp4" type="video/mp4" />
        </video>
      </div>

      <div className="options-container">
        <Link to="/summarizer" className="option summarizer" ref={el => optionsRef.current[0] = el}>
          <div className="content">
            <h2>Summarizer</h2>
            <p>Uncover the essence of any text in seconds! Our Summarizer transforms mountains of information into sleek, insightful summaries, perfect for the fast-paced learner.</p>
          </div>
          <img src={summarizerImage} alt="Summarizer" />
        </Link>

        <Link to="/qandagenerator" className="option qna-generator" ref={el => optionsRef.current[1] = el}>
          <img src={qnaGeneratorImage} alt="Q&A Generator" />
          <div className="content">
            <h2>Q&A Generator</h2>
            <p>Unlock knowledge with ease! Our Q&A Generator crafts engaging questions and precise answers, turning complex subjects into interactive learning adventures.</p>
          </div>
        </Link>

        <Link to="/flashcards" className="option flashcards" ref={el => optionsRef.current[2] = el}>
          <div className="content">
            <h2>Flashcards</h2>
            <p>Boost your brainpower with style! Dive into learning with our Flashcards, designed for effortless retention and mastery. Study smarter, not harder!</p>
          </div>
          <img src={flashcardsImage} alt="Flashcards" />
        </Link>
      </div>
    </div>
  );
};

export default Home;
