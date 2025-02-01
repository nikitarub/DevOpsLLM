import React, { useState, useEffect } from 'react';

function App() {
    const [messages, setMessages] = useState([]);
    const [inputValue, setInputValue] = useState('');

    useEffect(() => {
        // Define an async function inside useEffect
        const fetchLatestMessageAsync = async () => {
            try {
                const response = await fetch('http://localhost:8000/api/messages/latest');
                if (response.ok) {
                    const latestMessage = await response.json();
                    setMessages(prevMessages => [...prevMessages, latestMessage]);
                }
            } catch (error) {
                console.error("Failed to fetch latest message:", error);
            }
        };

        // Call the async function
        fetchLatestMessageAsync();
    }, []);

    const fetchChatHistory = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/messages/history');
            if (response.ok) {
                setMessages(await response.json());
            }
        } catch (error) {
            console.error("Failed to fetch chat history:", error);
        }
    };

    const sendMessage = async () => {
        if (!inputValue.trim()) return;

        try {
            const response = await fetch('http://localhost:8000/api/messages/send', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ content: inputValue })
            });

            if (response.ok) {
                const newMessage = await response.json();
                setMessages(prevMessages => [...prevMessages, { role: 'user', content: inputValue }, newMessage]);
                setInputValue('');
            }
        } catch (error) {
            console.error("Failed to send message:", error);
        }
    };

    return (
        <div className="App">
            <h1>LLM Chat App</h1>
            <button onClick={fetchChatHistory}>Load History</button>
            <div style={{ marginBottom: '20px' }}>
                {messages.map((msg, index) => (
                    <p key={index} style={{ textAlign: msg.role === 'user' ? 'right' : 'left', margin: '5px 0' }}>
                        [{msg.role}] {msg.content}
                    </p>
                ))}
            </div>
            <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Type a message..."
                style={{ width: '80%', padding: '10px', marginRight: '5px' }}
            />
            <button onClick={sendMessage}>Send</button>
        </div>
    );
}

export default App;