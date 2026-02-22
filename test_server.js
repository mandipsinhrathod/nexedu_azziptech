async function testServer() {
    const res = await fetch('http://localhost:5000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            agentId: "CurriculumArchitect",
            messageHistory: [
                { role: 'user', content: "Hello" }
            ]
        })
    });
    const data = await res.json();
    console.log("Response:", data);
}

testServer();
