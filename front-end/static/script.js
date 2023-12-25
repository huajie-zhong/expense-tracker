document.getElementById('expenseForm').addEventListener('submit', function (event) {
    event.preventDefault();
    // Add logic to handle form submission (e.g., send data to the server)
    // You will need AJAX/fetch to send data to the server
    // After successful submission, update the expense list
    updateExpenseList();
});

function updateExpenseList() {
    // Fetch expense data from the server and update the list
    // For simplicity, I'm using dummy data here
    const dummyData = [
        { type: 'Travel', amount: 200.00, description: 'Business trip to XYZ', status: 'Pending' },
        { type: 'Meals', amount: 50.00, description: 'Dinner with clients', status: 'Approved' },
    ];

    const expenseList = document.getElementById('expenseList');
    expenseList.innerHTML = ''; // Clear previous entries

    dummyData.forEach(expense => {
        const li = document.createElement('li');
        li.textContent = `${expense.type} - $${expense.amount.toFixed(2)} - ${expense.description} - Status: ${expense.status}`;
        expenseList.appendChild(li);
    });
}

// Initial update of the expense list
updateExpenseList();