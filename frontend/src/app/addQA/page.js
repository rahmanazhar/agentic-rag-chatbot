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
        const response = await axios.post('http://localhost:3003/add-qa', {
            question,
            answer
        });
        alert(response.data.message);
        setQuestion('');
        setAnswer('');
    } catch (error) {
        console.error(error);
        alert('Error adding question and answer');
    }
  };

  return (
    <div className={styles.fullScreen}>
      <div className={styles.container}>
        <h1 className={styles.title}>Add Question and Answer</h1>
        <form onSubmit={handleSubmit}>
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
          <button type="submit" className={styles.button}>
            Submit
          </button>
        </form>
      </div>
    </div>
  );
}
