export let currentData = {
    who: null,
    whereTo: null,
    how: null
};

export async function saveChanges(section) {
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

export async function fetchSectionData(section) {
    try {
        const response = await fetch(`/api/${section}`);
        const data = await response.json();
        currentData[section] = data;
        return data;
    } catch (error) {
        console.error('Error fetching data:', error);
        throw error;
    }
}