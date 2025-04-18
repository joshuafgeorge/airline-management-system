import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [procedure, setProcedure] = useState('');
  const [args, setArgs] = useState('');
  const [view, setView] = useState('');
  const [viewData, setViewData] = useState([]);

  const callProcedure = async () => {
    try {
      const response = await axios.post(`http://localhost:5000/api/procedure/${procedure}`, {
        args: args.split(',').map(a => a.trim())
      });
      alert('Procedure executed successfully');
    } catch (e) {
      alert('Failed to execute procedure');
    }
  };

  const fetchView = async () => {
    try {
      const res = await axios.get(`http://localhost:5000/api/view/${view}`);
      setViewData(res.data);
    } catch (e) {
      alert('Failed to load view');
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>Airline Management System</h1>

      <h2>Call Stored Procedure</h2>
      <input placeholder="Procedure Name" value={procedure} onChange={e => setProcedure(e.target.value)} />
      <input placeholder="Args (comma separated)" value={args} onChange={e => setArgs(e.target.value)} />
      <button onClick={callProcedure}>Execute</button>

      <h2>View Data</h2>
      <input placeholder="View Name" value={view} onChange={e => setView(e.target.value)} />
      <button onClick={fetchView}>Load</button>

      <pre>{JSON.stringify(viewData, null, 2)}</pre>
    </div>
  );
}

export default App;
