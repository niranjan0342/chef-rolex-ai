const API_BASE = "http://localhost:8000/api/v1";
        let sessionId = localStorage.getItem("session_id");
        let token = localStorage.getItem("token");
        let currentUser = null;

        const chatMessages = document.getElementById("chatMessages");
        const userInput = document.getElementById("userInput");
        const micBtn = document.getElementById("micBtn");
        const sendBtn = document.getElementById("sendBtn");
        const newChatBtn = document.getElementById("newChatBtn");
        const newChatSidebarBtn = document.getElementById("newChatSidebarBtn");
        const sessionList = document.getElementById("sessionList");

        // Auth Elements
        const authModal = document.getElementById("authModal");
        const loginBtnSidebar = document.getElementById("loginBtnSidebar");
        const userInfo = document.getElementById("userInfo");
        const userNameDisplay = document.getElementById("userNameDisplay");
        const logoutBtn = document.getElementById("logoutBtn");
        const closeModalBtn = document.getElementById("closeModalBtn");
        const authSubmitBtn = document.getElementById("authSubmitBtn");
        const authToggleLink = document.getElementById("authToggleLink");
        const authTitle = document.getElementById("modalTitle");
        const emailGroup = document.getElementById("emailGroup");
        const authError = document.getElementById("authError");

        let isLoginMode = true;

        // Auth Logic
        function toggleModal(show) {
            authModal.style.display = show ? 'flex' : 'none';
            authError.textContent = "";
        }

        loginBtnSidebar.onclick = () => toggleModal(true);
        closeModalBtn.onclick = () => toggleModal(false);

        authToggleLink.onclick = () => {
            isLoginMode = !isLoginMode;
            authTitle.textContent = isLoginMode ? "Login" : "Register";
            authSubmitBtn.textContent = isLoginMode ? "Login" : "Register";
            document.getElementById("authToggleText").textContent = isLoginMode ? "Don't have an account? " : "Already have an account? ";
            authToggleLink.textContent = isLoginMode ? "Register" : "Login";
            emailGroup.style.display = isLoginMode ? "none" : "block";
            authError.textContent = "";
        };

        authSubmitBtn.onclick = async () => {
            const username = document.getElementById("authUsername").value;
            const password = document.getElementById("authPassword").value;
            const email = document.getElementById("authEmail").value;

            authError.textContent = "";

            try {
                if (isLoginMode) {
                    const params = new URLSearchParams();
                    params.append('username', username);
                    params.append('password', password);
                    
                    const res = await fetch(`${API_BASE}/auth/login`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                        body: params
                    });

                    if (!res.ok) throw new Error("Invalid credentials");
                    const data = await res.json();
                    token = data.access_token;
                    localStorage.setItem("token", token);
                } else {
                    const res = await fetch(`${API_BASE}/auth/register`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ username, email, password })
                    });
                    if (!res.ok) {
                        const err = await res.json();
                        throw new Error(err.detail || "Registration failed");
                    }
                    // Auto login after register
                    const params = new URLSearchParams();
                    params.append('username', username);
                    params.append('password', password);
                    const loginRes = await fetch(`${API_BASE}/auth/login`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                        body: params
                    });
                    const data = await loginRes.json();
                    token = data.access_token;
                    localStorage.setItem("token", token);
                }
                
                toggleModal(false);
                await checkAuth();
            } catch (e) {
                authError.textContent = e.message;
            }
        };

        logoutBtn.onclick = () => {
            token = null;
            currentUser = null;
            localStorage.removeItem("token");
            updateAuthUI();
            startNewChat();
        };

        async function checkAuth() {
            if (!token) {
                updateAuthUI();
                return;
            }
            try {
                const res = await fetch(`${API_BASE}/auth/me`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (res.ok) {
                    currentUser = await res.json();
                    updateAuthUI();
                    loadUserSessions();
                } else {
                    throw new Error("Token expired");
                }
            } catch (e) {
                token = null;
                localStorage.removeItem("token");
                updateAuthUI();
            }
        }

        function updateAuthUI() {
            if (currentUser) {
                loginBtnSidebar.style.display = "none";
                userInfo.style.display = "flex";
                userNameDisplay.textContent = currentUser.username;
            } else {
                loginBtnSidebar.style.display = "block";
                userInfo.style.display = "none";
                sessionList.innerHTML = '<div style="text-align:center; padding:20px; font-size:12px; color:#888;">Log in to see past sessions</div>';
            }
        }

        async function loadUserSessions() {
            if (!token) return;
            try {
                const res = await fetch(`${API_BASE}/sessions`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (res.ok) {
                    const data = await res.json();
                    renderSessionList(data.sessions);
                }
            } catch (e) {
                console.error("Failed to load sessions", e);
            }
        }

        function renderSessionList(sessions) {
            sessionList.innerHTML = "";
            if (sessions.length === 0) {
                sessionList.innerHTML = '<div style="text-align:center; padding:20px; font-size:12px; color:#888;">No past sessions</div>';
                return;
            }
            
            sessions.forEach(s => {
                const div = document.createElement("div");
                div.className = `session-item ${s.session_id === sessionId ? 'active' : ''}`;
                div.textContent = s.title || 'Session ' + s.id;
                div.onclick = () => {
                    sessionId = s.session_id;
                    localStorage.setItem("session_id", sessionId);
                    loadHistory();
                    loadUserSessions(); // refresh active state
                };
                sessionList.appendChild(div);
            });
        }


        // Chat Logic
        userInput.addEventListener("keypress", function (e) {
            if (e.key === "Enter") sendMessage();
        });
        sendBtn.addEventListener("click", sendMessage);

        function startNewChat() {
            localStorage.removeItem("session_id");
            sessionId = null;
            chatMessages.innerHTML = "";
            addBotMessageInstant("Hi! I'm Chef Rolex. Tell me a dish and I'll walk you through it.");
            if (currentUser) loadUserSessions();
        }

        newChatBtn.addEventListener("click", startNewChat);
        newChatSidebarBtn.addEventListener("click", startNewChat);

        function addUserMessage(text) {
            const row = document.createElement("div");
            row.className = "user-row";
            const bubble = document.createElement("div");
            bubble.className = "user-bubble";
            bubble.textContent = text;
            row.appendChild(bubble);
            chatMessages.appendChild(row);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function addBotMessageInstant(text) {
            const row = document.createElement("div");
            row.className = "bot-row";
            const avatar = document.createElement("div");
            avatar.className = "bot-avatar";
            avatar.innerHTML = '<img src="logo.png" style="width:100%;height:100%;object-fit:contain;border-radius:50%;">';
            const wrap = document.createElement("div");
            const bubble = document.createElement("div");
            bubble.className = "bot-bubble";
            bubble.innerHTML = typeof marked !== 'undefined' ? marked.parse(text) : text;
            wrap.appendChild(bubble);
            row.appendChild(avatar);
            row.appendChild(wrap);
            chatMessages.appendChild(row);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function createStreamingBotBubble() {
            const row = document.createElement("div");
            row.className = "bot-row";

            const avatar = document.createElement("div");
            avatar.className = "bot-avatar";
            avatar.innerHTML = '<img src="logo.png" style="width:100%;height:100%;object-fit:contain;border-radius:50%;">';

            const wrap = document.createElement("div");

            const bubble = document.createElement("div");
            bubble.className = "bot-bubble";

            const cursor = document.createElement("span");
            cursor.className = "cursor-blink";
            bubble.appendChild(cursor);

            wrap.appendChild(bubble);
            row.appendChild(avatar);
            row.appendChild(wrap);
            chatMessages.appendChild(row);
            chatMessages.scrollTop = chatMessages.scrollHeight;

            return { bubble, cursor, wrap };
        }

        function finalizeBotBubble(bubble, cursor, wrap, fullText) {
            cursor.remove();

            const actions = document.createElement("div");
            actions.className = "msg-actions";

            const speakBtn = document.createElement("button");
            speakBtn.innerHTML = '<i class="ti ti-volume"></i>';
            speakBtn.title = "Read aloud";
            speakBtn.onclick = () => speakText(fullText);

            const copyBtn = document.createElement("button");
            copyBtn.innerHTML = '<i class="ti ti-copy"></i>';
            copyBtn.title = "Copy";
            copyBtn.onclick = () => navigator.clipboard.writeText(fullText);

            actions.appendChild(speakBtn);
            actions.appendChild(copyBtn);
            wrap.appendChild(actions);
        }

        async function sendMessage() {
            const message = userInput.value.trim();
            if (!message) return;

            addUserMessage(message);
            userInput.value = "";

            const { bubble, cursor, wrap } = createStreamingBotBubble();
            let fullText = "";

            try {
                const headers = { "Content-Type": "application/json" };
                if (token) headers["Authorization"] = `Bearer ${token}`;

                const response = await fetch(`${API_BASE}/chat/stream`, {
                    method: "POST",
                    headers: headers,
                    body: JSON.stringify({ message: message, session_id: sessionId })
                });

                if (!response.ok) {
                    throw new Error("Server returned " + response.status);
                }

                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let buffer = "";

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split("\n\n");
                    buffer = lines.pop();

                    for (const line of lines) {
                        if (line.startsWith("data: ")) {
                            const data = JSON.parse(line.slice(6));

                            if (data.type === "session") {
                                if (!sessionId || sessionId !== data.session_id) {
                                    sessionId = data.session_id;
                                    localStorage.setItem("session_id", sessionId);
                                    if (currentUser) loadUserSessions(); // refresh session list for new session
                                }
                            }

                            if (data.type === "chunk") {
                                fullText += data.content;
                                bubble.innerHTML = typeof marked !== 'undefined' ? marked.parse(fullText) : fullText;
                                bubble.appendChild(cursor);
                                chatMessages.scrollTop = chatMessages.scrollHeight;
                            }

                            if (data.type === "done") {
                                finalizeBotBubble(bubble, cursor, wrap, fullText);
                            }
                        }
                    }
                }

            } catch (error) {
                cursor.remove();
                bubble.textContent = "Oops! Something went wrong: " + error.message;
                console.error("Streaming error:", error);
            }
        }

        let recognition;
        let isListening = false;

        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.lang = "en-IN";

            recognition.onresult = function (event) {
                userInput.value = event.results[0][0].transcript;
            };

            recognition.onend = function () {
                isListening = false;
                micBtn.classList.remove("mic-active");
            };

            micBtn.addEventListener("click", function () {
                if (!isListening) {
                    recognition.start();
                    isListening = true;
                    micBtn.classList.add("mic-active");
                } else {
                    recognition.stop();
                }
            });
        } else {
            micBtn.style.display = "none";
        }

        function speakText(text) {
            if ('speechSynthesis' in window) {
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.lang = "en-IN";
                window.speechSynthesis.speak(utterance);
            }
        }

        async function loadHistory() {
            if (!sessionId) return;
            try {
                const res = await fetch(`${API_BASE}/chat/history/${sessionId}`);
                if (res.ok) {
                    const data = await res.json();
                    if (data.messages && data.messages.length > 0) {
                        chatMessages.innerHTML = ""; // clear default message
                        data.messages.forEach(msg => {
                            if (msg.role === "human") {
                                addUserMessage(msg.content);
                            } else {
                                addBotMessageInstant(msg.content);
                            }
                        });
                    }
                }
            } catch (err) {
                console.error("Failed to load history:", err);
            }
        }

        // Init
        window.addEventListener("DOMContentLoaded", async () => {
            await checkAuth();
            loadHistory();
        });