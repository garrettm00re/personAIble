import { fetchSectionData } from './dataManager.js';
import { formatWho, formatWhereTo, formatHow } from './formatters.js';

const backArrow = document.getElementById('back-arrow');
const pages = document.querySelectorAll('.content');

export async function navigate(targetId) {
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

export function initializeNavigation() {
    backArrow.addEventListener('click', () => navigate('root'));
    navigate('root');
}