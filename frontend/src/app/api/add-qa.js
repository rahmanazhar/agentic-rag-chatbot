// pages/api/add-qa.js
import axios from 'axios';

export default async function handler(req, res) {
    if (req.method === 'POST') {
        const { question, answer } = req.body;

        try {
            const response = await axios.post('http://localhost:5000/add-qa', { question, answer });
            res.status(200).json({ message: response.data.message });
        } catch (error) {
            res.status(500).json({ error: 'Failed to add question and answer' });
        }
    } else {
        res.status(405).json({ error: 'Method not allowed' });
    }
}
