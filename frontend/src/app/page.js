"use client";

import { useState } from 'react';
import axios from 'axios';
import styles from './page.module.css';

export default function Home() {
    const [message, setMessage] = useState('');
    const [response, setResponse] = useState('');

    const sendMessage = async () => {
        setResponse(''); // Clear previous response
        try {
            const res = await axios.post('http://localhost:3003/chat', { message });
            const eventSource = new EventSource('http://localhost:3003/chat-stream');

            eventSource.onmessage = (event) => {
                setResponse((prev) => prev + event.data);
            };

            eventSource.onerror = () => {
                eventSource.close();
            };
        } catch (error) {
            console.error("Error sending message:", error);
        }
    };

    return (
        <div className={styles.container}>
            <h1 className={styles.title}>Chatbot</h1>
            <div className={styles.inputContainer}>
                <input 
                    type="text" 
                    value={message} 
                    onChange={(e) => setMessage(e.target.value)} 
                    className={styles.input}
                    placeholder="Type your message..."
                />
                <button onClick={sendMessage} className={styles.button}>Send</button>
            </div>
            <div className={styles.response}>{response}</div>
        </div>
    );
}
