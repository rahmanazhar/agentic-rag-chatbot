"use client";
import { useState } from "react";
import axios from "axios";
import styles from "./page.module.css";

export default function Home() {
  const [question, setQuestion] = useState("");
  const [responses, setResponses] = useState([]);

  const sendQuestion = async () => {
    try {
      const response = await axios.post(
        "http://localhost:3003/ask",
        { question },
        { headers: { "Content-Type": "application/json" } }
      );

      setResponses((prevResponses) => [...prevResponses, response.data.answer]);
    } catch (error) {
      console.error("Error sending question:", error);
    }

    setQuestion("");
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Agentic RAG Chatbot</h1>
      <div className={styles.inputContainer}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          className={styles.input}
          placeholder="Type your question..."
        />
        <button onClick={sendQuestion} className={styles.button}>
          Send
        </button>
      </div>
      <div className={styles.responses}>
        {responses.map((response, index) => (
          <div key={index} className={styles.response}>
            {response}
          </div>
        ))}
      </div>
    </div>
  );
}
