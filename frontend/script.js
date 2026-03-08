// --- GLOBALS & STATE ---
let currentUser = null;
let dailyGoal = 2000;
let consumedCals = 0;
let foodHistory = [];
let dailyGoalMet = false;

// --- CORE FUNCTIONS ---
function updateDashboardStats() {
    document.getElementById('cals-consumed').innerText = consumedCals;
    document.getElementById('cals-goal').innerText = dailyGoal;
    
    let perc = Math.min((consumedCals / dailyGoal) * 100, 100);
    document.getElementById('cals-progress').style.width = perc + '%';
    
    if(consumedCals >= dailyGoal && !dailyGoalMet) {
        dailyGoalMet = true;
        alert("🎉 CONGRATULATIONS! You have met your daily calorie and nutrition target! 🎉");
    }
    
    // Dynamic Next Achievement based on XP
    const currentXP = parseInt(document.getElementById('dash-coins').innerText);
    const level = Math.floor(currentXP / 100) + 1;
    const nextBoundary = level * 100;
    const diff = nextBoundary - currentXP;
    
    document.getElementById('next-achieve-level').innerText = `Level ${level}`;
    document.getElementById('next-achieve-xp').innerText = `${diff} XP to go`;

    // Update History UI
    const historyList = document.getElementById('food-history-list');
    if(foodHistory.length === 0) {
        historyList.innerHTML = '<p class="text-muted sm-text">No meals logged yet today.</p>';
    } else {
        historyList.innerHTML = '';
        foodHistory.forEach(item => {
            historyList.innerHTML += `
                <div class="history-item">
                    <span>${item.name}</span>
                    <span class="mono-text">${item.cals} kcal</span>
                </div>
            `;
        });
    }
}

// Background Leaves Generator
function createLeaves() {
    const container = document.getElementById('leaves-container');
    if (!container) return;
    for(let i=0; i<30; i++) {
        let leaf = document.createElement('div');
        leaf.className = 'leaf';
        leaf.style.left = Math.random() * 100 + 'vw';
        leaf.style.animationDuration = (Math.random() * 5 + 5) + 's';
        leaf.style.animationDelay = (Math.random() * 5) + 's';
        leaf.style.opacity = Math.random() * 0.5 + 0.1;
        leaf.style.transform = `scale(${Math.random() * 0.5 + 0.5})`;
        container.appendChild(leaf);
    }
}

// --- BOOT SEQUENCE (LOADER) ---
window.addEventListener('DOMContentLoaded', () => {
    createLeaves();
    let loadPerc = 0;
    const loaderBar = document.getElementById('loader-bar');
    const loaderText = document.getElementById('loader-text');
    
    const interval = setInterval(() => {
        loadPerc += Math.floor(Math.random() * 15) + 5;
        if(loadPerc >= 100) {
            loadPerc = 100;
            clearInterval(interval);
            setTimeout(() => {
                document.getElementById('loader-screen').style.opacity = '0';
                setTimeout(() => {
                    document.getElementById('loader-screen').style.display = 'none';
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

// --- AUTH LOGIC ---
document.getElementById('to-register').addEventListener('click', (e) => {
    e.preventDefault();
    document.getElementById('login-panel').style.display = 'none';
    document.getElementById('register-panel').style.display = 'block';
});
document.getElementById('to-login').addEventListener('click', (e) => {
    e.preventDefault();
    document.getElementById('register-panel').style.display = 'none';
    document.getElementById('login-panel').style.display = 'block';
});

function enterDashboard(userParams) {
    currentUser = userParams;
    
    document.getElementById('dash-name').innerText = currentUser.name || "User";
    if (currentUser.condition && currentUser.condition !== "none") {
        document.getElementById('dash-mode').innerText = currentUser.condition.toUpperCase() + " MODE";
        document.getElementById('system-alert-text').innerText = `Active ${currentUser.condition} protocol. Adjusting iron, folic acid, and daily caloric recommendations for optimal health.`;
    }

    const savedAvatar = localStorage.getItem('kaloria_avatar');
    if(savedAvatar) {
        document.getElementById('sidebar-avatar').src = savedAvatar;
    }

    const auth = document.getElementById('auth-screen');
    auth.style.opacity = '0';
    setTimeout(() => {
        auth.style.display = 'none';
        const dash = document.getElementById('app-dashboard');
        dash.style.display = 'grid';
        setTimeout(() => dash.style.opacity = '1', 50);
        document.body.style.overflow = 'auto'; // allow scroll
        updateDashboardStats(); 
    }, 1000);
}

document.getElementById('login-btn').addEventListener('click', () => {
    const email = document.getElementById('auth-email').value;
    const pass = document.getElementById('auth-password').value;
    
    if(!email || !pass) {
        alert("Enter email and password.");
        return;
    }

    const savedProfileStr = localStorage.getItem('kaloria_profile');
    if(savedProfileStr) {
        const savedProfile = JSON.parse(savedProfileStr);
        if(savedProfile.email === email && savedProfile.password === pass) {
            enterDashboard(savedProfile);
        } else {
            alert("Incorrect email or password.");
        }
    } else {
        alert("No account found. Please initialize a profile first.");
    }
});

document.getElementById('register-btn').addEventListener('click', () => {
    const name = document.getElementById('reg-name').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;
    const age = parseInt(document.getElementById('reg-age').value);
    const weight = parseInt(document.getElementById('reg-weight').value);
    const job = document.getElementById('reg-job').value;
    const condition = document.getElementById('reg-condition').value;
    
    if(!name || !email || !password || !age || !weight) {
        alert("Please fill all base metrics, including Email and Password.");
        return;
    }
    
    const profile = { name, email, password, age, weight, job, condition };
    localStorage.setItem('kaloria_profile', JSON.stringify(profile));
    
    enterDashboard(profile);
});

// --- NAVIGATION LOGIC ---
const navItems = document.querySelectorAll('.menu-item');
const views = document.querySelectorAll('.view-container');

navItems.forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        navItems.forEach(nav => nav.classList.remove('active'));
        item.classList.add('active');
        
        const target = item.getAttribute('data-target');
        views.forEach(view => view.style.display = 'none');
        document.getElementById('view-' + target).style.display = 'block';
        
        document.getElementById('view-title').innerText = item.innerText;
    });
});

// --- PROFILE EDITING ---
document.getElementById('profile-edit-btn').addEventListener('click', () => {
    if(currentUser) {
        document.getElementById('edit-name').value = currentUser.name || "";
        document.getElementById('edit-age').value = currentUser.age || "";
        document.getElementById('edit-weight').value = currentUser.weight || "";
        document.getElementById('edit-job').value = currentUser.job || "desk_job";
        document.getElementById('edit-condition').value = currentUser.condition || "none";
    }
    document.getElementById('profile-modal').style.display = 'flex';
});

document.getElementById('close-profile-btn').addEventListener('click', () => {
    document.getElementById('profile-modal').style.display = 'none';
});

document.getElementById('save-profile-btn').addEventListener('click', () => {
    const name = document.getElementById('edit-name').value;
    const age = parseInt(document.getElementById('edit-age').value);
    const weight = parseInt(document.getElementById('edit-weight').value);
    const job = document.getElementById('edit-job').value;
    const condition = document.getElementById('edit-condition').value;
    
    if(!name || !age || !weight) {
        alert("Please fill all fields.");
        return;
    }
    
    let updatedProfile = { ...currentUser, name, age, weight, job, condition };
    localStorage.setItem('kaloria_profile', JSON.stringify(updatedProfile));
    
    document.getElementById('profile-modal').style.display = 'none';
    enterDashboard(updatedProfile);
});

// --- QUICK ACTIONS & VAULT ---
document.getElementById('quick-log').addEventListener('click', async () => {
    const foodName = prompt("Enter food name:");
    if(!foodName) return;
    const weightInput = prompt("Enter weight in grams:");
    const weightG = parseInt(weightInput);
    if(isNaN(weightG) || weightG <= 0) return;
    
    try {
        const res = await fetch('/api/estimate-food', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ food_name: foodName, weight_g: weightG })
        });
        const data = await res.json();
        
        if(data.status === 'success') {
            const finalCals = data.data.calories;
            consumedCals += finalCals;
            foodHistory.push({ name: `${foodName} (${weightG}g)`, cals: finalCals });
            document.getElementById('dash-coins').innerText = parseInt(document.getElementById('dash-coins').innerText) + 10;
            updateDashboardStats();
        } else {
            alert("USDA lookup failed.");
        }
    } catch(err) {
        alert("Could not reach backend.");
    }
});

document.getElementById('streak-7-btn').addEventListener('click', () => {
    alert("7-Day Streak Initiated! Stay consistent to earn your reward.");
    document.getElementById('dash-streak').innerText = '0';
});

document.getElementById('streak-30-btn').addEventListener('click', () => {
    alert("30-Day Routine Initiated! Hardcore mode activated.");
    document.getElementById('dash-streak').innerText = '0';
});

// Avatar Upload
document.getElementById('avatar-upload').addEventListener('change', (e) => {
    if(e.target.files.length > 0) {
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

// --- PHOTO UPLOAD & SCANNER ---
const fileInput = document.getElementById('food-image-input');
const fileName = document.getElementById('file-name');
const analyzeBtn = document.getElementById('analyze-vision-btn');
let selectedFileBase64 = null;

fileInput.addEventListener('change', (e) => {
    if(e.target.files.length > 0) {
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
    analyzeBtn.innerHTML = `<i class="ph ph-spinner ph-spin"></i> RUNNING NEURAL SCAN...`;
    
    try {
        const res = await fetch('/api/scan-food', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ image_data: selectedFileBase64 })
        });
        const data = await res.json();
        
        if (data.status === 'success') {
            document.getElementById('scan-food-name').innerText = data.data.food_name || "Food";
            document.getElementById('scan-calories').innerText = data.data.calories || "0";
            document.getElementById('scan-protein').innerText = data.data.protein || "0g";
            document.getElementById('scan-results').style.display = 'block';
        }
    } catch(err) {
        alert("Neural scan failed.");
    } finally {
        analyzeBtn.innerHTML = 'INITIALIZE SCAN';
    }
});

document.getElementById('confirm-log-btn').addEventListener('click', () => {
    const identifiedFood = document.getElementById('scan-food-name').innerText;
    const addCals = parseInt(document.getElementById('scan-calories').innerText);
    
    consumedCals += addCals;
    foodHistory.push({ name: identifiedFood, cals: addCals });
    updateDashboardStats();

    document.getElementById('scan-results').style.display = 'none';
    document.getElementById('food-preview').style.display = 'none';
    fileName.innerText = "No file selected";
    analyzeBtn.disabled = true;
    
    document.getElementById('dash-coins').innerText = parseInt(document.getElementById('dash-coins').innerText) + 50;
    
    document.querySelector('[data-target="home"]').click();
});

// --- AI CHATBOT LOGIC ---
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-chat-btn');
const history = document.getElementById('chat-history');

async function sendChat() {
    const text = chatInput.value.trim();
    if(!text) return;
    
    history.innerHTML += `
        <div class="chat-msg user">
            <div class="msg-bubble">${text}</div>
        </div>
    `;
    chatInput.value = '';
    history.scrollTop = history.scrollHeight;
    
    try {
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ 
                user_message: text,
                user_profile: currentUser
            })
        });
        const data = await res.json();
        
        history.innerHTML += `
            <div class="chat-msg bot">
                <div class="msg-bubble">${data.reply.replace(/\n/g, '<br>')}</div>
            </div>
        `;
        history.scrollTop = history.scrollHeight;
        
    } catch(e) {
        console.error(e);
        history.innerHTML += `
            <div class="chat-msg bot">
                <div class="msg-bubble" style="color:var(--warning)">Connection error. Cannot reach AI Core.</div>
            </div>
        `;
    }
}

sendBtn.addEventListener('click', sendChat);
chatInput.addEventListener('keypress', (e) => {
    if(e.key === 'Enter') sendChat();
});
