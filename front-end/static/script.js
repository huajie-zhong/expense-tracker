var expenses = {}; // Dictionary to store expense data for the chart
var categoryColors = {}; // Dictionary to store category colors

        function submitExpense() {
            var amount = document.getElementById('amount').value;
            var receipt = document.getElementById('receipt').files[0];

            if (amount.trim() === '' && !receipt) {
                alert('Please enter either the amount or upload a receipt.');
                return;
            }

            var formData = new FormData();
            formData.append('amount', amount);
            formData.append('receipt', receipt);
            formData.append('type', expenseType.options[expenseType.selectedIndex].text);

            fetch('/api/submit_expense', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                // Handle the response from the backend
                var adjustedAmount = parseFloat(data.adjustedAmount);
                var totalAmount = parseFloat(document.getElementById('totalAmount').textContent);
                totalAmount += isNaN(adjustedAmount) ? 0 : adjustedAmount;
                document.getElementById('totalAmount').textContent = totalAmount.toFixed(2);

                // Add the expense to the array for the chart
                var expenseKey = data.type;
                expenses[expenseKey] = isNaN(expenses[expenseKey]) ? adjustedAmount : adjustedAmount + expenses[expenseKey];

                // Update the pie chart
                updatePieChart();
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }

        function updatePieChart() {
            var ctx = document.getElementById('expenseChart').getContext('2d');

            // Check if there's an existing chart instance with ID '0'
            var existingChart = Chart.getChart(ctx);
            if (existingChart) {
            // If an existing chart is found, destroy it
            existingChart.destroy();
            }
            
            var categoryKeys = Object.keys(expenses);
            var categoryData = Object.values(expenses);

            // Ensure that category colors are initialized and consistent
            for (var i = 0; i < categoryKeys.length; i++) {
                if (!categoryColors[categoryKeys[i]]) {
                    categoryColors[categoryKeys[i]] = getRandomColor();
                }
            }

            var data = {
                labels: categoryKeys,
                datasets: [{
                    data: categoryData,
                    backgroundColor: categoryKeys.map(key => categoryColors[key]),
                }]
            };

            var options = {
                responsive: true,
            };

            new Chart(ctx, {
                type: 'pie',
                data: data,
                options: options
            });
        }

        function getRandomColor() {
            return '#' + Math.floor(Math.random() * 16777215).toString(16);
        }