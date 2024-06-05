"use client";
import { useState } from "react";
import axios from "axios";
import styles from "./page.module.css";

export default function Home() {
  const [question, setQuestion] = useState("");
  const [responses, setResponses] = useState([]);
  const [loading, setLoading] = useState(false);

  const sendQuestion = async () => {
    setLoading(true);
    try {
      const response = await axios.post(
        "http://localhost:3003/ask",
        { question },
        { headers: { "Content-Type": "application/json" } }
      );

      setResponses((prevResponses) => [
        ...prevResponses,
        { question, answer: response.data.answer },
      ]);
    } catch (error) {
      console.error("Error sending question:", error);
    }

    setLoading(false);
    setQuestion("");
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Agentic RAG Chatbot</h1>
      <div className={styles.responses}>
        {responses.map((response, index) => (
          <div key={index} className={styles.response}>
            <div className={styles.question}>{response.question}</div>
            <div className={styles.answer}>
              {response.answer.replace(/\*/g, "\n\n")}
            </div>
          </div>
        ))}
      </div>
      <div className={styles.inputContainer}>
        <textarea
          rows={2}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          className={styles.input}
          placeholder="Type your question..."
        />
        <button
          onClick={sendQuestion}
          className={styles.button}
          disabled={loading}
        >
          {loading ? "Sending..." : "Send"}
        </button>
      </div>
    </div>
  );
}
