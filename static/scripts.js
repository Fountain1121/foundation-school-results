document.addEventListener('DOMContentLoaded', () => {
    // Dark mode toggle
    const html = document.documentElement;
    const themeToggle = document.getElementById('theme-toggle');
    const sunIcon = document.getElementById('sun');
    const moonIcon = document.getElementById('moon');

    // Check for saved theme
    if (localStorage.getItem('theme') === 'dark') {
        html.classList.add('dark');
        sunIcon.classList.remove('hidden');
        moonIcon.classList.add('hidden');
    }

    themeToggle.addEventListener('click', () => {
        html.classList.toggle('dark');
        if (html.classList.contains('dark')) {
            localStorage.setItem('theme', 'dark');
            sunIcon.classList.remove('hidden');
            moonIcon.classList.add('hidden');
        } else {
            localStorage.setItem('theme', 'light');
            sunIcon.classList.add('hidden');
            moonIcon.classList.remove('hidden');
        }
    });

    // Table sorting
    document.querySelectorAll('table').forEach(table => {
        const headers = table.querySelectorAll('th[data-sort]');
        headers.forEach(header => {
            header.addEventListener('click', () => {
                const key = header.dataset.sort;
                const tbody = table.querySelector('tbody');
                const rows = Array.from(tbody.querySelectorAll('tr'));
                const isAsc = !header.classList.contains('sort-asc');
                
                headers.forEach(h => {
                    h.classList.remove('sort-asc', 'sort-desc');
                });
                header.classList.add(isAsc ? 'sort-asc' : 'sort-desc');

                rows.sort((a, b) => {
                    let aValue = a.children[Array.from(header.parentNode.children).indexOf(header)].textContent;
                    let bValue = b.children[Array.from(header.parentNode.children).indexOf(header)].textContent;
                    
                    if (key === 'student_id' || key === 'section_a' || key === 'section_b' || key === 'total') {
                        aValue = parseFloat(aValue) || 0;
                        bValue = parseFloat(bValue) || 0;
                    } else if (key === 'percentage') {
                        aValue = parseFloat(aValue.replace('%', '')) || 0;
                        bValue = parseFloat(bValue.replace('%', '')) || 0;
                    }
                    
                    return isAsc ? aValue > bValue ? 1 : -1 : aValue < bValue ? 1 : -1;
                });

                tbody.innerHTML = '';
                rows.forEach(row => tbody.appendChild(row));
            });
        });
    });
});