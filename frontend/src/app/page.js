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
  const [chatHistory, setChatHistory] = useState([]);
  const [randomQuestions, setRandomQuestions] = useState([]);

  let predefinedQuestions = "";

  const chatAreaRef = useRef(null);
  const OLLAMA_BASE_URL = "http://localhost:11434";
  const MODEL_NAME = "llama2";

  const sendQuestion = async () => {
    setLoading(true);
    const query = question ? question : predefinedQuestions;
    try {
      const askResponse = await axios.post(
        "http://localhost:3003/ask",
        { question: query },
        { headers: { "Content-Type": "application/json" } }
      );
      const initialAnswer = askResponse.data.answer;

      const newResponse = {
        question: query,
        initialAnswer: initialAnswer,
        finalAnswer: "",
      };

      setChatHistory((prevHistory) => [...prevHistory, query]);
      setResponses((prevResponses) => [...prevResponses, newResponse]);

      const latestIndex = responses.length;

      const messages = [
        ...(chatHistory.map((chat) => ({
          role: "system",
          content: `[INST]<Previous conversation>This is your previous conversation with the user. \
            User has asked "${chat}" and you answered "${finalAnswer}".</Previous conversation>[/INST]`,
        }))),
        {
          role: "system",
          content: `[INST]You are an intelligent assistant. \
          Do not give long answers. \
          Do not make up an answer. \
          Do not start with unnecessary greetings or introductions. \
          You will only use the <Previous conversation> to enhance your answer . \
          You will answer the following question using the provided answer: \
          User question: ${query}. 
          Provided answer: ${initialAnswer}.
          At the end of your answer, ask the user if they have any more questions. \
          [/INST]`,
        }
      ];

      console.log("messages", messages);

      setFinalAnswer("");

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
            setFinalAnswer(
              (prevAnswer) => (prevAnswer || "") + message?.message.content
            );
          }
        }
        result = lines[lines.length - 1];
      }

      setLoading(false);
      setQuestion("");
      predefinedQuestions = "";
    } catch (error) {
      console.error("Error sending question:", error);
      setLoading(false);
      setQuestion("");
      predefinedQuestions = "";
    }
  };

  const updateStatus = (index) => {
    setStatus((prevStatus) => ({ ...prevStatus, [index]: true }));
  };

  const fetchRandomQuestions = async () => {
    try {
      const response = await axios.get("http://localhost:3003/getQuestions");
      setRandomQuestions(response.data.questions);
    } catch (error) {
      console.error("Error fetching random questions:", error);
    }
  };

  useEffect(() => {
    fetchRandomQuestions();
  }, [loading]);

  useEffect(() => {
    if (chatAreaRef.current) {
      chatAreaRef.current.scrollTop = chatAreaRef.current.scrollHeight;
    }
  }, [responses, finalAnswer]);

  const click_and_chat = (question) => {
    if (loading) return;
    predefinedQuestions = question;
    sendQuestion();
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Lizard Global Chatbot</h1>
      <div className={styles.questionsBox}>
        <p className={styles.questionText}>
          Not sure what to ask? You can pick a question here:
        </p>

        <div className={styles.questionButtons}>
            {randomQuestions &&
              randomQuestions.map((randomQuestion, index) => (
                <button
                  key={index}
                  onClick={() => click_and_chat(randomQuestion)}
                  className={styles.questionButton}
                >
                  {randomQuestion}
                </button>
              ))}
          </div>
      </div>
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
