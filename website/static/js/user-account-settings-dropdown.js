document.addEventListener('DOMContentLoaded', () => {
    const dropdownBtn = document.getElementById('accountSettingsDropdownBtn');
    const dropdownMenu = document.getElementById('accountSettingsDropdown');

    // Toggle the dropdown on button click
    dropdownBtn.addEventListener('click', (e) => {
        e.stopPropagation(); // Prevent click from propagating to document
        dropdownMenu.style.display = dropdownMenu.style.display === 'block' ? 'none' : 'block';
    });

    // Hide the dropdown when clicking outside
    document.addEventListener('click', () => {
        dropdownMenu.style.display = 'none';
    });
});
