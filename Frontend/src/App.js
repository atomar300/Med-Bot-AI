import { useState } from 'react';
import './App.css';

function App() {
  const [prompt, setPrompt] = useState("");
  const [output, setOutput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleQuery = async () => {
    setLoading(true);
    const response = await fetch("http://127.0.0.1:5000/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({"input": prompt})
    });
    const finalOutput = await response.json();
    setOutput(finalOutput.response);
    setLoading(false);
  }

  return (
    <div className="App">
      <div>
        <textarea value={prompt} onChange={e => setPrompt(e.target.value)} placeholder='Type your query...' />
        <button onClick={handleQuery}>Go</button>
      </div>

      <div>
        {loading ? <div>Loading...</div> : <p>{output}</p>}
      </div>
    </div>
  );
}

export default App;
