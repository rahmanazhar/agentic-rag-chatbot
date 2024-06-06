"use client";
import { useState, useRef, useEffect } from "react";
import axios from "axios";
import styles from "./page.module.css";
import OllamaStream from "@/components/OllamaStream";

export default function Home() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [responses, setResponses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [latestIndex, setLatestIndex] = useState(null);

  const chatAreaRef = useRef(null);
  const sendQuestion = async () => {
    setLoading(true);
    try {
      const response = await axios.post(
        "http://localhost:3003/ask",
        { question },
        { headers: { "Content-Type": "application/json" } }
      );

      const message = {
        role: "system",
        content:
          "You are a helpful assistant for Lizard Global.\
                  Lizard Global is the best software company development in Malaysia and Netherlands.\
                  You will answer the following question using the provided answer:\
                  Question: " + question + " Answer: " + response.data.answer + "\
                  Please use this answer to answer the question.\
                  Keep the conversation going by asking user related questions.",
      };

      setResponses((prevResponses) => [
        ...prevResponses,
        { question: question, answer: message },
      ]);
      setLatestIndex(responses.length);

      setLoading(false);
      setQuestion("");
    } catch (error) {
      console.error("Error sending question:", error);
      setLoading(false);
      setQuestion("");
    }
  };

  useEffect(() => {
    chatAreaRef.current.scrollTop = chatAreaRef.current.scrollHeight;
  }, [responses]);

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Agentic RAG Chatbot</h1>
      <div ref={chatAreaRef} className={styles.responses}>
        {responses.map((response, index) => (
          <div key={index} className={styles.responseDiv}>
            <div key={index + "_question"} className={styles.response}>
              <div className={styles.question}>{response.question}</div>
            </div>
            <div key={index + "_answer"} className={styles.responseAnswer}>
            {latestIndex === index && <OllamaStream messages={[response.answer]} /> }
            </div>
          </div>
        ))}

        {loading && <span className={styles.loadingDot}>...</span>}
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
