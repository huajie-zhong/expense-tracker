var expenses = []; // Array to store expense data for the chart

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
                expenses.push(isNaN(adjustedAmount) ? 0 : adjustedAmount);

                // Update the pie chart
                updatePieChart();
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }

        function updatePieChart() {
            var ctx = document.getElementById('expenseChart').getContext('2d');
            var data = {
                labels: expenses.map((_, index) => 'Category ' + (index + 1)),
                datasets: [{
                    data: expenses,
                    backgroundColor: getRandomColorArray(expenses.length),
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

        function getRandomColorArray(count) {
            var colors = [];
            for (var i = 0; i < count; i++) {
                var randomColor = '#' + Math.floor(Math.random()*16777215).toString(16);
                colors.push(randomColor);
            }
            return colors;
        }