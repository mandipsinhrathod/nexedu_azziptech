import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { BookOpen, BrainCircuit, Target, ListChecks, Rocket, TrendingUp, Sparkles, Search, GraduationCap, User, LogOut, ArrowRight, Award } from 'lucide-react';
import './index.css';
import Auth from './Auth';

const SUGGESTED_TOPICS = [
    "Quantum Mechanics",
    "Astrophysics",
    "String Theory",
    "Calculus",
    "Linear Algebra",
    "Organic Chemistry",
    "Thermodynamics",
    "Machine Learning",
    "Data Structures",
    "Number Theory",
    "Fluid Dynamics",
    "Genetics",
    "Electromagnetism"
];

const AGENTS = [
    { id: 'CurriculumArchitect', name: 'Syllabus Creator', role: 'Builds Your Learning Path', icon: BookOpen, color: '#3b82f6' },
    { id: 'ResearchPhysicist', name: 'Core Teacher', role: 'Explains Concepts & Math', icon: BrainCircuit, color: '#8b5cf6' },
    { id: 'AdaptiveInstructor', name: 'Practical Guide', role: 'Gives Real-World Examples', icon: Target, color: '#10b981' },
    { id: 'AssessmentDesigner', name: 'Quiz Master', role: 'Tests Your Knowledge', icon: ListChecks, color: '#f59e0b' },
    { id: 'InnovationCatalyst', name: 'Future Explorer', role: 'Explores Advanced Ideas', icon: Rocket, color: '#ef4444' },
    { id: 'ProgressAnalyst', name: 'Growth Tracker', role: 'Tracks Your Mastery', icon: TrendingUp, color: '#06b6d4' },
    { id: 'CertificationAuthority', name: 'Certification Test', role: 'Final Exam & Certificate', icon: Award, color: '#eab308' }
];

function App() {
    const [user, setUser] = useState(null);
    const [topic, setTopic] = useState('');
    const [level, setLevel] = useState('Beginner');
    const [suggestions, setSuggestions] = useState([]);
    const [activeSession, setActiveSession] = useState(false);
    const [toastMessage, setToastMessage] = useState(null);
    const [toastType, setToastType] = useState('error');

    const showToast = (message, type = 'error') => {
        setToastMessage(message);
        setToastType(type);
        setTimeout(() => setToastMessage(null), 4000);
    };

    const handleTopicChange = (e) => {
        const val = e.target.value;
        setTopic(val);
        if (val.trim().length > 1) {
            setSuggestions(SUGGESTED_TOPICS.filter(t => t.toLowerCase().includes(val.toLowerCase()) && t.toLowerCase() !== val.toLowerCase()));
        } else {
            setSuggestions([]);
        }
    };

    const selectSuggestion = (suggestion) => {
        setTopic(suggestion);
        setSuggestions([]);
    };

    const [chatHistories, setChatHistories] = useState({});
    const [loadingAgent, setLoadingAgent] = useState(null);
    const [selectedAgent, setSelectedAgent] = useState(null);
    const [draftMessage, setDraftMessage] = useState('');

    const [certificates, setCertificates] = useState(() => JSON.parse(localStorage.getItem('nexedu_certs') || '[]'));
    const [showCerts, setShowCerts] = useState(false);

    const chatEndRef = useRef(null);
    const chatContainerRef = useRef(null);

    // Scroll to the top when navigating to a new agent
    useEffect(() => {
        if (chatContainerRef.current) {
            chatContainerRef.current.scrollTop = 0;
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    }, [selectedAgent]);

    // Auto-scrolling to bottom on new messages has been removed
    // so that the user does not get forced to the bottom of long responses.

    const startSession = () => {
        if (!topic) return showToast("Please enter a research topic!", "error");
        setActiveSession(true);
        setChatHistories({});

        // Initialize standard prompt message
        const initialMessage = `The topic the student wants to learn is: "${topic}". The requested difficulty level is: "${level}". Please begin.`;
        handleAgentInteraction('CurriculumArchitect', initialMessage);
    };

    const handleAgentInteraction = async (agentId, userMessageText) => {
        if (!topic || !userMessageText.trim()) return;

        setSelectedAgent(agentId);
        setLoadingAgent(agentId);
        setDraftMessage('');

        // Get existing history or start fresh
        let currentHistory = [...(chatHistories[agentId] || [])];

        // Auto-inject context if it's the very first message
        if (currentHistory.length === 0) {
            const currentIndex = AGENTS.findIndex(a => a.id === agentId);
            if (currentIndex > 0) {
                const prevAgentId = AGENTS[currentIndex - 1].id;
                const prevAgentHistory = chatHistories[prevAgentId];
                if (prevAgentHistory) {
                    const lastAssistantMessage = [...prevAgentHistory].reverse().find(m => m.role === 'assistant');
                    if (lastAssistantMessage) {
                        userMessageText = `${userMessageText}\n\n[System Context from Previous Node (${AGENTS[currentIndex - 1].name}): \n${lastAssistantMessage.content}]`;
                    }
                }
            } else if (agentId !== 'CurriculumArchitect' && chatHistories['CurriculumArchitect']) {
                // Fallback for non-sequential jumps
                const architectFirstResponse = chatHistories['CurriculumArchitect'].find(m => m.role === 'assistant');
                if (architectFirstResponse) {
                    userMessageText = `${userMessageText}\n\n[System Context: Here is the generated Curriculum: \n${architectFirstResponse.content}]`;
                }
            }
        }

        // Append the user's new message to history
        const newHistory = [...currentHistory, { role: 'user', content: userMessageText }];

        // Optimistically update UI
        setChatHistories(prev => ({
            ...prev,
            [agentId]: newHistory
        }));

        try {
            const response = await fetch('http://localhost:5001/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    agentId,
                    messageHistory: newHistory // Backend now expects full message history!
                })
            });

            if (!response.ok) {
                throw new Error("Failed to fetch insight from AI Core.");
            }

            const data = await response.json();

            // Append the assistant's reply
            setChatHistories(prev => ({
                ...prev,
                [agentId]: [...prev[agentId], { role: 'assistant', content: data.content }]
            }));
        } catch (err) {
            showToast("System Diagnostics Error: " + err.message, "error");
        } finally {
            setLoadingAgent(null);
        }
    };

    const handleSendMessage = (e) => {
        e.preventDefault();
        if (selectedAgent && draftMessage.trim()) {
            handleAgentInteraction(selectedAgent, draftMessage);
        }
    };

    if (!user) {
        return <Auth onLogin={setUser} />;
    }

    const handleLogout = () => {
        setUser(null);
        setActiveSession(false);
        setChatHistories({});
        setTopic('');
        setLevel('Beginner');
        setSuggestions([]);
    };

    return (
        <div className="app-container">
            {toastMessage && (
                <div className={`toast-notification ${toastType}`}>
                    {toastType === 'error' ? '⚠️ ' : '✅ '} {toastMessage}
                </div>
            )}
            <header className="header">
                <div className="header-left" style={{ display: 'flex', alignItems: 'center' }}>
                    <div className="logo-container">
                        <img src="/logo_transparent.png" alt="NexEdu Logo" className="logo" onError={(e) => e.target.style.display = 'none'} style={{ height: '90px', maxWidth: '350px', objectFit: 'contain', filter: 'drop-shadow(0 0 15px rgba(59, 130, 246, 0.4))', margin: '0', backgroundColor: '#ffffff', borderRadius: '16px', padding: '10px' }} />
                    </div>
                </div>
                <div className="header-right" style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
                        <span style={{ fontSize: '0.75rem', fontWeight: 'bold', letterSpacing: '1px', textTransform: 'uppercase', color: 'var(--text-secondary)' }}>Our Website</span>
                        <a
                            href="http://localhost:5000/"
                            className="start-btn"
                            style={{ padding: '0.6rem 1.2rem', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.95rem', backgroundColor: '#8b5cf6', border: '1px solid #a78bfa' }}
                            title="Navigate to Original EduGPT"
                            target="_blank" rel="noreferrer"
                        >
                            <Rocket size={16} /> EduGPT Hub
                        </a>
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
                        <span style={{ fontSize: '0.75rem', fontWeight: 'bold', letterSpacing: '1px', textTransform: 'uppercase', color: 'var(--text-secondary)' }}>Achievements</span>
                        <button onClick={() => setShowCerts(true)} className="start-btn" style={{ padding: '0.6rem 1.2rem', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.95rem', backgroundColor: '#eab308', border: '1px solid #facc15', color: '#111827', fontWeight: 'bold', borderRadius: '8px' }}>
                            <Award size={18} /> Certificates
                        </button>
                    </div>

                    <div className="user-profile-badge">
                        <div className="avatar-circle">
                            <User size={20} className="avatar-icon" />
                        </div>
                        <div className="user-details">
                            <span className="welcome-text">Welcome,</span>
                            <span className="user-name">{user.name}</span>
                        </div>
                        <button onClick={handleLogout} className="signout-btn icon-btn" title="Sign Out">
                            <LogOut size={18} />
                        </button>
                    </div>
                </div>
            </header>

            {showCerts ? (
                <main className="main-content" style={{ padding: '3rem 2rem', width: '100%', maxWidth: '1000px', margin: '0 auto', flexGrow: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '2rem' }}>
                        <h2 style={{ display: 'flex', alignItems: 'center', gap: '15px', marginTop: 0, color: 'white', fontSize: '2rem' }}>
                            <Award color="#eab308" size={36} /> My Certificates
                        </h2>
                        <button onClick={() => setShowCerts(false)} className="start-btn" style={{ padding: '0.6rem 1.2rem', backgroundColor: '#374151', color: 'white', border: '1px solid #4b5563', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold' }}>Return to Hub</button>
                    </div>

                    {certificates.length === 0 ? (
                        <div style={{ textAlign: 'center', padding: '5rem 2rem', backgroundColor: 'rgba(255,255,255,0.02)', borderRadius: '16px', border: '1px dashed rgba(255,255,255,0.1)' }}>
                            <Award size={64} style={{ color: '#4b5563', marginBottom: '1rem' }} />
                            <h3 style={{ color: '#d1d5db', marginBottom: '0.5rem' }}>No Certificates Yet</h3>
                            <p style={{ color: '#9ca3af', maxWidth: '400px', margin: '0 auto' }}>Complete a learning module and pass the Certification Test to earn an official credential!</p>
                        </div>
                    ) : (
                        <div style={{ display: 'grid', gap: '20px', gridTemplateColumns: 'repeat(auto-fill, minmax(400px, 1fr))' }}>
                            {certificates.map((cert, idx) => (
                                <div key={idx} style={{ padding: '24px', borderRadius: '16px', background: 'linear-gradient(135deg, rgba(234, 179, 8, 0.1) 0%, rgba(234, 179, 8, 0.02) 100%)', border: '1px solid rgba(234, 179, 8, 0.3)', display: 'flex', flexDirection: 'column', gap: '15px', position: 'relative', overflow: 'hidden' }}>
                                    <div style={{ position: 'absolute', top: '-10px', right: '-10px', opacity: 0.1 }}><Award size={100} color="#fbbf24" /></div>
                                    <div>
                                        <h3 style={{ margin: '0 0 8px 0', color: '#fbbf24', fontSize: '1.4rem' }}>Certificate of Mastery</h3>
                                        <p style={{ margin: 0, color: '#f3f4f6', fontSize: '1.1rem' }}>Topic: <strong style={{ color: 'white' }}>{cert.topic}</strong></p>
                                    </div>
                                    <div style={{ marginTop: 'auto', borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '15px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                        <div>
                                            <span style={{ display: 'block', fontSize: '0.85rem', color: '#9ca3af', marginBottom: '4px' }}>Issued to</span>
                                            <span style={{ color: 'white', fontWeight: 'bold' }}>{user.name}</span>
                                        </div>
                                        <div style={{ textAlign: 'right' }}>
                                            <span style={{ display: 'block', fontSize: '0.85rem', color: '#9ca3af', marginBottom: '4px' }}>Date</span>
                                            <span style={{ color: 'white' }}>{cert.date}</span>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </main>
            ) : !activeSession ? (
                <main className="main-content flex-center">
                    <div className="init-card relative">
                        <div className="init-header">
                            <div className="init-icon-wrapper">
                                <Sparkles size={36} className="init-icon text-accent" />
                            </div>
                            <h2>Initialize Learning Node</h2>
                            <p className="init-subtitle">Configure the parameters for your multi-agent cognitive session.</p>
                        </div>

                        <div className="input-group-row">
                            <div className="autocomplete-wrapper">
                                <Search size={20} className="input-icon" />
                                <input
                                    type="text"
                                    value={topic}
                                    onChange={handleTopicChange}
                                    placeholder="Enter topic: Gravity, AI, Quantum..."
                                    className="topic-input w-full with-icon"
                                    onKeyDown={e => e.key === 'Enter' && startSession()}
                                />
                                {suggestions.length > 0 && (
                                    <ul className="suggestions-list">
                                        {suggestions.map((s, i) => (
                                            <li key={i} onClick={() => selectSuggestion(s)}>
                                                {s}
                                            </li>
                                        ))}
                                    </ul>
                                )}
                            </div>
                            <div className="select-wrapper">
                                <GraduationCap size={20} className="select-icon" />
                                <select value={level} onChange={(e) => setLevel(e.target.value)} className="level-select with-icon">
                                    <option value="Beginner">Beginner Level</option>
                                    <option value="Intermediate">Intermediate Level</option>
                                    <option value="Advanced">Advanced Level</option>
                                    <option value="Research">Research Level</option>
                                </select>
                            </div>
                        </div>

                        <button onClick={startSession} className="start-btn glowing-btn">
                            Initialize Modules <Rocket size={18} />
                        </button>
                    </div>
                </main>
            ) : (
                <main className="dashboard-grid">
                    <aside className="agents-sidebar">
                        <h3 className="sidebar-title">Cognitive Modules</h3>
                        <p className="topic-indicator">Topic: <span>{topic}</span></p>

                        <div className="agent-buttons">
                            {AGENTS.map((agent) => {
                                const isCompleted = chatHistories[agent.id] && chatHistories[agent.id].length > 0;
                                return (
                                    <button
                                        key={agent.id}
                                        className={`agent-tab ${selectedAgent === agent.id ? 'active' : ''} ${isCompleted ? 'completed' : ''}`}
                                        onClick={() => {
                                            setSelectedAgent(agent.id);
                                            // If no history exists, auto-initialize
                                            if (!chatHistories[agent.id]) {
                                                handleAgentInteraction(agent.id, `Initialize the ${agent.name} protocol for topic: "${topic}".`);
                                            }
                                        }}
                                        disabled={loadingAgent !== null && loadingAgent !== agent.id && loadingAgent !== selectedAgent}
                                    >
                                        <div className="agent-info-wrapper">
                                            <div className="agent-badge" style={{ backgroundColor: `${agent.color}20`, color: agent.color, boxShadow: `0 0 10px ${agent.color}40` }}>
                                                <agent.icon size={20} />
                                            </div>
                                            <div className="agent-info">
                                                <strong style={{ fontSize: '1.1rem' }}>{agent.name}</strong>
                                                <small>{agent.role}</small>
                                            </div>
                                        </div>
                                        {loadingAgent === agent.id && <span className="loader-ring"></span>}
                                    </button>
                                )
                            })}
                        </div>

                        <button className="reset-btn" onClick={() => {
                            if (chatHistories['CertificationAuthority'] && chatHistories['CertificationAuthority'].length > 1) {
                                if (!certificates.find(c => c.topic === topic)) {
                                    const newCerts = [...certificates, { topic, date: new Date().toLocaleDateString() }];
                                    setCertificates(newCerts);
                                    localStorage.setItem('nexedu_certs', JSON.stringify(newCerts));
                                    showToast("Course Completed! Earned new Certificate.", "success");
                                }
                            }
                            setActiveSession(false);
                        }}>End Session</button>
                    </aside>

                    <section className="agent-display">
                        {selectedAgent ? (
                            <div className="display-card chat-view">
                                <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                                    <div className="agent-header-icon" style={{ flexShrink: 0, width: '55px', height: '55px', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: '50%', backgroundColor: `${AGENTS.find(a => a.id === selectedAgent)?.color}20`, border: `1px solid ${AGENTS.find(a => a.id === selectedAgent)?.color}40`, color: AGENTS.find(a => a.id === selectedAgent)?.color }}>
                                        {React.createElement(AGENTS.find(a => a.id === selectedAgent)?.icon || Sparkles, { size: 28 })}
                                    </div>
                                    <h2 style={{ margin: 0 }}>{AGENTS.find(a => a.id === selectedAgent)?.name} Protocol</h2>
                                </div>

                                <div className="chat-history scrollbar-custom" ref={chatContainerRef}>
                                    {(!chatHistories[selectedAgent] || chatHistories[selectedAgent].length === 0) && (
                                        <p className="empty-state">System ready. Waiting for initialization...</p>
                                    )}

                                    {chatHistories[selectedAgent]?.map((msg, index) => {
                                        if (msg.role === 'system') return null; // Don't show system prompts

                                        const isAssistant = msg.role === 'assistant';
                                        const currentAgent = AGENTS.find(a => a.id === selectedAgent);

                                        return (
                                            <div key={index} style={{ display: 'flex', gap: '12px', alignItems: 'flex-start', alignSelf: isAssistant ? 'flex-start' : 'flex-end', maxWidth: '85%' }}>
                                                {isAssistant && (
                                                    <div className="ai-avatar pulse-anim" style={{ flexShrink: 0, marginTop: '5px', width: '42px', height: '42px', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: '50%', backgroundColor: `${currentAgent?.color}20`, color: currentAgent?.color, border: `1px solid ${currentAgent?.color}40`, boxShadow: `0 0 10px ${currentAgent?.color}30` }}>
                                                        {React.createElement(currentAgent?.icon || Sparkles, { size: 22 })}
                                                    </div>
                                                )}
                                                <div className={`chat-bubble ${msg.role}`} style={{ maxWidth: '100%', alignSelf: 'auto' }}>
                                                    <div className="markdown-render">
                                                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                                            {msg.content.replace(/\[System Context:[\s\S]*?\]/g, '').trim()}
                                                        </ReactMarkdown>
                                                    </div>
                                                </div>
                                            </div>
                                        );
                                    })}

                                    {loadingAgent === selectedAgent && (
                                        <div className="loading-state inline-loading">
                                            <div className="pulsing-core small-core"></div>
                                            <p>Synthesizing...</p>
                                        </div>
                                    )}

                                    {/* Invisible div to scroll to bottom automatically */}
                                    <div ref={chatEndRef} />
                                </div>

                                <form className="chat-input-area" onSubmit={handleSendMessage}>
                                    <input
                                        type="text"
                                        value={draftMessage}
                                        onChange={(e) => setDraftMessage(e.target.value)}
                                        placeholder={`Follow up with the ${AGENTS.find(a => a.id === selectedAgent)?.name}...`}
                                        className="chat-input"
                                        disabled={loadingAgent !== null}
                                    />
                                    <button type="submit" className="send-btn" disabled={loadingAgent !== null || !draftMessage.trim()}>
                                        Send
                                    </button>
                                </form>

                                {(() => {
                                    const currentIndex = AGENTS.findIndex(a => a.id === selectedAgent);
                                    if (!loadingAgent && chatHistories[selectedAgent]?.length > 0 && currentIndex >= 0 && currentIndex < AGENTS.length - 1) {
                                        const nextAgent = AGENTS[currentIndex + 1];
                                        return (
                                            <button
                                                className="proceed-next-bar"
                                                onClick={() => {
                                                    setSelectedAgent(nextAgent.id);
                                                    if (!chatHistories[nextAgent.id] || chatHistories[nextAgent.id].length === 0) {
                                                        handleAgentInteraction(nextAgent.id, `Transitioning to ${nextAgent.name} protocol for topic: "${topic}". Please proceed with the next learning segment based on the previous context.`);
                                                    }
                                                }}
                                            >
                                                Proceed to {nextAgent.name} <ArrowRight size={20} />
                                            </button>
                                        )
                                    }
                                    return null;
                                })()}
                            </div>
                        ) : (
                            <div className="welcome-console">
                                <h2>System Online</h2>
                                <p>Welcome to NexEdu. Select a Cognitive Module from the left panel to connect and chat.</p>
                            </div>
                        )}
                    </section>
                </main>
            )
            }

            <footer className="app-footer">
                <div className="footer-content">
                    <img src="/logo_transparent.png" alt="NexEdu Logo" className="footer-logo" onError={(e) => e.target.style.display = 'none'} style={{ height: '80px', backgroundColor: '#ffffff', borderRadius: '12px', padding: '8px' }} />
                    <div className="footer-text">
                        <p>&copy; {new Date().getFullYear()} NexEdu Intelligence.</p>
                        <small>Empowering the future through AI-driven education.</small>
                    </div>
                </div>
            </footer>


        </div >
    );
}

export default App;
