
function showSection(section) {
    document.querySelectorAll('.game-log-section').forEach(el => {
        el.classList.remove('active');
    });
    
    const sections = {
        'averages': 'averages-section',
        'totals': 'totals-section',
        'per36': 'per36-section'
    };
    
    Object.values(sections).forEach(id => {
        const element = document.getElementById(id);
        if (element) element.style.display = 'none';
    });
    
    const targetSection = sections[section];
    if (targetSection) {
        const element = document.getElementById(targetSection);
        if (element) element.style.display = 'block';
    }
}


function showGameLog(season) {
    const statSections = ['averages-section', 'totals-section', 'per36-section'];
    statSections.forEach(id => {
        const element = document.getElementById(id);
        if (element) element.style.display = 'none';
    });
    
    document.querySelectorAll('.game-log-section').forEach(el => {
        el.classList.remove('active');
    });
    
    const gameLogElement = document.getElementById('gamelog-' + season);
    if (gameLogElement) {
        gameLogElement.classList.add('active');
    }
}

function sortTable(header) {
    const table = header.closest('table');
    const tbody = table.querySelector('tbody');
    const columnIndex = Array.from(header.parentElement.children).indexOf(header);
    
    const rows = Array.from(tbody.querySelectorAll('tr:not(.career-row)'));
    const careerRow = tbody.querySelector('.career-row');
    
    rows.sort((a, b) => {
        const aValue = a.cells[columnIndex].textContent.trim();
        const bValue = b.cells[columnIndex].textContent.trim();
        
        const aNum = parseFloat(aValue);
        const bNum = parseFloat(bValue);
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return bNum - aNum; 
        }
        
        return aValue.localeCompare(bValue); 
    });
    
    tbody.innerHTML = '';
    
    rows.forEach(row => tbody.appendChild(row));
    
    if (careerRow) {
        tbody.appendChild(careerRow);
    }
}


document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('th').forEach(header => {
        header.addEventListener('click', function() {
            sortTable(this);
        });
    });
});

function sortTable(header) {
    const table = header.closest('table');
    const tbody = table.querySelector('tbody');
    const columnIndex = Array.from(header.parentElement.children).indexOf(header);

    const currentDir = header.dataset.sortDir || 'desc';
    const newDir = currentDir === 'asc' ? 'desc' : 'asc';
    header.dataset.sortDir = newDir;

    header.parentElement.querySelectorAll('th').forEach(th => {
        if (th !== header) delete th.dataset.sortDir;
    });

    const rows = Array.from(tbody.querySelectorAll('tr:not(.career-row)'));
    const careerRow = tbody.querySelector('.career-row');

    rows.sort((a, b) => {
        const aValue = a.cells[columnIndex].textContent.trim();
        const bValue = b.cells[columnIndex].textContent.trim();

        const aNum = parseFloat(aValue);
        const bNum = parseFloat(bValue);

        let result;

        if (!isNaN(aNum) && !isNaN(bNum)) {
            result = aNum - bNum;
        } else {
            result = aValue.localeCompare(bValue);
        }

        return newDir === 'asc' ? result : -result;
    });

    tbody.innerHTML = '';
    rows.forEach(row => tbody.appendChild(row));

    if (careerRow) {
        tbody.appendChild(careerRow);
    }
}
