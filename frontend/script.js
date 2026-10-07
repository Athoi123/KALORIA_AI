// --- GLOBALS & STATE ---
let currentUser = null;
let dailyGoal = 2000;
let consumedCals = 0;
let foodHistory = [];
let dailyGoalMet = false;

async function apiRequest(path, payload = null) {
    const method = payload === null ? 'GET' : 'POST';
    const options = {
        method,
        headers: { 'Content-Type': 'application/json' }
    };

    if (payload !== null) {
        options.body = JSON.stringify(payload);
    }

    const response = await fetch(path, options);
    const data = await response.json().catch(() => ({}));

    if (!response.ok || data.status === 'error') {
        throw new Error(data.message || 'Request failed.');
    }

    return data;
}

function stripPassword(profile) {
    if (!profile) return null;
    const copy = { ...profile };
    delete copy.password;
    return copy;
}

// --- CORE FUNCTIONS ---
function updateDashboardStats() {
    document.getElementById('cals-consumed').innerText = consumedCals;
    document.getElementById('cals-goal').innerText = dailyGoal;

    const perc = Math.min((consumedCals / dailyGoal) * 100, 100);
    document.getElementById('cals-progress').style.width = perc + '%';

    if (consumedCals >= dailyGoal && !dailyGoalMet) {
        dailyGoalMet = true;
        alert('🎉 CONGRATULATIONS! You have met your daily calorie and nutrition target! 🎉');
    }

    const currentXP = parseInt(document.getElementById('dash-coins').innerText, 10) || 0;
    const level = Math.floor(currentXP / 100) + 1;
    const nextBoundary = level * 100;
    const diff = nextBoundary - currentXP;

    document.getElementById('next-achieve-level').innerText = `Level ${level}`;
    document.getElementById('next-achieve-xp').innerText = `${diff} XP to go`;

    const historyList = document.getElementById('food-history-list');
    if (foodHistory.length === 0) {
        historyList.innerHTML = '<p class="text-muted sm-text">No meals logged yet today.</p>';
    } else {
        historyList.innerHTML = '';
        foodHistory.forEach((item) => {
            historyList.innerHTML += `
                <div class="history-item">
                    <span>${item.name}</span>
                    <span class="mono-text">${item.cals} kcal</span>
                </div>
            `;
        });
    }
}

function createLeaves() {
    const container = document.getElementById('leaves-container');
    if (!container) return;
    for (let i = 0; i < 30; i++) {
        const leaf = document.createElement('div');
        leaf.className = 'leaf';
        leaf.style.left = Math.random() * 100 + 'vw';
        leaf.style.animationDuration = (Math.random() * 5 + 5) + 's';
        leaf.style.animationDelay = (Math.random() * 5) + 's';
        leaf.style.opacity = Math.random() * 0.5 + 0.1;
        leaf.style.transform = `scale(${Math.random() * 0.5 + 0.5})`;
        container.appendChild(leaf);
    }
}

window.addEventListener('DOMContentLoaded', () => {
    createLeaves();
    let loadPerc = 0;
    const loaderBar = document.getElementById('loader-bar');
    const loaderText = document.getElementById('loader-text');

    const interval = setInterval(() => {
        loadPerc += Math.floor(Math.random() * 15) + 5;
        if (loadPerc >= 100) {
            loadPerc = 100;
            clearInterval(interval);
            setTimeout(() => {
                const loaderScreen = document.getElementById('loader-screen');
                loaderScreen.style.opacity = '0';
                setTimeout(() => {
                    loaderScreen.style.display = 'none';
                    const auth = document.getElementById('auth-screen');
                    auth.style.display = 'flex';
                    setTimeout(() => auth.style.opacity = '1', 50);
                }, 1000);
            }, 500);
        }
        if (loaderBar) loaderBar.style.width = loadPerc + '%';
        if (loaderText) loaderText.innerText = `Initializing Systems: ${loadPerc}%`;
    }, 200);
});

const authLoginPanel = document.getElementById('login-panel');
const authRegisterPanel = document.getElementById('register-panel');

function showLoginPanel() {
    if (authLoginPanel) authLoginPanel.style.display = 'block';
    if (authRegisterPanel) authRegisterPanel.style.display = 'none';
}

function showRegisterPanel() {
    if (authLoginPanel) authLoginPanel.style.display = 'none';
    if (authRegisterPanel) authRegisterPanel.style.display = 'block';
}

if (authLoginPanel && authRegisterPanel) {
    showLoginPanel();

    document.getElementById('to-register').addEventListener('click', (e) => {
        e.preventDefault();
        showRegisterPanel();
    });

    document.getElementById('to-login').addEventListener('click', (e) => {
        e.preventDefault();
        showLoginPanel();
    });
}

function enterDashboard(userParams) {
    currentUser = userParams;
    localStorage.setItem('kaloria_current_user', JSON.stringify(currentUser));

    document.getElementById('dash-name').innerText = currentUser.name || 'User';
    document.getElementById('dash-mode').innerText = currentUser.condition && currentUser.condition !== 'none'
        ? `${currentUser.condition.toUpperCase()} MODE`
        : 'NORMAL MODE';

    const alertElement = document.getElementById('system-alert-text');
    if (alertElement && currentUser.condition && currentUser.condition !== 'none') {
        alertElement.innerText = `Active ${currentUser.condition} protocol. Adjusting iron, folic acid, and daily caloric recommendations for optimal health.`;
    }

    const savedAvatar = localStorage.getItem('kaloria_avatar');
    if (savedAvatar) {
        document.getElementById('sidebar-avatar').src = savedAvatar;
    }

    const auth = document.getElementById('auth-screen');
    auth.style.opacity = '0';
    setTimeout(() => {
        auth.style.display = 'none';
        const dash = document.getElementById('app-dashboard');
        dash.style.display = 'grid';
        setTimeout(() => dash.style.opacity = '1', 50);
        document.body.style.overflow = 'auto';
        updateDashboardStats();
    }, 1000);
}

async function handleLogin() {
    const email = document.getElementById('auth-email').value.trim();
    const pass = document.getElementById('auth-password').value;

    if (!email || !pass) {
        alert('Enter email and password.');
        return;
    }

    try {
        const response = await apiRequest('/api/auth/login', { email, password: pass });
        const profile = response.data;
        profile.password = pass;
        localStorage.setItem('kaloria_profile', JSON.stringify(profile));
        enterDashboard(profile);
    } catch (error) {
        alert(error.message || 'Incorrect email or password.');
    }
}

async function handleRegister() {
    const name = document.getElementById('reg-name').value.trim();
    const email = document.getElementById('reg-email').value.trim();
    const password = document.getElementById('reg-password').value;
    const age = parseInt(document.getElementById('reg-age').value, 10);
    const weight = parseInt(document.getElementById('reg-weight').value, 10);
    const job = document.getElementById('reg-job').value;
    const condition = document.getElementById('reg-condition').value;

    if (!name || !email || !password || !age || !weight) {
        alert('Please fill all base metrics, including Email and Password.');
        return;
    }

    try {
        const response = await apiRequest('/api/auth/register', { name, email, password, age, weight, job, condition });
        const profile = response.data;
        profile.password = password;
        localStorage.setItem('kaloria_profile', JSON.stringify(profile));
        enterDashboard(profile);
    } catch (error) {
        alert(error.message || 'Could not create your profile.');
    }
}

document.getElementById('login-btn').addEventListener('click', handleLogin);
document.getElementById('register-btn').addEventListener('click', handleRegister);

const navItems = document.querySelectorAll('.menu-item');
const views = document.querySelectorAll('.view-container');

navItems.forEach((item) => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        navItems.forEach((nav) => nav.classList.remove('active'));
        item.classList.add('active');

        const target = item.getAttribute('data-target');
        views.forEach((view) => {
            view.style.display = 'none';
        });
        const targetView = document.getElementById('view-' + target);
        if (targetView) targetView.style.display = 'block';

        document.getElementById('view-title').innerText = item.innerText;
    });
});

document.getElementById('profile-edit-btn').addEventListener('click', () => {
    if (currentUser) {
        document.getElementById('edit-name').value = currentUser.name || '';
        document.getElementById('edit-age').value = currentUser.age || '';
        document.getElementById('edit-weight').value = currentUser.weight || '';
        document.getElementById('edit-job').value = currentUser.job || 'desk_job';
        document.getElementById('edit-condition').value = currentUser.condition || 'none';
    }
    document.getElementById('profile-modal').style.display = 'flex';
});

document.getElementById('close-profile-btn').addEventListener('click', () => {
    document.getElementById('profile-modal').style.display = 'none';
});

async function saveProfileChanges() {
    const name = document.getElementById('edit-name').value.trim();
    const age = parseInt(document.getElementById('edit-age').value, 10);
    const weight = parseInt(document.getElementById('edit-weight').value, 10);
    const job = document.getElementById('edit-job').value;
    const condition = document.getElementById('edit-condition').value;

    if (!name || !age || !weight) {
        alert('Please fill all fields.');
        return;
    }

    const updatedProfile = {
        ...currentUser,
        name,
        age,
        weight,
        job,
        condition,
        password: currentUser?.password || ''
    };

    try {
        const response = await apiRequest('/api/auth/update-profile', updatedProfile);
        const profile = response.data;
        profile.password = updatedProfile.password;
        localStorage.setItem('kaloria_profile', JSON.stringify(profile));
        document.getElementById('profile-modal').style.display = 'none';
        enterDashboard(profile);
    } catch (error) {
        alert(error.message || 'Saving profile failed.');
    }
}

document.getElementById('save-profile-btn').addEventListener('click', saveProfileChanges);

document.getElementById('quick-log').addEventListener('click', async () => {
    const foodName = prompt('Enter food name:');
    if (!foodName) return;

    const weightInput = prompt('Enter weight in grams:');
    const weightG = parseInt(weightInput, 10);
    if (Number.isNaN(weightG) || weightG <= 0) return;

    try {
        const response = await apiRequest('/api/estimate-food', {
            food_name: foodName,
            weight_g: weightG
        });

        const finalCals = response.data.calories;
        consumedCals += finalCals;
        foodHistory.push({ name: `${foodName} (${weightG}g)`, cals: finalCals });

        if (currentUser && currentUser.email) {
            await apiRequest('/api/food-log', {
                user_email: currentUser.email,
                food_name: foodName,
                calories: finalCals,
                protein: 0,
                carbs: 0,
                fat: 0
            });
        }

        document.getElementById('dash-coins').innerText = parseInt(document.getElementById('dash-coins').innerText, 10) + 10;
        updateDashboardStats();
    } catch (error) {
        alert(error.message || 'USDA lookup failed.');
    }
});

document.getElementById('streak-7-btn').addEventListener('click', () => {
    alert('7-Day Streak Initiated! Stay consistent to earn your reward.');
    document.getElementById('dash-streak').innerText = '0';
});

document.getElementById('streak-30-btn').addEventListener('click', () => {
    alert('30-Day Routine Initiated! Hardcore mode activated.');
    document.getElementById('dash-streak').innerText = '0';
});

document.getElementById('avatar-upload').addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        const file = e.target.files[0];
        const reader = new FileReader();
        reader.onloadend = () => {
            const base64Str = reader.result;
            document.getElementById('sidebar-avatar').src = base64Str;
            localStorage.setItem('kaloria_avatar', base64Str);
        };
        reader.readAsDataURL(file);
    }
});

const fileInput = document.getElementById('food-image-input');
const fileName = document.getElementById('file-name');
const analyzeBtn = document.getElementById('analyze-vision-btn');
let selectedFileBase64 = null;

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        const file = e.target.files[0];
        fileName.innerText = file.name;
        analyzeBtn.disabled = false;

        const reader = new FileReader();
        reader.onloadend = () => {
            selectedFileBase64 = reader.result;
            const preview = document.getElementById('food-preview');
            preview.src = selectedFileBase64;
            preview.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }
});

analyzeBtn.addEventListener('click', async () => {
    const selectedFile = fileInput.files[0];
    if (!selectedFile) return;

    analyzeBtn.innerHTML = '<i class="ph ph-spinner ph-spin"></i> SCANNING (CAN TAKE ~1 MIN)...';
    const resultsBox = document.getElementById('scan-results');
    const messageEl = document.getElementById('scan-message');
    const detailsEl = document.getElementById('scan-details');
    const logBtn = document.getElementById('confirm-log-btn');

    try {
        // The browser sets the multipart Content-Type/boundary itself.
        const formData = new FormData();
        formData.append('file', selectedFile);
        const response = await fetch('/api/scan-food', { method: 'POST', body: formData });
        const result = await response.json();

        const statusMessages = {
            not_food: 'No food was detected in this image. Please upload a clear food image.',
            nutrition_lookup_error: 'Food detected, but nutritional information could not be retrieved.',
            nutrition_data_error: 'Food was identified, but nutrition data could not be calculated.'
        };

        resultsBox.style.display = 'block';
        if (result.status === 'success') {
            document.getElementById('scan-food-name').innerText = result.food_name;
            document.getElementById('scan-calories').innerText = result.calories;
            document.getElementById('scan-protein').innerText = `${result.protein}g`;
            document.getElementById('scan-carbs').innerText = `${result.carbs}g`;
            document.getElementById('scan-fat').innerText = `${result.fat}g`;
            document.getElementById('scan-portion').innerText = `${result.estimated_portion_grams}g`;
            document.getElementById('scan-confidence').innerText = result.confidence_score;
            messageEl.style.display = 'none';
            detailsEl.style.display = 'block';
            logBtn.style.display = '';
        } else {
            messageEl.innerText = statusMessages[result.status] || result.message || result.notes || 'Scan failed.';
            messageEl.style.display = 'block';
            detailsEl.style.display = 'none';
            logBtn.style.display = 'none';
        }
    } catch (error) {
        console.error('Neural scan failed:', error);
        alert('Neural scan failed.');
    } finally {
        analyzeBtn.innerHTML = 'INITIALIZE SCAN';
    }
});


document.getElementById('confirm-log-btn').addEventListener('click', async () => {
    const identifiedFood = document.getElementById('scan-food-name').innerText;
    const addCals = parseInt(document.getElementById('scan-calories').innerText, 10);

    consumedCals += addCals;
    foodHistory.push({ name: identifiedFood, cals: addCals });
    if (currentUser && currentUser.email) {
        try {
            await apiRequest('/api/food-log', {
                user_email: currentUser.email,
                food_name: identifiedFood,
                calories: addCals,
                protein: parseInt(document.getElementById('scan-protein').innerText, 10) || 0,
                carbs: Math.round(parseFloat(document.getElementById('scan-carbs').innerText)) || 0,
                fat: Math.round(parseFloat(document.getElementById('scan-fat').innerText)) || 0
            });
        } catch (error) {
            console.error('Meal log persistence failed:', error);
        }
    }

    updateDashboardStats();
    document.getElementById('scan-results').style.display = 'none';
    document.getElementById('food-preview').style.display = 'none';
    fileName.innerText = 'No file selected';
    analyzeBtn.disabled = true;
    document.getElementById('dash-coins').innerText = parseInt(document.getElementById('dash-coins').innerText, 10) + 50;
    document.querySelector('[data-target="home"]').click();
});

const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-chat-btn');
const history = document.getElementById('chat-history');

async function sendChat() {
    const text = chatInput.value.trim();
    if (!text) return;

    history.innerHTML += `
        <div class="chat-msg user">
            <div class="msg-bubble">${text}</div>
        </div>
    `;
    chatInput.value = '';
    history.scrollTop = history.scrollHeight;

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_message: text,
                user_profile: currentUser || {}
            })
        });
        const data = await response.json();

        history.innerHTML += `
            <div class="chat-msg bot">
                <div class="msg-bubble">${(data.reply || 'No answer available.').replace(/\n/g, '<br>')}</div>
            </div>
        `;
        history.scrollTop = history.scrollHeight;
    } catch (error) {
        console.error(error);
        history.innerHTML += `
            <div class="chat-msg bot">
                <div class="msg-bubble" style="color:var(--warning)">Connection error. Cannot reach AI Core.</div>
            </div>
        `;
    }
}

sendBtn.addEventListener('click', sendChat);
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendChat();
});
