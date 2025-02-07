export function formatSubPlan(subPlan) {
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

export function formatWho(data) {
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

export function formatWhereTo(data) {
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

export function formatHow(data) {
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

export function saveChangesButton(route) {
    return `<div class="sticky-save-container">
        <button class="save-button" onclick="saveChanges('${route}')">Save Changes</button>
    </div>`;
}
