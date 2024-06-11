import React from "react";
import styles from "./OllamaStream.module.css";

const OllamaStream = ({ finalAnswer, index, status, updateStatus }) => {
  const [messages, setMessages] = React.useState([]);

  React.useEffect(() => {
    if (finalAnswer && !status[index]) {
      setMessages(finalAnswer);
    }
    if (status[index]) {
      updateStatus(index);
    }
  }, [finalAnswer]);

  return (
    <div className={styles.streamContainer}>
      {messages}
      {!status[index] && <span className={styles.loadingDot}>...</span>}
    </div>
  );
};

export default OllamaStream;
