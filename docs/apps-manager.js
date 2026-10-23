document.addEventListener('DOMContentLoaded', () => {
    const appsKey = 'hamse_home_apps';
    const defaultApps = [
        { id: 'license', name: 'License Key Management', icon: '🔑', url: 'licenses.html', color: 'linear-gradient(135deg, #6a5af9, #2575fc)' }
    ];
    let apps = JSON.parse(localStorage.getItem(appsKey)) || defaultApps;
    let isEditing = false;

    // Samee qaabka bogga (Gradient Purple + Grid)
    document.body.style.cssText = 'margin:0; padding:0; background: linear-gradient(135deg, #8A2387, #E94057, #F27121); min-height: 100vh; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; overflow-x: hidden;';
    
    let grid = document.createElement('div');
    grid.style.cssText = 'display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px 15px; padding: 40px 20px; margin-top: 40px;';
    document.body.appendChild(grid);

    let editBtn = document.createElement('button');
    editBtn.textContent = 'Edit';
    editBtn.style.cssText = 'position: fixed; top: 20px; right: 20px; padding: 8px 18px; border-radius: 20px; background: rgba(255,255,255,0.2); color: white; border: 1px solid rgba(255,255,255,0.3); font-weight: 600; backdrop-filter: blur(10px); z-index: 100; cursor: pointer; font-size: 14px;';
    document.body.appendChild(editBtn);

    function renderApps() {
        grid.innerHTML = '';
        apps.forEach((app, index) => {
            const div = document.createElement('div');
            div.style.cssText = 'display: flex; flex-direction: column; align-items: center; position: relative; cursor: pointer;' + (isEditing ? ' animation: jiggle 0.3s infinite alternate;' : '');
            
            let iconHtml = app.icon.startsWith('http') 
                ? `<img src="${app.icon}" style="width:100%; height:100%; border-radius:22%; object-fit:cover;">` 
                : app.icon;

            div.innerHTML = `
                ${isEditing ? `<button class="del-btn" data-idx="${index}" style="position: absolute; top: -5px; left: -5px; background: #ff3b30; color: white; border: none; border-radius: 50%; width: 22px; height: 22px; font-size: 12px; font-weight: bold; z-index: 10; cursor: pointer;">✕</button>` : ''}
                <div style="width: 65px; height: 65px; border-radius: 16px; display: flex; align-items: center; justify-content: center; font-size: 32px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); background: ${app.color || '#333'}; overflow: hidden;">
                    ${iconHtml}
                </div>
                <div style="color: white; font-size: 11px; margin-top: 6px; text-align: center; text-shadow: 0 1px 3px rgba(0,0,0,0.8); width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${app.name}</div>
            `;
            
            if (!isEditing) div.onclick = () => window.location.href = app.url;
            grid.appendChild(div);
        });

        if (isEditing) {
            let addBtn = document.createElement('div');
            addBtn.style.cssText = 'display: flex; flex-direction: column; align-items: center; position: relative; cursor: pointer; animation: jiggle 0.3s infinite alternate;';
            addBtn.innerHTML = `<div style="width: 65px; height: 65px; border-radius: 16px; display: flex; align-items: center; justify-content: center; font-size: 32px; background: rgba(255,255,255,0.1); border: 2px dashed rgba(255,255,255,0.5);">+</div><div style="color: white; font-size: 11px; margin-top: 6px;">Add App</div>`;
            addBtn.onclick = addApp;
            grid.appendChild(addBtn);
        }
    }

    function addApp() {
        const name = prompt("Magaca App-ka (Tusaale: MT Manager VIP):");
        if (!name) return;
        let icon = prompt("Icon (Emoji ama Link sawir, tusaale: 🚀 ama https://...):", "🚀");
        if (!icon) return;
        const url = prompt("Link-ga (URL ama APK download):");
        if (!url) return;
        
        let color = 'linear-gradient(135deg, #00b09b, #96c93d)';
        apps.push({ name, icon, url, color });
        localStorage.setItem(appsKey, JSON.stringify(apps));
        renderApps();
    }

    editBtn.onclick = () => {
        isEditing = !isEditing;
        editBtn.textContent = isEditing ? 'Done' : 'Edit';
        renderApps();
    };

    grid.addEventListener('click', (e) => {
        if (e.target.classList.contains('del-btn')) {
            const idx = e.target.getAttribute('data-idx');
            apps.splice(idx, 1);
            localStorage.setItem(appsKey, JSON.stringify(apps));
            renderApps();
        }
    });

    const style = document.createElement('style');
    style.textContent = `@keyframes jiggle { 0% { transform: rotate(-2deg); } 100% { transform: rotate(2deg); } }`;
    document.head.appendChild(style);

    renderApps();
});
