// API 基础URL - 自动检测当前域名和端口
const API_BASE = window.location.origin; // 自动使用当前访问的域名和端口

// 全局状态
let currentPage = 'chat';
let currentSalesId = 'sales_001';
let currentUser = null;
let authToken = null;

// 从localStorage加载token
if (typeof Storage !== 'undefined') {
    authToken = localStorage.getItem('auth_token');
    const savedUser = localStorage.getItem('current_user');
    if (savedUser) {
        try {
            currentUser = JSON.parse(savedUser);
            currentSalesId = currentUser.id;
        } catch (e) {
            console.error('Failed to parse saved user:', e);
        }
    }
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    initAuth();
    initNavigation();
    initChat();
    initKnowledge();
    initScripts();
    initDashboard();
    initInsights();
    
    // 检查登录状态
    if (!authToken) {
        showLoginModal();
    } else {
        // 验证token是否有效
        verifyAuth();
    }
    
    // 加载仪表板数据
    if (authToken) {
        loadDashboard();
    }
});

// 认证功能
function initAuth() {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const loginModal = document.getElementById('login-modal');
    const closeLoginBtn = document.getElementById('close-login');
    const showRegisterLink = document.getElementById('show-register');
    const showLoginLink = document.getElementById('show-login');
    const logoutBtn = document.getElementById('logout-btn');
    
    // 登录表单
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('login-username').value;
            const password = document.getElementById('login-password').value;
            
            showLoading();
            
            try {
                const res = await fetch(`${API_BASE}/api/auth/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });
                
                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.detail || '登入失敗');
                }
                
                const data = await res.json();
                authToken = data.access_token;
                currentUser = data.user;
                currentSalesId = currentUser.id;
                
                // 保存到localStorage
                if (typeof Storage !== 'undefined') {
                    localStorage.setItem('auth_token', authToken);
                    localStorage.setItem('current_user', JSON.stringify(currentUser));
                }
                
                hideLoginModal();
                updateUserUI();
                showToast('登入成功！', 'success');
                hideLoading();
            } catch (error) {
                showToast(`登入失敗：${error.message}`, 'error');
                hideLoading();
            }
        });
    }
    
    // 注册表单
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('register-username').value;
            const password = document.getElementById('register-password').value;
            const email = document.getElementById('register-email').value;
            const fullName = document.getElementById('register-fullname').value;
            const role = document.getElementById('register-role').value;
            
            showLoading();
            
            try {
                const res = await fetch(`${API_BASE}/api/auth/register`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        username,
                        password,
                        email: email || null,
                        full_name: fullName || null,
                        role
                    })
                });
                
                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.detail || '註冊失敗');
                }
                
                const data = await res.json();
                authToken = data.access_token;
                currentUser = data.user;
                currentSalesId = currentUser.id;
                
                // 保存到localStorage
                if (typeof Storage !== 'undefined') {
                    localStorage.setItem('auth_token', authToken);
                    localStorage.setItem('current_user', JSON.stringify(currentUser));
                }
                
                hideLoginModal();
                updateUserUI();
                showToast('註冊成功！', 'success');
                hideLoading();
            } catch (error) {
                showToast(`註冊失敗：${error.message}`, 'error');
                hideLoading();
            }
        });
    }
    
    // 切换登录/注册视图
    if (showRegisterLink) {
        showRegisterLink.addEventListener('click', (e) => {
            e.preventDefault();
            document.getElementById('login-form-view').style.display = 'none';
            document.getElementById('register-form-view').style.display = 'block';
        });
    }
    
    if (showLoginLink) {
        showLoginLink.addEventListener('click', (e) => {
            e.preventDefault();
            document.getElementById('register-form-view').style.display = 'none';
            document.getElementById('login-form-view').style.display = 'block';
        });
    }
    
    // 关闭模态框
    if (closeLoginBtn) {
        closeLoginBtn.addEventListener('click', hideLoginModal);
    }
    
    if (loginModal) {
        loginModal.addEventListener('click', (e) => {
            if (e.target === loginModal) {
                hideLoginModal();
            }
        });
    }
    
    // 登出
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            authToken = null;
            currentUser = null;
            currentSalesId = null;
            
            if (typeof Storage !== 'undefined') {
                localStorage.removeItem('auth_token');
                localStorage.removeItem('current_user');
            }
            
            updateUserUI();
            showLoginModal();
            showToast('已登出', 'success');
        });
    }
}

function showLoginModal() {
    const modal = document.getElementById('login-modal');
    if (modal) {
        modal.classList.add('show');
        document.getElementById('login-form-view').style.display = 'block';
        document.getElementById('register-form-view').style.display = 'none';
    }
}

function hideLoginModal() {
    const modal = document.getElementById('login-modal');
    if (modal) {
        modal.classList.remove('show');
    }
}

function updateUserUI() {
    const userInfo = document.getElementById('user-info');
    const usernameDisplay = document.getElementById('username-display');
    const logoutBtn = document.getElementById('logout-btn');
    
    if (currentUser && authToken) {
        if (userInfo) userInfo.style.display = 'flex';
        if (usernameDisplay) usernameDisplay.textContent = currentUser.full_name || currentUser.username;
        if (logoutBtn) logoutBtn.style.display = 'block';
    } else {
        if (userInfo) userInfo.style.display = 'none';
        if (logoutBtn) logoutBtn.style.display = 'none';
    }
}

async function verifyAuth() {
    if (!authToken) return false;
    
    try {
        const res = await fetch(`${API_BASE}/api/auth/me`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (!res.ok) {
            // Token无效，清除
            authToken = null;
            currentUser = null;
            if (typeof Storage !== 'undefined') {
                localStorage.removeItem('auth_token');
                localStorage.removeItem('current_user');
            }
            updateUserUI();
            showLoginModal();
            return false;
        }
        
        const userData = await res.json();
        currentUser = userData;
        currentSalesId = userData.id;
        updateUserUI();
        return true;
    } catch (error) {
        console.error('Auth verification error:', error);
        return false;
    }
}

// 添加认证头到fetch请求的辅助函数
function getAuthHeaders() {
    const headers = { 'Content-Type': 'application/json' };
    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }
    return headers;
}

// 导航功能
function initNavigation() {
    const navButtons = document.querySelectorAll('.nav-btn');
    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const page = btn.dataset.page;
            switchPage(page);
        });
    });
}

function switchPage(page) {
    // 更新导航
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.page === page);
    });
    
    // 更新页面
    document.querySelectorAll('.page').forEach(p => {
        p.classList.toggle('active', p.id === `${page}-page`);
    });
    
    currentPage = page;
    
    // 页面特定初始化
    if (page === 'dashboard') {
        loadDashboard();
    }
}

// 对话功能
function initChat() {
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const salesIdInput = document.getElementById('sales-id');
    
    // 更新销售员ID显示（从当前用户）
    if (currentUser && salesIdInput) {
        salesIdInput.value = currentUser.full_name || currentUser.username;
    }
    
    // 发送消息
    function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;
        
        const customerType = document.getElementById('customer-type').value;
        
        // 添加用户消息到界面
        addMessage('user', message);
        chatInput.value = '';
        
        // 禁用发送按钮
        sendBtn.disabled = true;
        showLoading();
        
        // 检查登录状态
        if (!authToken) {
            showLoginModal();
            sendBtn.disabled = false;
            hideLoading();
            return;
        }
        
        // 发送API请求
        fetch(`${API_BASE}/api/chat`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                message: message,
                sales_id: currentSalesId || currentUser.id,
                customer_type: customerType || null
            })
        })
        .then(res => {
            if (!res.ok) {
                return res.json().then(err => {
                    throw new Error(err.detail || `HTTP ${res.status}: ${res.statusText}`);
                });
            }
            return res.json();
        })
        .then(data => {
            // 添加AI回复
            if (data && data.response) {
                addMessage('assistant', data.response, data.suggestions || []);
            } else {
                throw new Error('回應格式錯誤：缺少 response 欄位');
            }
            hideLoading();
            sendBtn.disabled = false;
        })
        .catch(error => {
            console.error('Error:', error);
            showToast(`傳送失敗：${error.message || '請重試'}`, 'error');
            hideLoading();
            sendBtn.disabled = false;
        });
    }
    
    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
}

function addMessage(role, content, suggestions = []) {
    const messagesContainer = document.getElementById('chat-messages');
    
    // 移除欢迎消息
    const welcomeMsg = messagesContainer.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = role === 'user' 
        ? '<i class="fas fa-user"></i>' 
        : '<i class="fas fa-robot"></i>';
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.textContent = content;
    
    messageContent.appendChild(bubble);
    
    // 添加建议
    if (suggestions && suggestions.length > 0) {
        const suggestionsDiv = document.createElement('div');
        suggestionsDiv.className = 'message-suggestions';
        
        const title = document.createElement('div');
        title.className = 'message-suggestions-title';
        title.textContent = '💡 相關建議：';
        suggestionsDiv.appendChild(title);
        
        suggestions.forEach(suggestion => {
            const tag = document.createElement('span');
            tag.className = 'suggestion-tag';
            tag.textContent = suggestion;
            suggestionsDiv.appendChild(tag);
        });
        
        messageContent.appendChild(suggestionsDiv);
    }
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(messageContent);
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// 知识库功能
function initKnowledge() {
    const searchBtn = document.getElementById('search-btn');
    const searchInput = document.getElementById('search-query');
    const addForm = document.getElementById('add-content-form');
    
    // 搜索
    function search() {
        const query = searchInput.value.trim();
        if (!query) {
            showToast('請輸入搜尋關鍵詞', 'error');
            return;
        }
        
        showLoading();
        
        fetch(`${API_BASE}/api/knowledge/content?query=${encodeURIComponent(query)}&page=1&page_size=10`, {
            headers: getAuthHeaders()
        })
            .then(res => res.json())
            .then(data => {
                displayKnowledgeResults(data.items);
                hideLoading();
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('搜尋失敗', 'error');
                hideLoading();
            });
    }
    
    searchBtn.addEventListener('click', search);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            search();
        }
    });
    
    // 添加内容
    addForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const title = document.getElementById('content-title').value;
        const content = document.getElementById('content-text').value;
        const contentType = document.getElementById('content-type').value;
        const tags = document.getElementById('content-tags').value
            .split(',')
            .map(t => t.trim())
            .filter(t => t);
        
        showLoading();
        
        fetch(`${API_BASE}/api/knowledge/content`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                title: title,
                content: content,
                content_type: contentType,
                tags: tags,
                created_by: 'trainer_001'
            })
        })
        .then(res => res.json())
        .then(data => {
            showToast('內容新增成功！', 'success');
            addForm.reset();
            // 自动搜索新添加的内容
            document.getElementById('search-query').value = title;
            search();
            hideLoading();
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('新增失敗', 'error');
            hideLoading();
        });
    });
}

function displayKnowledgeResults(items) {
    const resultsContainer = document.getElementById('knowledge-results');
    
    if (!items || items.length === 0) {
        resultsContainer.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-search"></i>
                <p>未找到相關內容</p>
            </div>
        `;
        return;
    }
    
    resultsContainer.innerHTML = items.map(item => `
        <div class="content-card">
            <div class="content-card-header">
                <div class="content-card-title">${escapeHtml(item.title)}</div>
                <div class="content-type-badge">${getContentTypeName(item.content_type)}</div>
            </div>
            <div class="content-card-body">${escapeHtml(item.content)}</div>
            <div class="content-tags">
                ${item.tags.map(tag => `<span class="tag">${escapeHtml(tag)}</span>`).join('')}
            </div>
        </div>
    `).join('');
}

function getContentTypeName(type) {
    const names = {
        'training_material': '培訓材料',
        'sales_script': '銷售話術',
        'qa': '問答對',
        'best_practice': '最佳實踐'
    };
    return names[type] || type;
}

// 话术生成功能
function initScripts() {
    const generateForm = document.getElementById('generate-script-form');
    
    generateForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const scenario = document.getElementById('script-scenario').value;
        const customerType = document.getElementById('script-customer-type').value;
        const requirements = document.getElementById('script-requirements').value;
        
        showLoading();
        
        fetch(`${API_BASE}/api/scripts/generate`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                scenario: scenario,
                customer_type: customerType || null,
                requirements: requirements || null
            })
        })
        .then(res => res.json())
        .then(data => {
            displayScript(data);
            hideLoading();
            showToast('話術生成成功！', 'success');
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('生成失敗', 'error');
            hideLoading();
        });
    });
}

function displayScript(script) {
    const resultsContainer = document.getElementById('script-results');
    
    let variantsHtml = '';
    if (script.variants && script.variants.length > 0) {
        variantsHtml = `
            <div class="script-variants">
                <div class="script-variants-title">💡 話術變體：</div>
                ${script.variants.map((variant, index) => `
                    <div class="variant-item">
                        <strong>變體 ${index + 1}：</strong>
                        <div style="margin-top: 0.5rem; white-space: pre-wrap;">${escapeHtml(variant)}</div>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    resultsContainer.innerHTML = `
        <div class="script-card">
            <div class="script-card-header">
                <div class="script-card-title">${escapeHtml(script.title)}</div>
            </div>
            <div class="script-content">${escapeHtml(script.script)}</div>
            ${variantsHtml}
        </div>
    `;
}

// 仪表板功能
function initDashboard() {
    // 在switchPage时已经调用loadDashboard
}

function loadDashboard() {
    fetch(`${API_BASE}/api/analytics/dashboard`, {
        headers: getAuthHeaders()
    })
        .then(res => res.json())
        .then(data => {
            document.getElementById('stat-conversations').textContent = data.total_conversations || 0;
            document.getElementById('stat-sales').textContent = data.active_sales || 0;
            document.getElementById('stat-content').textContent = data.total_content || 0;
            document.getElementById('stat-scripts').textContent = data.total_scripts || 0;
            
            // 显示最佳话术
            const topScriptsContainer = document.getElementById('top-scripts');
            if (data.top_performing_scripts && data.top_performing_scripts.length > 0) {
                topScriptsContainer.innerHTML = data.top_performing_scripts.map(script => `
                    <div class="script-stat-item">
                        <div class="script-stat-info">
                            <div class="script-stat-title">${escapeHtml(script.title)}</div>
                            <div class="script-stat-meta">
                                使用次數: ${script.usage_count} | 
                                成功率: ${(script.success_rate * 100).toFixed(1)}%
                            </div>
                        </div>
                        <div class="script-stat-badge">
                            ${(script.success_rate * 100).toFixed(0)}%
                        </div>
                    </div>
                `).join('');
            } else {
                topScriptsContainer.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-chart-bar"></i>
                        <p>暫無話術數據</p>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('載入數據失敗', 'error');
        });
}

// 学习洞察功能
function initInsights() {
    const loadBtn = document.getElementById('load-insights-btn');
    
    loadBtn.addEventListener('click', () => {
        const salesId = document.getElementById('insights-sales-id').value.trim();
        if (!salesId) {
            showToast('請輸入業務員ID', 'error');
            return;
        }
        
        showLoading();
        
        fetch(`${API_BASE}/api/learning/insights/${salesId}`, {
            headers: getAuthHeaders()
        })
            .then(res => res.json())
            .then(data => {
                displayInsights(data);
                hideLoading();
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('載入失敗', 'error');
                hideLoading();
            });
    });
}

function displayInsights(data) {
    const container = document.getElementById('insights-content');
    
    if (!data.suggestions || data.suggestions.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-lightbulb"></i>
                <p>暫無學習洞察</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = data.suggestions.map(suggestion => {
        let type = 'pattern';
        let typeName = '模式';
        if (suggestion.includes('建議加強')) {
            type = 'improvement';
            typeName = '改進';
        } else if (suggestion.includes('優勢')) {
            type = 'strength';
            typeName = '優勢';
        }
        
        return `
            <div class="insight-card ${type}">
                <div class="insight-type">${typeName}</div>
                <div class="insight-content">${escapeHtml(suggestion)}</div>
            </div>
        `;
    }).join('');
}

// 工具函数
function showLoading() {
    document.getElementById('loading').classList.add('show');
}

function hideLoading() {
    document.getElementById('loading').classList.remove('show');
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

