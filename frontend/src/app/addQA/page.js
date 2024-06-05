"use client";
import { useState } from "react";
import axios from "axios";
import styles from "./page.module.css";

export default function AddQA() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      await axios.post("http://localhost:3003/add-qa", {
        question,
        answer,
      });
      alert("Question and answer added successfully!");
      setQuestion("");
      setAnswer("");
    } catch (error) {
      console.error("Error adding question and answer:", error);
    }
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Add Question and Answer</h1>
        <div className={styles.formGroup}>
          <label htmlFor="question" className={styles.label}>
            Question:
          </label>
          <input
            id="question"
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            className={styles.input}
          />
        </div>
        <div className={styles.formGroup}>
          <label htmlFor="answer" className={styles.label}>
            Answer:
          </label>
          <input
            id="answer"
            type="text"
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            className={styles.input}
          />
        </div>
        <button type="submit" className={styles.button} onClick={handleSubmit}>
          Submit
        </button>
    </div>
  );
}
