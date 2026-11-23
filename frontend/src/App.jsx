import {useEffect, useState} from 'react';

const BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api';

async function request(path, {method = 'GET', body, token} = {}) {
  const response = await fetch(`${BASE}${path}`, {
    method,
    headers: {
      ...(body ? {'Content-Type': 'application/json'} : {}),
      ...(token ? {Authorization: `Bearer ${token}`} : {}),
    },
    ...(body ? {body: JSON.stringify(body)} : {}),
  });
  if (response.status === 204) return null;
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error?.message || `HTTP ${response.status}`);
  return payload.data;
}

export default function App() {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(''); // memory only: a lab simplification, not persistence
  const [mode, setMode] = useState('login');
  const [account, setAccount] = useState({fullName: '', email: '', password: ''});
  const [resources, setResources] = useState([]);
  const [draft, setDraft] = useState({title: '', description: '', url: '', category: 'lecture'});
  const [search, setSearch] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  async function refresh(query = search) {
    setLoading(true);
    try {
      setResources(await request(`/resources?q=${encodeURIComponent(query)}`));
      setMessage('');
    } catch (err) { setMessage(err.message); }
    finally {setLoading(false);}
  }
  useEffect(() => {refresh('');}, []);

  async function submitAccount(event) {
    event.preventDefault();
    setMessage('');
    try {
      const result = await request(`/auth/${mode}`, {method: 'POST', body: mode === 'login'
        ? {email: account.email, password: account.password}
        : account});
      setToken(result.accessToken);
      setUser(result.user);
      setAccount({fullName: '', email: '', password: ''});
    } catch (err) {setMessage(err.message);}
  }
  async function addResource(event) {
    event.preventDefault();
    setMessage('');
    try {await request('/resources', {method: 'POST', body: draft, token});
      setDraft({title: '', description: '', url: '', category: 'lecture'});
      await refresh(''); setSearch('');
    } catch (err) {setMessage(err.message);}
  }
  async function deleteResource(id) {
    if (!window.confirm('Remove this resource?')) return;
    try {await request(`/resources/${id}`, {method: 'DELETE', token}); await refresh();}
    catch (err) {setMessage(err.message);}
  }

  return <main className="container">
    <header className="hero"><span className="eyebrow">IUC · BTECH 3 CSE</span><h1>Campus Resource Hub</h1><p>Full-Stack Web Development · React + FastAPI + PostgreSQL</p></header>
    <section className="panel">
      {!user ? <><h2>{mode === 'login' ? 'Sign in' : 'Create an account'}</h2>
        <form onSubmit={submitAccount} className="grid">
          {mode === 'register' && <label>Full name<input required minLength={2} value={account.fullName} onChange={e => setAccount({...account, fullName: e.target.value})}/></label>}
          <label>Email<input type="email" required value={account.email} onChange={e => setAccount({...account, email: e.target.value})}/></label>
          <label>Password<input type="password" required minLength={10} value={account.password} onChange={e => setAccount({...account, password: e.target.value})}/></label>
          <button>{mode === 'login' ? 'Sign in' : 'Register'}</button>
        </form><button className="link" onClick={() => setMode(mode === 'login' ? 'register' : 'login')}>{mode === 'login' ? 'New user? Register' : 'Already registered? Sign in'}</button></>
        : <div className="toolbar"><span>Signed in as <strong>{user.full_name}</strong></span><button onClick={() => {setToken(''); setUser(null);}}>Sign out</button></div>}
    </section>
    {user && <section className="panel"><h2>Add a learning resource</h2>
      <form className="grid" onSubmit={addResource}>
        <label>Title<input required minLength={3} maxLength={150} value={draft.title} onChange={e => setDraft({...draft, title: e.target.value})}/></label>
        <label>URL<input required type="url" value={draft.url} onChange={e => setDraft({...draft, url: e.target.value})}/></label>
        <label>Description<input maxLength={2000} value={draft.description} onChange={e => setDraft({...draft, description: e.target.value})}/></label>
        <label>Category<select value={draft.category} onChange={e => setDraft({...draft, category: e.target.value})}><option>lecture</option><option>exercise</option><option>video</option><option>general</option></select></label>
        <button>Publish resource</button>
      </form></section>}
    <section className="panel"><div className="toolbar"><h2>Shared resources</h2><form onSubmit={e => {e.preventDefault(); refresh();}}><input placeholder="Search resources" value={search} onChange={e => setSearch(e.target.value)}/><button>Search</button></form></div>
      {message && <p role="alert" className="error">{message}</p>}
      {loading ? <p>Loading…</p> : resources.length === 0 ? <p>No matching resources yet.</p> :
        <div className="cards">{resources.map(item => <article className="resource" key={item.id}><div><span className="tag">{item.category}</span><h3>{item.title}</h3><p>{item.description}</p><small>Shared by {item.owner_name}</small></div><div><a href={item.url} rel="noreferrer noopener" target="_blank">Open link</a>{user && String(item.owner_id) === String(user.id) && <button className="danger" onClick={() => deleteResource(item.id)}>Delete</button>}</div></article>)}</div>}
    </section><footer>Educational starter · Replace demo credentials before deploying.</footer>
  </main>;
}
