document.addEventListener('DOMContentLoaded', () => {
    const grid = document.querySelector('.apps-grid') || document.body;
    const editBtn = document.getElementById('edit-apps-btn');
    const appsKey = 'hamse_home_apps';
    
    const defaultApps = [
        { id: 'license', name: 'License Key Management', icon: '🔑', url: 'licenses.html', color: 'linear-gradient(135deg, #6a5af9, #2575fc)' }
    ];

    let apps = JSON.parse(localStorage.getItem(appsKey)) || defaultApps;
    let isEditing = false;

    function renderApps() {
        if (!grid) return;
        grid.innerHTML = '';
        apps.forEach((app, index) => {
            const div = document.createElement('div');
            div.className = 'app-icon-container' + (isEditing ? ' jiggle' : '');
            div.innerHTML = `
                ${isEditing ? `<button class="del-btn" data-idx="${index}">✕</button>` : ''}
                <div class="app-icon" style="background: ${app.color || '#333'}">${app.icon}</div>
                <div class="app-name">${app.name}</div>
            `;
            if (!isEditing) {
                div.onclick = () => window.location.href = app.url;
            }
            grid.appendChild(div);
        });
    }

    // Haddii aysan jirin badhanka Edit, aan abuurno
    if (!editBtn) {
        const nav = document.createElement('div');
        nav.style.cssText = 'position:fixed; top:20px; right:20px; z-index:100;';
        nav.innerHTML = `<button id="edit-apps-btn" style="padding:8px 16px; border-radius:20px; background:rgba(255,255,255,0.2); color:white; border:none; font-weight:bold; backdrop-filter:blur(10px);">Edit</button>`;
        document.body.appendChild(nav);
        document.getElementById('edit-apps-btn').onclick = toggleEdit;
    } else {
        editBtn.onclick = toggleEdit;
    }

    function toggleEdit() {
        isEditing = !isEditing;
        const btn = document.getElementById('edit-apps-btn');
        btn.textContent = isEditing ? 'Done' : 'Edit';
        
        if (isEditing) {
            // Ku dar badhanka Add App
            if (!document.getElementById('add-app-btn')) {
                const addBtn = document.createElement('div');
                addBtn.id = 'add-app-btn';
                addBtn.className = 'app-icon-container jiggle';
                addBtn.innerHTML = `<div class="app-icon" style="background: rgba(255,255,255,0.1); border: 2px dashed rgba(255,255,255,0.5); display:flex; align-items:center; justify-content:center; font-size:30px;">+</div><div class="app-name">Add App</div>`;
                addBtn.onclick = promptNewApp;
                grid.appendChild(addBtn);
            }
        } else {
            const addBtn = document.getElementById('add-app-btn');
            if (addBtn) addBtn.remove();
        }
        renderApps();
    }

    function promptNewApp() {
        const name = prompt("Magaca App-ka (Tusaale: MT Manager VIP):");
        if (!name) return;
        const icon = prompt("Icon (Emoji ama URL sawir, tusaale: 🚀 ama https://...):", "🚀");
        if (!icon) return;
        const url = prompt("Link-ga (URL ama APK download):");
        if (!url) return;
        
        let color = 'linear-gradient(135deg, #ff9a9e, #fecfef)';
        if (icon.startsWith('http')) {
            apps.push({ name, icon: `<img src="${icon}" style="width:100%; height:100%; border-radius:22%; object-fit:cover;">`, url, color: 'transparent' });
        } else {
            apps.push({ name, icon, url, color });
        }
        
        localStorage.setItem(appsKey, JSON.stringify(apps));
        toggleEdit(); // Dib u celi edit mode
        toggleEdit(); // Fur edit mode si '+' u soo baxo
    }

    // Dhageyso delete
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('del-btn')) {
            const idx = e.target.getAttribute('data-idx');
            apps.splice(idx, 1);
            localStorage.setItem(appsKey, JSON.stringify(apps));
            toggleEdit(); toggleEdit();
        }
    });

    // CSS loogu talagalay jiggle iyo qurxinta
    const style = document.createElement('style');
    style.textContent = `
        .apps-grid { display: flex; flex-wrap: wrap; gap: 20px; padding: 20px; justify-content: flex-start; }
        .app-icon-container { display: flex; flex-direction: column; align-items: center; width: 75px; position: relative; cursor: pointer; }
        .app-icon { width: 65px; height: 65px; border-radius: 16px; display: flex; align-items: center; justify-content: center; font-size: 32px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
        .app-name { color: white; font-size: 11px; margin-top: 6px; text-align: center; text-shadow: 0 1px 3px rgba(0,0,0,0.8); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; width: 100%; }
        .jiggle { animation: jiggle 0.3s infinite alternate; }
        @keyframes jiggle { 0% { transform: rotate(-2deg); } 100% { transform: rotate(2deg); } }
        .del-btn { position: absolute; top: -5px; left: -5px; background: #ff3b30; color: white; border: none; border-radius: 50%; width: 22px; height: 22px; font-size: 12px; font-weight: bold; z-index: 10; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 2px 5px rgba(0,0,0,0.5); }
    `;
    document.head.appendChild(style);
    renderApps();
});
