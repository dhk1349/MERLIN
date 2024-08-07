import React from 'react';
import { useState, useEffect, useRef } from "react";
import styles from './Chat.module.css';
import { checkQuestionStatus, retrieveChatLog } from './Api';

function Chat({ isOpen, onClose, conversation, setConversation, setResult }) {
    const [newMessage, setNewMessage] = useState('');
    const [pollingActive, setPollingActive] = useState(false);
    const lastMessageRef = useRef(null);  // Reference to track the last message
    const intervalRef = useRef(null);     // Reference to track the interval ID

    useEffect(() => {
        if (isOpen) {
            // When the modal is opened, activate polling
            setPollingActive(true);
        } else {
            // Stop polling when the modal is closed
            setPollingActive(false);
        }
    }, [isOpen]);

    useEffect(() => {
        const pollQuestionStatus = async () => {
            const sessionId = window.sessionStorage.getItem("merlin_session_id");
            if (!sessionId) return;

            try {
                const statusData = await checkQuestionStatus(sessionId);

                if (statusData.status === "complete") {
                    // Fetch the chat log if the question generation is complete
                    const chatData = await retrieveChatLog(sessionId);

                    if (statusData.status === "complete" && chatData.chatlog.length > 0) {
                        // Get the last message from the chat log
                        const lastMessage = chatData.chatlog[chatData.chatlog.length - 1];
                        const lastMessageText = lastMessage.parts.map(part => part.text).join(' ');

                        // Check if the last message is different from the one already processed
                        if (lastMessageText !== lastMessageRef.current) {
                            setConversation(prevConversation => [
                                ...prevConversation,
                                {
                                    role: lastMessage.role === 'model' ? 'MERLIN' : 'You',
                                    message: lastMessageText
                                }
                            ]);
                            lastMessageRef.current = lastMessageText; // Update the last processed message
                        }

                        setPollingActive(false); // Stop polling once complete

                    } else {
                        console.log(statusData.status, chatData.chatlog.length);
                    }
                }
            } catch (error) {
                console.log(error);
                console.error("Error during status polling:", error);
            }
        };

        if (pollingActive) {
            intervalRef.current = setInterval(pollQuestionStatus, 2000); // Poll every 2 seconds
        }

        return () => {
            if (intervalRef.current) {
                clearInterval(intervalRef.current); // Clear interval on unmount or when polling stops
            }
        };
    }, [pollingActive, conversation]);  // Remove setConversation from dependency array


    const handleSubmit = async (e) => {
        e.preventDefault();
        if (newMessage.trim() !== '') {
            const updatedConversation = [
                ...conversation,
                { role: 'You', message: newMessage }
            ];  //to capture the snapshot of updated conversation 

            // Update the state
            setConversation(updatedConversation);
            setNewMessage('');

            const messages = updatedConversation.map(conv => ({
                role: conv.role === 'MERLIN' ? 'model' : 'user',
                message: conv.message
            }));
            const sessionId = window.sessionStorage.getItem("merlin_session_id") || "initial";

            try {
                const response = await fetch('http://127.0.0.1:80/get-topk', {
                    method: 'POST',
                    body: JSON.stringify({ session_id: sessionId, messages: messages }),
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });

                if (!response.ok) {
                    throw new Error('Failed to post data');
                }

                const data = await response.json();

                // Handle response data here
                setResult(data.topk);

            } catch (error) {
                console.error('Error posting data:', error);
            }
            setPollingActive(true);

        }
    };

    if (!isOpen) return null;
    return (
        <div className={styles.modalOverlay} onClick={onClose}>
            <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
                <h2>Conversation History</h2>
                <div className={styles.chatContainer}>
                    {conversation.map((message, index) => (
                        <div key={index} className={`${styles.messageContainer} ${message.role === 'MERLIN' ? styles.merlinContainer : styles.userContainer}`}>
                            <div className={styles.chatRole}><strong>{message.role}</strong></div>
                            <div className={`${styles.chatMessage} ${message.role === 'MERLIN' ? styles.merlin : styles.you}`}>
                                <div className={styles.chatText}>{message.message}</div>
                            </div>
                        </div>
                    ))}
                </div>
                <form className={styles.newMessageForm} onSubmit={handleSubmit}>
                    <input
                        type="text"
                        value={newMessage}
                        onChange={(e) => setNewMessage(e.target.value)}
                        placeholder="Type your message..."
                        className={styles.newMessageInput}
                    />
                    <button type="submit" className={styles.sendMessageBtn}>Send</button>
                </form>
                <button onClick={onClose} className={styles.closeBtn}>Close</button>
            </div>
        </div>
    );
}

export default Chat;
