"use client";
import { useState, useRef, useEffect } from "react";
import axios from "axios";
import styles from "./page.module.css";
import OllamaStream from "@/components/OllamaStream";

export default function Home() {
  const [question, setQuestion] = useState("");
  const [responses, setResponses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState({});
  const [finalAnswer, setFinalAnswer] = useState("");

  const chatAreaRef = useRef(null);
  const OLLAMA_BASE_URL = "http://localhost:11434";
  const MODEL_NAME = "llama2";

  const sendQuestion = async () => {
    setLoading(true);
    try {
      const askResponse = await axios.post(
        "http://localhost:3003/ask",
        { question },
        { headers: { "Content-Type": "application/json" } }
      );
      const initialAnswer = askResponse.data.answer;

      const newResponse = {
        question: question,
        initialAnswer: initialAnswer,
        finalAnswer: "",
      };

      setResponses((prevResponses) => [...prevResponses, newResponse]); 
      setFinalAnswer("");

      const latestIndex = responses.length;

      const messages = [
        {
          role: "system",
          content: `You are an assistant for Lizard Global. \
          Lizard Global is the best software company development in Malaysia and Netherlands. \
          You will answer the following user question using the provided answer: \
          Question: ${question} Answer: ${initialAnswer} \
          Follow these rules: \
          1. Repeat this answer to answer the question. This answer is absolutely correct. \
          2. If you don't know the answer, just say that you don't know. \
          3. Do not make up an answer. \
          4. if the question is about the price, use the price answer without changing the answer. \
          5. Do not start with "Of course! I'd be happy to help you" or "I'm sorry I can't help you"`,
        },
      ];

      const url = `${OLLAMA_BASE_URL}/api/chat`;
      const headers = { "Content-Type": "application/json" };
      const payload = {
        model: MODEL_NAME,
        messages: messages,
        stream: true,
        temperature: 1.0,
        max_tokens: 512,
      };

      const response = await fetch(url, {
        method: "POST",
        headers: headers,
        body: JSON.stringify(payload),
      });

      const reader = response.body.getReader();
      let result = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          updateStatus(latestIndex);
          break;
        }
        const chunk = new TextDecoder("utf-8").decode(value);
        result += chunk;
        const lines = result.split("\n");
        for (let i = 0; i < lines.length - 1; i++) {
          if (lines[i].trim() !== "") {
            const message = JSON.parse(lines[i]);
            setFinalAnswer((prevAnswer) => (prevAnswer || "") + message?.message.content);
          }
        }
        result = lines[lines.length - 1];
      }

      setLoading(false);
      setQuestion("");
    } catch (error) {
      console.error("Error sending question:", error);
      setLoading(false);
      setQuestion("");
    }
  };

  const updateStatus = (index) => {
    setStatus((prevStatus) => ({ ...prevStatus, [index]: true }));
  };

  useEffect(() => {
    if (chatAreaRef.current) {
      chatAreaRef.current.scrollTop = chatAreaRef.current.scrollHeight;
    }
  }, [responses, finalAnswer]);

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
              <OllamaStream
                finalAnswer={finalAnswer}
                index={index}
                status={status}
                updateStatus={updateStatus}
              />
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
          {loading ? "Thinking..." : "Send"}
        </button>
      </div>
    </div>
  );
}
