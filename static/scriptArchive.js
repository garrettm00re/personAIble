    document.getElementById('user-input').addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            submitQuestion();
        }
    });
    const backArrow = document.getElementById('back-arrow');
    const pages = document.querySelectorAll('.content');

async function submitQuestion() {
    const input = document.getElementById('user-input');
    const question = input.value.trim();

    if (question) {
        addMessage(question, 'user');
        input.value = '';
        
        try {
            const response = await fetch('/api/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question: question })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                addMessage(data.answer, 'system');
            } else {
                addMessage('Error: ' + data.error, 'system');
            }
        } catch (error) {
            addMessage('Error connecting to the server', 'system');
            console.error('Error:', error);
        }
    }
}

function addMessage(text, type) {
    const qaContainer = document.getElementById('qa-container');
    const message = document.createElement('div');
    message.className = `message ${type}-message`;
    message.textContent = text;
    qaContainer.appendChild(message);
    qaContainer.scrollTop = qaContainer.scrollHeight;
}

    backArrow.addEventListener('click', () => navigate('root'));
    navigate('root'); 
function formatSubPlan(subPlan) {
let html = '';
subPlan.forEach(plan => {
    html += `
        <div class="plan-section">
            <h3>${plan.goal.description}</h3>
            <p><strong>Deadline:</strong> ${plan.goal.deadline}</p>
            <p><strong>Justification:</strong> ${plan.justification}</p>
            
            <table class="action-table">
                <thead>
                    <tr>
                        <th>Action Item</th>
                        <th>When</th>
                        <th>Duration</th>
                    </tr>
                </thead>
                <tbody>
                    ${(plan.actionItems || plan.actionItem || []).map(item => `
                        <tr>
                            <td>${item.what}</td>
                            <td>${item.when}</td>
                            <td>${item.duration}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>`;
});

return html;
}

function formatWho(data) {
    let html = '<div class="data-section">';
    for (const [key, value] of Object.entries(data)) {
        html += `
            <table class="info-table">
                <thead>
                    <tr>
                        <th colspan="${Array.isArray(value) ? 1 : 2}">${key}</th>
                    </tr>
                </thead>
                <tbody>`;
        
        if (Array.isArray(value)) {
            value.forEach((item, index) => {
                html += `<tr><td contenteditable="true" data-key="${key}" data-index="${index}">${item}</td></tr>`;
            });
        } else {
            html += `<tr><td contenteditable="true" data-key="${key}">${value}</td></tr>`;
        }
        
        html += `</tbody></table>`;
    }
    return html + '</div>' + saveChangesButton('who');
}

function formatWhereTo(data) {
    let html = `
        <table class="info-table">
            <thead>
                <tr>
                    <th>Desire</th>
                    <th>Strength</th>
                    <th>Timeliness</th>
                </tr>
            </thead>
            <tbody>`;
    
    data.desires.forEach((desire, index) => {
        html += `
            <tr>
                <td contenteditable="true" data-field="description" data-index="${index}">${desire.description}</td>
                <td contenteditable="true" data-field="strength" data-index="${index}">${desire.strength}</td>
                <td contenteditable="true" data-field="timeliness" data-index="${index}">${desire.timeliness}</td>
            </tr>`;
    });
    
    return html + '</tbody></table>' + saveChangesButton('whereTo');
}

function formatHow(data) {
    let html = '';
    data.subPlans.forEach((plan, planIndex) => {
        html += `
            <div class="plan-section">
                <table class="info-table">
                    <thead>
                        <tr>
                            <th colspan="2">Goal: <span contenteditable="true" data-plan="${planIndex}" data-field="goal.description">${plan.goal.description}</span></th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>Deadline:</strong></td>
                            <td contenteditable="true" data-plan="${planIndex}" data-field="goal.deadline">${plan.goal.deadline}</td>
                        </tr>
                        <tr>
                            <td><strong>Justification:</strong></td>
                            <td contenteditable="true" data-plan="${planIndex}" data-field="justification">${plan.justification}</td>
                        </tr>
                    </tbody>
                </table>

                <table class="info-table action-table">
                    <thead>
                        <tr>
                            <th>Action Item</th>
                            <th>When</th>
                            <th>Duration</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${(plan.actionItems || plan.actionItem || []).map((item, itemIndex) => `
                            <tr>
                                <td contenteditable="true" data-plan="${planIndex}" data-action="${itemIndex}" data-field="what">${item.what}</td>
                                <td contenteditable="true" data-plan="${planIndex}" data-action="${itemIndex}" data-field="when">${item.when}</td>
                                <td contenteditable="true" data-plan="${planIndex}" data-action="${itemIndex}" data-field="duration">${item.duration}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>`;
    });
    return html + saveChangesButton('how');
}

function saveChangesButton(route) {
    return `<div class="sticky-save-container">
        <button class="save-button" onclick="saveChanges('${route}')">Save Changes</button>
    </div>`;
}

let currentData = {
    who: null,
    whereTo: null,
    how: null
};

async function saveChanges(section) {
    try {
        let newData;
        
        switch(section) {
            case 'who':
                newData = {...currentData.who};
                document.querySelectorAll('#who td[contenteditable]').forEach(td => {
                    const key = td.dataset.key;
                    const index = td.dataset.index;
                    if (index !== undefined) {
                        if (!Array.isArray(newData[key])) newData[key] = [];
                        newData[key][index] = td.textContent;
                    } else {
                        newData[key] = td.textContent;
                    }
                });
                break;

            case 'whereTo':
                newData = {desires: []};
                const rows = document.querySelectorAll('#whereTo tbody tr');
                rows.forEach(row => {
                    const cells = row.querySelectorAll('td');
                    newData.desires.push({
                        description: cells[0].textContent,
                        strength: cells[1].textContent,
                        timeliness: cells[2].textContent
                    });
                });
                break;

            case 'how':
                newData = {subPlan: []};
                document.querySelectorAll('#how .plan-section').forEach((section, planIndex) => {
                    const plan = {
                        goal: {
                            description: section.querySelector(`[data-plan="${planIndex}"][data-field="goal.description"]`).textContent,
                            deadline: section.querySelector(`[data-plan="${planIndex}"][data-field="goal.deadline"]`).textContent
                        },
                        justification: section.querySelector(`[data-plan="${planIndex}"][data-field="justification"]`).textContent,
                        actionItems: []
                    };

                    section.querySelectorAll('tr').forEach(row => {
                        const what = row.querySelector(`[data-field="what"]`);
                        if (what) {
                            plan.actionItems.push({
                                what: what.textContent,
                                when: row.querySelector(`[data-field="when"]`).textContent,
                                duration: row.querySelector(`[data-field="duration"]`).textContent
                            });
                        }
                    });

                    newData.subPlan.push(plan);
                });
                break;
        }
        console.log("NEW DATA: ", newData)
        const response = await fetch(`/api/${section}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(newData)
        });

        if (!response.ok) throw new Error('Failed to save changes');
        
        alert('Changes saved successfully!');
        await navigate(section); // Refresh the view
        
    } catch (error) {
        console.error('Error saving changes:', error);
        alert('Failed to save changes. Please try again.');
    }
}

async function navigate(targetId) {
    pages.forEach(page => page.classList.add('hidden'));
    const targetPage = document.getElementById(targetId);
    targetPage.classList.remove('hidden');
    backArrow.classList.toggle('hidden', targetId === 'root');
    if (targetId !== 'root' && targetId !== 'settings') {
        try {
            const response = await fetch(`/api/${targetId}`);
            const data = await response.json();
            currentData[targetId] = data; // Store the current data
            
            switch(targetId) {
                case 'who':
                    targetPage.innerHTML = formatWho(data);
                    break;
                case 'whereTo':
                    targetPage.innerHTML = formatWhereTo(data);
                    break;
                case 'how':
                    targetPage.innerHTML = formatHow(data);
                    break;
            }
        } catch (error) {
            console.error('Error fetching data:', error);
            targetPage.innerHTML = '<p>Error loading content</p>';
        }
    }
}