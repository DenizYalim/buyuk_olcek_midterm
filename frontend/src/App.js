import React, { useState } from 'react';

function ChatBubble({msg}){
  return (
    <div className={"bubble " + (msg.from === 'user' ? 'user' : 'bot')}>
      <div className="text">{msg.text}</div>
    </div>
  );
}

export default function App(){
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);

  async function sendMessage(message){
    setLoading(true);
    setMessages((m)=>[...m, {from:'user', text:message}]);
    try{
      const res = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
      });

      // Read raw text first, then try to parse JSON to avoid consuming the body twice
      const raw = await res.text();
      let j;
      try{
        j = JSON.parse(raw);
      }catch(parseErr){
        j = { response: raw };
      }

      let reply = 'No response';
      if (j.result !== undefined) {
        try {
          reply = typeof j.result === 'string' ? j.result : JSON.stringify(j.result);
        } catch (e) {
          reply = String(j.result);
        }
      } else if (j.response !== undefined) {
        reply = j.response;
      } else if (j.error !== undefined) {
        reply = 'Error: ' + j.error;
      }
      setMessages((m)=>[...m, {from:'bot', text: reply}]);
    }catch(e){
      setMessages((m)=>[...m, {from:'bot', text: 'Error: ' + String(e)}]);
    }finally{
      setLoading(false);
    }
  }

  function handleSubmit(e){
    e.preventDefault();
    if(!text.trim()) return;
    sendMessage(text.trim());
    setText('');
  }

  return (
    <div className="app">
      <header>
        <h1>Tuition Assistant</h1>
        <div className="actions">
          <button onClick={() => sendMessage('Query tuition for student 123')}>
            Query Tuition
          </button>
          <button onClick={() => sendMessage('Show unpaid tuition for student 123')}>
            Unpaid Tuition
          </button>
          <button onClick={() => sendMessage('Pay tuition for student 123')}>
            Pay Tuition
          </button>
        </div>
      </header>

      <main>
        <div className="chat">
          {messages.map((m, i) => (
            <ChatBubble key={i} msg={m} />
          ))}
        </div>
      </main>

      <form className="composer" onSubmit={handleSubmit}>
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Type a message or use the buttons above"
          disabled={loading}
        />
        <button type="submit" disabled={loading}>Send</button>
      </form>
    </div>
  );
}
