let agenda = [];
let selectedEvents = [];

function loadAgenda() {
    fetch('agenda.json')
        .then(response => response.json())
        .then(data => {
            agenda = data;
            loadSelectedEvents();
            createDayTables();
        })
        .catch(error => console.error('Error loading agenda:', error));
}

function loadSelectedEvents() {
    fetch('/get_selected_events')
        .then(response => response.json())
        .then(data => {
            selectedEvents = data;
            updateSelectedEvents();
        })
        .catch(error => console.error('Error loading selected events:', error));
}

function saveSelectedEvents() {
    fetch('/save_selected_events', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(selectedEvents),
    })
        .then(response => response.json())
        .then(data => console.log('Save successful:', data))
        .catch((error) => console.error('Error saving selected events:', error));
}

function createDayTables() {
    const dayTablesDiv = document.getElementById('dayTables');
    agenda.forEach(day => {
        const table = document.createElement('table');
        const caption = table.createCaption();
        caption.textContent = `Schedule for ${day.date}`;

        const headerRow = table.insertRow();
        ['Time', 'Title', 'Room', 'Type', 'Select'].forEach(header => {
            const th = document.createElement('th');
            th.textContent = header;
            headerRow.appendChild(th);
        });

        day.sessions.forEach(session => {
            const row = table.insertRow();
            row.insertCell().textContent = session.time;
            row.insertCell().textContent = session.title;
            row.insertCell().textContent = session.room;
            row.insertCell().textContent = session.session_type || ''; // Add fallback for missing session_type

            const selectCell = row.insertCell();
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.addEventListener('change', () => toggleEventSelection(session, checkbox));
            selectCell.appendChild(checkbox);
        });

        dayTablesDiv.appendChild(table);
    });
}

function toggleEventSelection(session, checkbox) {
    if (checkbox.checked) {
        selectedEvents.push({
            id: session.id,
            title: session.title,
            date: session.date,
            startTime: session.time.split('–')[0].trim(),
            endTime: session.time.split('–')[1].trim(),
            room: session.room,
            description: session.description
        });
    } else {
        selectedEvents = selectedEvents.filter(event => event.id !== session.id);
    }
    updateSelectedEvents();
    saveSelectedEvents();
}

function updateSelectedEvents() {
    const selectedEventsDiv = document.getElementById('selectedEvents');
    selectedEventsDiv.innerHTML = '';

    const table = document.createElement('table');
    const headerRow = table.insertRow();
    ['Date', 'Time', 'Title', 'Room'].forEach(header => {
        const th = document.createElement('th');
        th.textContent = header;
        headerRow.appendChild(th);
    });

    selectedEvents.sort((a, b) => {
        if (a.date !== b.date) return a.date.localeCompare(b.date);
        return a.startTime.localeCompare(b.startTime);
    });

    selectedEvents.forEach(event => {
        const row = table.insertRow();
        row.insertCell().textContent = event.date;
        row.insertCell().textContent = `${event.startTime} – ${event.endTime}`;
        row.insertCell().textContent = event.title;
        row.insertCell().textContent = event.room;

        if (hasConflict(event)) {
            row.classList.add('conflict');
        }
    });

    selectedEventsDiv.appendChild(table);
}

function hasConflict(event) {
    return selectedEvents.some(otherEvent =>
        otherEvent.id !== event.id &&
        otherEvent.date === event.date &&
        doTimesOverlap(event.startTime, event.endTime, otherEvent.startTime, otherEvent.endTime)
    );
}

function doTimesOverlap(start1, end1, start2, end2) {
    const [s1, e1] = [start1, end1].map(t => new Date(`2023-01-01 ${t}`));
    const [s2, e2] = [start2, end2].map(t => new Date(`2023-01-01 ${t}`));
    return s1 < e2 && s2 < e1;
}

window.onload = loadAgenda;
