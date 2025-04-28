import React, { useState, useEffect } from 'react';
import {
  BrowserRouter,
  Routes,
  Route,
  Link,
  useParams
} from 'react-router-dom';
import axios from 'axios';

axios.defaults.baseURL = 'http://127.0.0.1:5000/api';

function Menu() {
  return (
    <nav style={{ padding: 20 }}>
      <h1>Airline Management System</h1>

      <h2>Procedures</h2>
      <ul>
        <li><Link to="/procedures/add-airplane">Add Airplane</Link></li>
        <li><Link to="/procedures/add-airport">Add Airport</Link></li>
        <li><Link to="/procedures/add-person">Add Person</Link></li>
        <li><Link to="/procedures/toggle-license">Grant/Revoke License</Link></li>
        <li><Link to="/procedures/offer-flight">Offer Flight</Link></li>
        <li><Link to="/procedures/flight-landing">Flight Landing</Link></li>
        <li><Link to="/procedures/flight-takeoff">Flight Takeoff</Link></li>
        <li><Link to="/procedures/passengers-board">Board Passengers</Link></li>
        <li><Link to="/procedures/passengers-disembark">Disembark Passengers</Link></li>
        <li><Link to="/procedures/assign-pilot">Assign Pilot</Link></li>
        <li><Link to="/procedures/recycle-crew">Recycle Crew</Link></li>
        <li><Link to="/procedures/retire-flight">Retire Flight</Link></li>
        <li><Link to="/procedures/simulation-cycle">Simulation Cycle</Link></li>
      </ul>

      <h2>Views</h2>
      <ul>
        <li><Link to="/views/flights_in_the_air">Flights In The Air</Link></li>
        <li><Link to="/views/flights_on_the_ground">Flights On The Ground</Link></li>
        <li><Link to="/views/people_in_the_air">People In The Air</Link></li>
        <li><Link to="/views/people_on_the_ground">People On The Ground</Link></li>
        <li><Link to="/views/route_summary">Route Summary</Link></li>
        <li><Link to="/views/alternative_airports">Alternative Airports</Link></li>
      </ul>

      <h2>Health Check</h2>
      <ul>
        <li><Link to="/health">API Health</Link></li>
      </ul>
    </nav>
  );
}

function HealthCheck() {
  const [status, setStatus] = useState(null);

  useEffect(() => {
    axios.get('/health')
      .then(res => setStatus(res.data))
      .catch(err => setStatus({ error: err.message }));
  }, []);

  if (!status) return <p>Loading health status…</p>;

  return (
    <div style={{ padding: 20 }}>
      <h2>API Health</h2>
      <pre>{JSON.stringify(status, null, 2)}</pre>
      <Link to="/">← Back to menu</Link>
    </div>
  );
}

function ProcedurePage({ title, fields, requestConfig }) {
  const [values, setValues] = useState(fields.reduce((o, f) => ({ ...o, [f]: '' }), {}));
  const [msg, setMsg] = useState('');

  const handleSubmit = async () => {
    setMsg('');
    try {
      const url = requestConfig.url(values);
      const method = requestConfig.method || 'post';
      const body = requestConfig.body ? requestConfig.body(values) : values;
      if (method === 'delete') {
        await axios.delete(url, { data: body });
      } else {
        await axios[method](url, body);
      }
      setMsg('Success!');
    } catch (e) {
      setMsg(`Error: ${e.response?.data?.error || e.message}`);
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>{title}</h2>
      {fields.map(f => (
        <div key={f} style={{ margin: '8px 0' }}>
          <label style={{ width: 160, display: 'inline-block' }}>{f}:</label>
          <input
            value={values[f]}
            onChange={e => setValues({ ...values, [f]: e.target.value })}
          />
        </div>
      ))}
      <button onClick={handleSubmit}>Execute</button>
      {msg && <p>{msg}</p>}
      <Link to="/">← Back to menu</Link>
    </div>
  );
}

function ViewPage({ viewName }) {
  const [data, setData] = useState(null);

  useEffect(() => {
    axios.get(`/views/${viewName}`)
      .then(res => setData(res.data))
      .catch(err => setData({ error: err.message }));
  }, [viewName]);

  if (!data) return <p>Loading view…</p>;
  if (data.error) {
    return (
      <div style={{ padding: 20 }}>
        <p>Error: {data.error}</p>
        <Link to="/">← Back to menu</Link>
      </div>
    );
  }

  return (
    <div style={{ padding: 20 }}>
      <h2>{viewName.replace(/_/g, ' ').toUpperCase()}</h2>
      <table border="1" cellPadding="4">
        <thead>
          <tr>
            {Object.keys(data[0] || {}).map(col => <th key={col}>{col}</th>)}
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) =>
            <tr key={i}>
              {Object.values(row).map((val, j) => <td key={j}>{String(val)}</td>)}
            </tr>
          )}
        </tbody>
      </table>
      <Link to="/">← Back to menu</Link>
    </div>
  );
}

function ViewRoute() {
  const { viewName } = useParams();
  return <ViewPage viewName={viewName} />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Menu />} />

        <Route
          path="/procedures/add-airplane"
          element={<ProcedurePage
            title="Add Airplane"
            fields={[
              'ip_airlineID','ip_tail_num','ip_seat_capacity',
              'ip_speed','ip_locationID','ip_plane_type',
              'ip_maintenanced','ip_model','ip_neo'
            ]}
            requestConfig={{ url: () => '/airplanes' }}
          />}
        />
        <Route
          path="/procedures/add-airport"
          element={<ProcedurePage
            title="Add Airport"
            fields={[
              'ip_airportID','ip_airport_name','ip_city',
              'ip_state','ip_country','ip_locationID'
            ]}
            requestConfig={{ url: () => '/airports' }}
          />}
        />
        <Route
          path="/procedures/add-person"
          element={<ProcedurePage
            title="Add Person"
            fields={[
              'ip_personID','ip_first_name','ip_last_name',
              'ip_locationID','ip_taxID','ip_experience',
              'ip_miles','ip_funds'
            ]}
            requestConfig={{ url: () => '/people' }}
          />}
        />
        <Route
          path="/procedures/toggle-license"
          element={<ProcedurePage
            title="Grant/Revoke License"
            fields={['ip_personID','ip_license']}
            requestConfig={{
              url: v => `/pilots/${v.ip_personID}/license`,
              body: v => ({ ip_license: v.ip_license })
            }}
          />}
        />
        <Route
          path="/procedures/offer-flight"
          element={<ProcedurePage
            title="Offer Flight"
            fields={[
              'ip_flightID','ip_routeID','ip_support_airline',
              'ip_support_tail','ip_progress','ip_next_time','ip_cost'
            ]}
            requestConfig={{ url: () => '/flights' }}
          />}
        />
        <Route
          path="/procedures/flight-landing"
          element={<ProcedurePage
            title="Flight Landing"
            fields={['ip_flightID']}
            requestConfig={{
              url: v => `/flights/${v.ip_flightID}/land`
            }}
          />}
        />
        <Route
          path="/procedures/flight-takeoff"
          element={<ProcedurePage
            title="Flight Takeoff"
            fields={['ip_flightID']}
            requestConfig={{
              url: v => `/flights/${v.ip_flightID}/takeoff`
            }}
          />}
        />
        <Route
          path="/procedures/passengers-board"
          element={<ProcedurePage
            title="Board Passengers"
            fields={['ip_flightID']}
            requestConfig={{
              url: v => `/flights/${v.ip_flightID}/board`
            }}
          />}
        />
        <Route
          path="/procedures/passengers-disembark"
          element={<ProcedurePage
            title="Disembark Passengers"
            fields={['ip_flightID']}
            requestConfig={{
              url: v => `/flights/${v.ip_flightID}/disembark`
            }}
          />}
        />
        <Route
          path="/procedures/assign-pilot"
          element={<ProcedurePage
            title="Assign Pilot"
            fields={['ip_flightID','ip_personID']}
            requestConfig={{
              url: v => `/flights/${v.ip_flightID}/assign-pilot`,
              body: v => ({ ip_personID: v.ip_personID })
            }}
          />}
        />
        <Route
          path="/procedures/recycle-crew"
          element={<ProcedurePage
            title="Recycle Crew"
            fields={['ip_flightID']}
            requestConfig={{
              url: v => `/flights/${v.ip_flightID}/recycle-crew`
            }}
          />}
        />
        <Route
          path="/procedures/retire-flight"
          element={<ProcedurePage
            title="Retire Flight"
            fields={['ip_flightID']}
            requestConfig={{
              url: v => `/flights/${v.ip_flightID}`,
              method: 'delete'
            }}
          />}
        />
        <Route
          path="/procedures/simulation-cycle"
          element={<ProcedurePage
            title="Simulation Cycle"
            fields={[]}
            requestConfig={{ url: () => '/simulation-cycle' }}
          />}
        />

        <Route path="/views/:viewName" element={<ViewRoute />} />
        <Route path="/health" element={<HealthCheck />} />
      </Routes>
    </BrowserRouter>
  );
}