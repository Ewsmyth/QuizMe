$(document).ready(function () {
    const COLUMN_SETTINGS_KEY = 'table_column_settings';

    // Function to save column settings to localStorage
    function saveColumnSettings(table) {
        const order = table.colReorder.order(); // Current column order
        const originalOrder = Array.from({ length: order.length }, (_, i) => order.indexOf(i)); // Original-to-current mapping
        const visibility = originalOrder.map(originalIndex => {
            const visible = table.column(originalIndex).visible();
            console.log(`Saving visibility for originalIndex ${originalIndex}: ${visible}`);
            return visible;
        });

        const columnSettings = { order, visibility };

        console.log('Saving Column Settings:', columnSettings);
        localStorage.setItem(COLUMN_SETTINGS_KEY, JSON.stringify(columnSettings));
    }

    // Function to load column settings from localStorage
    function loadColumnSettings(table) {
        const columnSettings = JSON.parse(localStorage.getItem(COLUMN_SETTINGS_KEY));
        if (columnSettings) {
            console.log('Loading Column Settings:', columnSettings);

            // Restore column order
            table.colReorder.order(columnSettings.order);

            // Restore column visibility
            const originalOrder = Array.from({ length: columnSettings.order.length }, (_, i) => columnSettings.order.indexOf(i)); // Current-to-original mapping
            columnSettings.visibility.forEach((visible, originalIndex) => {
                const currentIndex = originalOrder[originalIndex];
                console.log(
                    `Loading visibility for originalIndex ${originalIndex} (currentIndex ${currentIndex}): ${visible}`
                );
                table.column(currentIndex).visible(visible, false); // Apply without redraw
            });

            // Redraw the table after applying all settings
            table.columns.adjust().draw();
        }
    }

    // Initialize the DataTable
    const table = $('#myTable').DataTable({
        colReorder: true,
        responsive: true,
        order: [[0, 'asc']],
        columnDefs: [{ targets: 1, orderable: false }],
        scrollX: true,
    });

    // Load settings on page load
    loadColumnSettings(table);

    // Removes the search label from the table search bar
    $('#myTable_filter label').contents().filter(function () {
        return this.nodeType === 3;
    }).remove();

    $('#myTable_length').insertAfter('.dataTables_scroll');
    // Un-wraps the search input from the label
    $('#myTable_filter input').unwrap();
    // Adds a placeholder to the search input
    $('#myTable_filter input').attr('placeholder', 'Search');
    // Wraps the search element inside a new div
    $('#myTable_filter').wrap('<div class="above-table-header"></div>');
    $('#myTable_filter').prepend($('#searchBarIcon'));
    // When the SVG icon is clicked, focus the input field
    $('#searchBarIcon').on('click', function () {
        $('#myTable_filter input').focus();
    });
    // Adds the toggle buttons button to the .above-table-header div
    $('.above-table-header').append($('#open-popup'));
    // Wrap lower elements inside the new div
    $('#myTable_length, #myTable_paginate, #myTable_info').wrapAll('<div class="below-table-footer"></div>');
    // Create the .footer-left-side div
    $('<div class="footer-left-side"></div>')
        .append($('#myTable_info')) // Move #myTable_info inside .footer-left-side
        .append($('#myTable_length')) // Move #myTable_length inside .footer-left-side
        .prependTo('.below-table-footer'); // Add .footer-left-side to the top of .below-table-footer

    const searchInput = $('#myTable_filter input');

    searchInput.attr('type', 'text');
    
    // Appends the custom reset button next to the DataTable search input
    $('#myTable_filter').append('<button id="resetSearch" class="reset-button" style="display: none;">Reset</button>');

    const resetButton = $('#resetSearch');

    searchInput.on('input', function () {
        if ($(this).val().length > 0) {
            resetButton.show();
        } else {
            resetButton.hide();
        }
    });

    resetButton.on('click', function () {
        searchInput.val('');
        resetButton.hide();
        table.search('').draw(); // Use the `table` variable here
    });

    resetButton.on('click', function () {
        searchInput.focus();
    });

    // Populate the column menu dynamically
    function populateColumnMenu() {
        toggleColumnMenuList.empty(); // Clear existing menu items

        table.columns().every(function (index) {
            const column = this;
            const headerText = $(column.header()).text();

            const listItem = $('<li></li>');
            const checkbox = $('<input type="checkbox">').prop('checked', column.visible());
            const label = $('<label></label>').text(headerText);

            checkbox.on('change', function () {
                const isChecked = $(this).is(':checked');
                console.log(`Toggling visibility for column ${index} to ${isChecked}`);
                column.visible(isChecked); // Toggle column visibility
                saveColumnSettings(table); // Save settings after visibility change
            });

            listItem.append(checkbox).append(label);
            toggleColumnMenuList.append(listItem);
        });
    }

    // Variables for the toggle column popup menu
    const toggleColumnMenuBtn = document.getElementById('toggleColumnMenuBtn');
    const toggleColumnMenuCloseBtn = document.getElementById('toggleColumnMenuCloseBtn');
    const toggleColumnMenu = document.getElementById('toggleColumnMenu');
    const toggleColumnMenuList = $('#toggleColumnMenuList');

    // Opens the toggle column popup menu
    toggleColumnMenuBtn.addEventListener('click', () => {
        populateColumnMenu(); // Populate menu before opening
        toggleColumnMenu.classList.add('open');
    });

    // Closes the toggle column popup menu
    toggleColumnMenuCloseBtn.addEventListener('click', () => {
        toggleColumnMenu.classList.remove('open');
    });

    // Listen for column reorder events and update the saved settings
    table.on('column-reorder', function () {
        console.log('Column order changed');
        saveColumnSettings(table);
        populateColumnMenu(); // Update the menu
    });

    // Initial menu population
    populateColumnMenu();
});