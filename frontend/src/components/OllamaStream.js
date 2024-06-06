import { useEffect, useState } from "react";

const OllamaStream = ({ messages }) => {
  const [responses, setResponses] = useState("");

  const OLLAMA_BASE_URL = "http://localhost:11434";
  const MODEL_NAME = "llama2";
  useEffect(() => {
    const fetchResponses = async () => {
      const url = `${OLLAMA_BASE_URL}/api/chat`;
      const headers = { "Content-Type": "application/json" };
      const payload = {
        model: MODEL_NAME,
        messages: messages,
        stream: true,
        temperature: 1.0,
        max_tokens: 512,
      };

      try {
        const response = await fetch(url, {
          method: "POST",
          headers: headers,
          body: JSON.stringify(payload),
        });

        const reader = response.body.getReader();
        let result = "";
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          const chunk = new TextDecoder("utf-8").decode(value);
          result += chunk;
          const lines = result.split("\n");
          if (lines.length > 1) {
            lines.slice(0, -1).forEach((line) => {
              const data = JSON.parse(line);
              console.log(data);
              setResponses((prevResponses) => prevResponses + data.message.content.replace(/"/g, ""));
            });
            result = lines.slice(-1)[0];
          }
        }
      } catch (error) {
        console.error("Error streaming data from Ollama:", error);
      }
    };

    fetchResponses();
  }, [messages]);

  return (
    <div>
      {responses && <div>{responses}</div>}
    </div>
  );
};

export default OllamaStream;
