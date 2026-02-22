import React, { useState } from 'react';
import { Mail, Lock, User, ArrowRight, Loader, Github, Twitter, Chrome } from 'lucide-react';
import './index.css';

function Auth({ onLogin }) {
    const [isLogin, setIsLogin] = useState(true);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [name, setName] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        const endpoint = isLogin ? '/api/login' : '/api/register';
        const payload = isLogin ? { email, password } : { name, email, password };

        try {
            const response = await fetch(`http://localhost:5001${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Authentication failed');
            }

            onLogin(data.user);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleSocialLogin = (provider) => {
        setLoading(true);
        setError(null);
        // Simulate a real authentication delay for third-party providers
        setTimeout(() => {
            onLogin({
                id: provider,
                name: `${provider} User`,
                email: `user@${provider.toLowerCase()}.com`
            });
        }, 1200);
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                <div className="auth-header">
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.5rem' }}>
                        <img src="/logo_transparent.png" alt="NexEdu Logo" className="auth-logo" onError={(e) => e.target.style.display = 'none'} style={{ margin: 0, height: '180px', maxWidth: '100%', objectFit: 'contain', filter: 'drop-shadow(0 0 30px rgba(59, 130, 246, 0.5))', backgroundColor: '#ffffff', borderRadius: '24px', padding: '15px' }} />
                    </div>
                    <h2>{isLogin ? 'Welcome Back' : 'Create an Account'}</h2>
                    <p>{isLogin ? 'Enter your credentials to access the AI Nexus.' : 'Join NexEdu to learn beyond limits.'}</p>
                </div>

                <form onSubmit={handleSubmit} className="auth-form">
                    {error && <div className="auth-error">{error}</div>}

                    {!isLogin && (
                        <div className="input-group">
                            <label>Full Name</label>
                            <div className="input-with-icon">
                                <User className="input-icon auth-icon" size={18} />
                                <input
                                    type="text"
                                    value={name}
                                    onChange={(e) => setName(e.target.value)}
                                    placeholder="Future Scientist"
                                    required={!isLogin}
                                />
                            </div>
                        </div>
                    )}

                    <div className="input-group">
                        <label>Email Address</label>
                        <div className="input-with-icon">
                            <Mail className="input-icon auth-icon" size={18} />
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="learner@nexedu.ai"
                                required
                            />
                        </div>
                    </div>

                    <div className="input-group">
                        <label>Password</label>
                        <div className="input-with-icon">
                            <Lock className="input-icon auth-icon" size={18} />
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="••••••••"
                                required
                            />
                        </div>
                    </div>

                    <div className="auth-options" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', margin: '0 0 1.5rem 0', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                        <label className="remember-me" style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                            <input type="checkbox" style={{ accentColor: 'var(--accent-color)', width: '16px', height: '16px', cursor: 'pointer' }} />
                            <span>Remember me</span>
                        </label>
                        {isLogin && <a href="#" className="forgot-password" style={{ color: 'var(--accent-color)', textDecoration: 'none', transition: 'color 0.3s' }}>Forgot Password?</a>}
                    </div>

                    <button type="submit" className="auth-btn glowing-btn auth-submit" disabled={loading} style={{ width: '100%', marginBottom: '1.5rem' }}>
                        {loading ? <Loader className="spin" size={20} /> : (isLogin ? 'Authenticate' : 'Initialize Profile')}
                        {!loading && <ArrowRight size={18} />}
                    </button>

                    <div className="auth-separator" style={{ display: 'flex', alignItems: 'center', textAlign: 'center', margin: '1.5rem 0', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                        <div style={{ flex: 1, height: '1px', background: 'rgba(255, 255, 255, 0.1)' }}></div>
                        <span style={{ margin: '0 15px' }}>Or continue with</span>
                        <div style={{ flex: 1, height: '1px', background: 'rgba(255, 255, 255, 0.1)' }}></div>
                    </div>

                    <div className="social-login" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '10px', marginBottom: '1.5rem' }}>
                        <button type="button" className="social-btn" onClick={() => handleSocialLogin('Google')} disabled={loading} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '8px', padding: '12px', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', borderRadius: '8px', cursor: 'pointer', transition: 'all 0.3s ease', color: 'white' }}>
                            <Chrome size={20} color="#ea4335" />
                            <span style={{ fontSize: '0.8rem' }}>Google</span>
                        </button>
                        <button type="button" className="social-btn" onClick={() => handleSocialLogin('GitHub')} disabled={loading} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '8px', padding: '12px', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', borderRadius: '8px', cursor: 'pointer', transition: 'all 0.3s ease', color: 'white' }}>
                            <Github size={20} />
                            <span style={{ fontSize: '0.8rem' }}>GitHub</span>
                        </button>
                        <button type="button" className="social-btn" onClick={() => handleSocialLogin('Twitter')} disabled={loading} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '8px', padding: '12px', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', borderRadius: '8px', cursor: 'pointer', transition: 'all 0.3s ease', color: 'white' }}>
                            <Twitter size={20} color="#1da1f2" />
                            <span style={{ fontSize: '0.8rem' }}>Twitter</span>
                        </button>
                    </div>
                </form>

                <div className="auth-footer">
                    <p>
                        {isLogin ? "Don't have an account? " : "Already have an account? "}
                        <span className="auth-toggle" onClick={() => setIsLogin(!isLogin)}>
                            {isLogin ? 'Sign up' : 'Log in'}
                        </span>
                    </p>
                </div>
            </div>
        </div>
    );
}

export default Auth;
