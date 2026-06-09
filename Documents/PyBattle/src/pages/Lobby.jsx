import React, { useState, useEffect } from 'react';
import API from '../api/axios';
import { useNavigate } from 'react-router-dom';
import problems from '../problems';

const lobbyStyles = `
  * { box-sizing: border-box; }

  @media (max-width: 768px) {
    .lobby-navbar { padding: 12px 15px !important; }
    .lobby-logo { font-size: 18px !important; }
    .lobby-content { padding: 20px 15px !important; }
    .lobby-heading { font-size: 28px !important; }
    .lobby-grid { grid-template-columns: 1fr 1fr !important; gap: 12px !important; }
    .lobby-create-btn { max-width: 100% !important; }
    .welcome-text { font-size: 13px !important; }
    .change-btn { font-size: 11px !important; padding: 4px 10px !important; }
  }

  @media (max-width: 480px) {
    .lobby-grid { grid-template-columns: 1fr !important; }
    .lobby-heading { font-size: 22px !important; }
    .lobby-subheading { font-size: 13px !important; }
    .battle-card-title { font-size: 15px !important; }
  }
`;

function Lobby() {
  const [battles, setBattles] = useState([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const guestId = sessionStorage.getItem('guest_id') || Math.floor(Math.random() * 10000);
  sessionStorage.setItem('guest_id', guestId);
  const guestName = sessionStorage.getItem('guest_name') || 'Guest_' + guestId;
  sessionStorage.setItem('guest_name', guestName);

  const fetchBattles = async () => {
    try {
      const res = await API.get('/battles/list');
      setBattles(res.data);
    } catch (err) {
      console.error('Failed to fetch battles');
    }
  };

  useEffect(() => {
    fetchBattles();
    const interval = setInterval(fetchBattles, 3000);
    return () => clearInterval(interval);
  }, []);

  const createBattle = async () => {
    setLoading(true);
    try {
      const randomProblem = problems[Math.floor(Math.random() * problems.length)];
      const res = await API.post(`/battles/create?player1_id=${guestId}`, {
        problem_id: randomProblem.id,
      });
      navigate(`/battle/${res.data.id}`, { state: { problem: randomProblem } });
    } catch (err) {
      console.error('Failed to create battle');
    }
    setLoading(false);
  };

  const joinBattle = async (battleId) => {
    try {
      const res = await API.post(`/battles/join/${battleId}?player2_id=${guestId}`);
      const problem = problems.find(p => p.id === res.data.problem_id);
      navigate(`/battle/${battleId}`, { state: { problem } });
    } catch (err) {
      console.error('Failed to join battle');
    }
  };

  return (
    <div style={styles.container}>
      <style>{lobbyStyles}</style>

      {/* Navbar */}
      <div className="lobby-navbar" style={styles.navbar}>
        <h2 className="lobby-logo" style={styles.navLogo}>⚔️ Battle.py</h2>
        <div style={styles.navRight}>
          <span className="welcome-text" style={styles.welcome}>👋 {guestName}</span>
          <button
            className="change-btn"
            style={styles.changeNameBtn}
            onClick={() => {
              sessionStorage.removeItem('guest_name');
              sessionStorage.removeItem('guest_id');
              window.location.href = '/setname';
            }}
          >
            ✏️ Change Name
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="lobby-content" style={styles.content}>
        <h1 className="lobby-heading" style={styles.heading}>Battle Lobby</h1>
        <p className="lobby-subheading" style={styles.subheading}>
          Challenge someone or wait for an opponent!
        </p>

        {/* Create Battle Button */}
        <button
          className="btn-primary lobby-create-btn"
          style={styles.createBtn}
          onClick={createBattle}
          disabled={loading}
        >
          {loading ? 'Creating...' : '⚔️ Create New Battle'}
        </button>

        {/* Battle List */}
        <h2 style={styles.listTitle}>Open Battles</h2>

        {battles.length === 0 ? (
          <div style={styles.emptyCard}>
            <p style={{ fontSize: '40px', marginBottom: '10px' }}>🎮</p>
            <p style={{ fontWeight: '700', marginBottom: '5px' }}>No open battles right now.</p>
            <p style={{ fontSize: '14px' }}>Be the first to create one!</p>
          </div>
        ) : (
          <div className="lobby-grid" style={styles.grid}>
            {battles.map((battle) => (
              <div key={battle.id} style={styles.battleCard}>
                <div style={styles.battleIcon}>⚔️</div>
                <p className="battle-card-title" style={styles.battleTitle}>
                  Battle #{battle.id}
                </p>
                <p style={styles.battleInfo}>
                  Problem #{battle.problem_id} • Waiting...
                </p>
                <p style={styles.battleStatus}>🟢 Open</p>
                <button
                  className="btn-primary"
                  style={styles.joinBtn}
                  onClick={() => joinBattle(battle.id)}
                >
                  Join Battle
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

const styles = {
  container: { minHeight: '100vh', background: '#0f0f1a' },
  navbar: {
    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
    padding: '15px 30px', background: '#1a1a2e',
    borderBottom: '1px solid #6c63ff55',
  },
  navLogo: { fontSize: '22px', fontWeight: '900', color: '#6c63ff' },
  navRight: { display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' },
  welcome: { color: '#00d4aa', fontWeight: '600', fontSize: '14px' },
  changeNameBtn: {
    background: 'transparent', border: '1px solid #6c63ff',
    color: '#6c63ff', padding: '6px 14px', borderRadius: '20px',
    cursor: 'pointer', fontWeight: '600', fontSize: '13px',
  },
  content: {
    maxWidth: '900px', margin: '0 auto',
    padding: '40px 20px', textAlign: 'center',
  },
  heading: {
    fontSize: '42px', fontWeight: '900',
    color: '#ffffff', marginBottom: '10px',
  },
  subheading: { color: '#aaaaaa', marginBottom: '30px' },
  createBtn: { maxWidth: '300px', margin: '0 auto 40px auto', display: 'block' },
  listTitle: {
    fontSize: '24px', fontWeight: '700',
    color: '#6c63ff', marginBottom: '20px',
  },
  emptyCard: {
    background: '#1a1a2e', borderRadius: '20px', padding: '40px',
    color: '#aaaaaa', border: '1px solid #6c63ff33',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))',
    gap: '20px',
  },
  battleCard: {
    background: '#1a1a2e', borderRadius: '20px', padding: '20px',
    border: '1px solid #6c63ff55', textAlign: 'center',
    transition: 'transform 0.2s, box-shadow 0.2s',
  },
  battleIcon: { fontSize: '36px', marginBottom: '10px' },
  battleTitle: { fontSize: '18px', fontWeight: '700', color: '#ffffff', marginBottom: '5px' },
  battleInfo: { color: '#aaaaaa', fontSize: '13px', marginBottom: '5px' },
  battleStatus: { color: '#00d4aa', marginBottom: '15px', fontWeight: '600', fontSize: '14px' },
  joinBtn: { maxWidth: '150px', margin: '0 auto', padding: '8px 20px' },
};

export default Lobby;
