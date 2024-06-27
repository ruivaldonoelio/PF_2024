document.querySelectorAll('.navbar-toggler').forEach(button => {
    button.addEventListener('click', function() {
        const icon = this.querySelector('.toggle-icon');
        const isCollapsed = this.getAttribute('aria-expanded') === 'true';

        if (isCollapsed) {
            icon.innerHTML = `
                <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m19 15-7-7-7 7" />
            `;
        } else {
            icon.innerHTML = `
                <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m19 9-7 7-7-7" />
            `;
        }
    });
});
