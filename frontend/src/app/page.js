import { useState } from 'react';
import axios from 'axios';

export default function Home() {
    const [message, setMessage] = useState('');
    const [response, setResponse] = useState('');

    const sendMessage = async () => {
        const res = await axios.post('http://localhost:5000/chat', { message });
        setResponse(res.data.response);
    };

    return (
        <div>
            <h1>Chatbot</h1>
            <input 
                type="text" 
                value={message} 
                onChange={(e) => setMessage(e.target.value)} 
            />
            <button onClick={sendMessage}>Send</button>
            <div>{response}</div>
        </div>
    );
}
