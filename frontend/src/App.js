import React, { useState } from "react";
import { ReactMediaRecorder } from "react-media-recorder";


function App() {
  const [resume, setResume] = useState(null);
  const [jobDesc, setJobDesc] = useState(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [feedback, setFeedback] = useState("");
  const [history, setHistory] = useState([]);
  const [resumeInsights, setResumeInsights] = useState(null);

  const uploadFile = async (file, endpoint) => {
    const formData = new FormData();
    formData.append("file", file);
    await fetch(`http://localhost:8000/${endpoint}`, {
      method: "POST",
      body: formData,
    });
  };

  const startInterview = async () => {
    await fetch("http://localhost:8000/interview/start");
    alert("Interview started. Now click 'Next Question'");
    setHistory([]);
    setFeedback("");
    setQuestion("");
    setAnswer("");
  };

  const getQuestion = async () => {
    const res = await fetch("http://localhost:8000/interview/next");
    const data = await res.json();
    setQuestion(data.question);
    setAnswer("");
    setFeedback("");
  };

  const submitAnswer = async () => {
    const res = await fetch("http://localhost:8000/interview/answer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ answer }),
    });
    const data = await res.json();

    let fullFeedback = `Score: ${data.score || data.overall_score}\n`;

    if (data.rubric) {
      fullFeedback += `Rubric Scores:\n`;
      fullFeedback += `  Relevance: ${data.rubric.relevance}\n`;
      fullFeedback += `  Technical Accuracy: ${data.rubric.technical_accuracy}\n`;
      fullFeedback += `  Clarity: ${data.rubric.clarity}\n`;
      fullFeedback += `  Job Alignment: ${data.rubric.job_alignment}\n`;
    }

    fullFeedback += `\nFeedback: ${data.feedback}`;
    setFeedback(fullFeedback);
    const coachingText = (data.coaching || "").replace(/^Coaching Tips:\s*/i, "");

    setHistory((prev) => [
      ...prev,
      {
        question,
        answer,
        feedback: fullFeedback,
        score: data.score || data.overall_score,
        coaching: coachingText,
      },
    ]);

    setQuestion("");
    setAnswer("");
  };

  const handleAnalyzeResume = async () => {
    try {
      const res = await fetch("http://localhost:8000/resume/insights");
      const data = await res.json();
      setResumeInsights(data);
    } catch (err) {
      console.error("Failed to fetch resume insights", err);
    }
  };

  const speakFromServer = async (text) => {
  const res = await fetch("http://localhost:8000/tts", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text })
  });

  if (!res.ok) {
    console.error("Failed to fetch TTS audio:", res.statusText);
    return;
  }

  const blob = await res.blob();
  const audioUrl = URL.createObjectURL(blob);
  const audio = new Audio(audioUrl);
  audio.play().catch((err) => {
    console.error("Playback error:", err);
  });
};


  

const VoiceRecorder = ({ onTranscribe }) => {
  const handleStop = async (blobUrl) => {
    console.log("Recording finished. Fetching blob from", blobUrl);
    const res = await fetch(blobUrl);
    const blob = await res.blob();

    if (blob.size < 1000) {
      alert("Recording too short or failed.");
      return;
    }

    const file = new File([blob], "recording.webm", { type: blob.type });
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch("http://localhost:8000/interview/transcribe", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();
    if (data.transcript) {
      onTranscribe(data.transcript);
    } else {
      alert("Transcription failed: " + (data.error || "no transcript returned"));
    }
  };

  return (
    <ReactMediaRecorder
      audio
      onStop={handleStop}
      render={({ status, startRecording, stopRecording }) => (
        <div>
          <p>Status: {status}</p>
          <button onClick={startRecording}>🎤 Start</button>
          <button onClick={stopRecording}>📤 Stop & Transcribe</button>
        </div>
      )}
    />
  );
};




  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h2>AI Interview Agent</h2>

      <div>
        <p>Upload Resume (PDF):</p>
        <input
          type="file"
          onChange={(e) => {
            setResume(e.target.files[0]);
            uploadFile(e.target.files[0], "upload-resume/");
          }}
        />
      </div>

      <div>
        <p>Upload Job Description (txt):</p>
        <input
          type="file"
          onChange={(e) => {
            setJobDesc(e.target.files[0]);
            uploadFile(e.target.files[0], "upload-jd/");
          }}
        />
      </div>

      <div style={{ marginTop: "1rem" }}>
        <button onClick={startInterview}>Start Interview</button>
        <button onClick={getQuestion} style={{ marginLeft: "10px" }}>
          Next Question
        </button>
        <button onClick={handleAnalyzeResume} style={{ marginLeft: "10px" }}>
          Analyze Resume Insights
        </button>
      </div>

      {resumeInsights && (
        <div style={{ marginTop: "2rem", padding: "1rem", border: "1px solid #ccc", borderRadius: "8px" }}>
          <h4>Resume Insights</h4>
          <p><strong>Hard Skills:</strong> {resumeInsights.hard_skills || "N/A"}</p>
          <p><strong>Soft Skills:</strong> {resumeInsights.soft_skills || "N/A"}</p>
          <p><strong>Experience Summary:</strong> {resumeInsights.experience_summary}</p>
          <p><strong>Behavioral Traits:</strong> {resumeInsights.behavioral_traits}</p>
        </div>
      )}

      {question && (
        <div style={{ marginTop: "2rem" }}>
          <h4>Question:</h4>
          <p>{question}</p>
          <button onClick={() => speakFromServer(question)}>🔊 Play Question</button>
          <br /><br />
          <textarea
            rows={4}
            cols={80}
            placeholder="Your answer..."
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
          />
          <br />
          <button onClick={submitAnswer}>Submit Answer</button>
          <VoiceRecorder onTranscribe={(transcript) => setAnswer(transcript)} />
        </div>
      )}

      {feedback && (
        <div style={{ marginTop: "2rem" }}>
          <h4>Feedback:</h4>
          <pre>{feedback}</pre>
          <button onClick={() => speakFromServer(feedback)}>🔊 Play Feedback</button>
        </div>
      )}

      {history.length > 0 && (
        <div style={{ marginTop: "2rem" }}>
          <h4>Answer History:</h4>
          <ul>
            {history.map((item, idx) => (
              <li key={idx} style={{ marginBottom: "1.5rem" }}>
                <strong>Q{idx + 1}:</strong> {item.question}<br />
                <strong>Your Answer:</strong> {item.answer}<br />
                <strong>Score:</strong> {item.score}<br />
                <strong>Feedback:</strong>
                <pre>{item.feedback}</pre>
                {item.coaching && (
                  <>
                    <strong>Coaching Tips:</strong>
                    <pre>{item.coaching}</pre>
                  </>
                )}
                <hr />
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;
