// イベントを表示（XSS対策済み）
function displayEvents(events) {
    const eventsGrid = document.getElementById('eventsGrid');

    if (!eventsGrid) {
        console.error('イベントグリッド（eventsGrid）が見つかりません');
        return;
    }

    // 既存の内容をクリア
    eventsGrid.innerHTML = '';

    if (events.length === 0) {
        const p = document.createElement('p');
        p.style.textAlign = 'center';
        p.style.color = '#999';
        p.style.padding = '40px';
        p.textContent = '該当するイベントが見つかりませんでした';
        eventsGrid.appendChild(p);
        return;
    }

    events.forEach(event => {
        const eventElement = document.createElement('div');
        eventElement.className = 'event-item';
        eventElement.dataset.area = event.area;

        // 日付（簡易）
        const month = event.event_date;
        const day = '';

        // エリア名変換
        const areaNames = {
            maebashi: '前橋・赤城',
            takasaki: '高崎・富岡',
            kusatsu: '草津・四万',
            minakami: '水上・尾瀬',
            ikaho: '伊香保・榛名',
            kiryu: '桐生',
            tomioka: '富岡',
            tatebayashi: '館林'
        };
        const areaDisplay = areaNames[event.area] || event.area;

        /* --- 固定HTMLのみ innerHTML --- */
        eventElement.innerHTML = `
            <div class="event-date-box">
                <div class="event-month"></div>
                <div class="event-day"></div>
            </div>
            <div class="event-info">
                <h3></h3>
                <div class="event-meta">
                    <span class="event-location"></span>
                    <span class="event-area"></span>
                    <span class="event-category"></span>
                </div>
                <p class="event-description"></p>
            </div>
        `;

        /* --- ユーザー入力は textContent --- */
        eventElement.querySelector('.event-month').textContent = `${month}月`;
        eventElement.querySelector('.event-day').textContent = day;
        eventElement.querySelector('h3').textContent = event.event_name;
        eventElement.querySelector('.event-location').textContent = `📍 ${event.location}`;
        eventElement.querySelector('.event-area').textContent = areaDisplay;
        eventElement.querySelector('.event-category').textContent = event.category;
        eventElement.querySelector('.event-description').textContent = event.description;

        eventsGrid.appendChild(eventElement);
    });
}
