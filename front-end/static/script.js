var expenses = {}; // Dictionary to store expense data for the chart
var categoryColors = {}; // Dictionary to store category colors


// Expense methods

function updateExpense() {
    var totalAmount = 0;
  /* Fetch for current user's expense data from backend and update it to local storage and pie chart*/
  fetch("/api/get_expenses").then((response) => {
    if (!response.ok) {
      console.error("Error:", response.json().errorData.message);
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    response
      .json()
      .then((data) => {
        // Handle the response from the backend
        console.log("Success:", data);
        purchases = data.purchases;
        for (var i = 0; i < purchases.length; i++) {
          var expenseKey = purchases[i].type;
          expenses[expenseKey] = isNaN(expenses[expenseKey])
            ? purchases[i].amount
            : purchases[i].amount + expenses[expenseKey];
          totalAmount += purchases[i].amount;
        }
      })
      .then(() => {
        updatePieChart();
        document.getElementById("totalAmount").textContent = totalAmount.toFixed(2);
      });
  });
}

function submitExpense() {
  var amount = document.getElementById("amount").value;
  var receipt = document.getElementById("receipt").files[0];

  var type = expenseType.options[expenseType.selectedIndex].text;

  if (type === "More Options") {
    var newOptionValue = document.getElementById("newOptionValue").value;
    type = newOptionValue.toLowerCase().replace(/\b[a-z]/g, function(letter) {
      return letter.toUpperCase();
  });
  }

  var formData = new FormData();

  if (amount.trim() !== ""){
    if(amount < 0){
      alert("Please enter a positive amount.");
      return;
    }
    formData.append("amount", amount);
  }
  else if (receipt){
    formData.append("receipt", receipt);
  }
  else{
    alert("Please enter either the amount or upload a receipt.");
    return;
  }

  formData.append("receipt", receipt);
  formData.append("type", type);

  fetch("/api/submit_expense/", {
    method: "POST",
    body: formData,
  }).then((response) => {
    if (!response.ok) {
      console.error("Error:", response.json().errorData.message);
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    response.json().then((data) => {
      // Handle the response from the backend
      var adjustedAmount = parseFloat(data.adjustedAmount);
      var totalAmount = parseFloat(
        document.getElementById("totalAmount").textContent
      );
      totalAmount += isNaN(adjustedAmount) ? 0 : adjustedAmount;
      document.getElementById("totalAmount").textContent =
        totalAmount.toFixed(2);

      // Add the expense to the dictionary for the chart
      var expenseKey = data.type;
      expenses[expenseKey] = isNaN(expenses[expenseKey])
        ? adjustedAmount
        : adjustedAmount + expenses[expenseKey];

      // Update the pie chart
      updatePieChart();

      // Reset the form
      const receiptInput = document.getElementById('receipt');
      const previewImage = document.getElementById('preview');

      // Reset the input element
      receiptInput.value = '';

      // Reset the img element
      previewImage.src = '';
      previewImage.style.display = 'none';

      // Reset the expense amount input
      document.getElementById("amount").value = "";
    });
  });
}

function updatePieChart() {
  var ctx = document.getElementById("expenseChart").getContext("2d");

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
      categoryColors[categoryKeys[i]] = stringToColor(categoryKeys[i]);
    }
  }

  var data = {
    labels: categoryKeys,
    datasets: [
      {
        data: categoryData,
        backgroundColor: categoryKeys.map((key) => categoryColors[key]),
      },
    ],
  };

  var options = {
    responsive: false,
  };

  new Chart(ctx, {
    type: "pie",
    data: data,
    options: options,
  });
}

function stringToColor(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  let color = "#";
  for (let i = 0; i < 3; i++) {
    let value = (hash >> (i * 8)) & 0xff;
    color += ("00" + value.toString(16)).substr(-2);
  }
  return color;
}



// Login and Registration methods

function login() {
  var username = document.getElementById("username").value;
  var password = document.getElementById("password").value;

  if (username.trim() === "" || password.trim() == "") {
    alert("Please enter username and password");
    return;
  }

  var formData = new FormData();
  formData.append("username", username);
  formData.append("password", password);

  fetch("/api/login/", {
    method: "POST",
    body: formData,
  }).then((response) => {
    if (!response.ok) {
      if (response.status === 401) {
        document.getElementById("loginError").innerHTML =
          "Username or Password is not correct";
      }
      console.error("Login failed:", response.json().errorData.message);
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    response.json().then((data) => {
      document.cookie = `access_token=${data.token}; path=/; secure; samesite=strict; HttpOnly`;
      document.cookie = `refresh_token=${data.refresh_token}; path=/; secure; samesite=strict; HttpOnly`;
      updateExpense();
      window.location.replace("/");
    });
  });
}

function register() {
  var username = document.getElementById("newUsername").value;
  var password = document.getElementById("newPassword").value;

  if (username.trim() === "" || password.trim() == "") {
    alert("Please enter username and password");
    return;
  }

  var formData = new FormData();
  formData.append("username", username);
  formData.append("password", password);

  fetch("/api/register/", {
    method: "POST",
    body: formData,
  }).then((response) => {
    if (!response.ok) {
      if (response.status === 400) {
        document.getElementById("registerError").innerHTML =
          "User already existed";
      }
      console.error("Login failed:", response.json().errorData.message);
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    console.log("Registration successful:", response.json().data);
    window.location.href = "/login";
  });
}

document
  .getElementById("loginForm")
  .addEventListener("submit", function (event) {
    event.preventDefault(); // Prevent the default form submission
    login();
  });

document
  .getElementById("registerForm")
  .addEventListener("submit", function (event) {
    event.preventDefault(); // Prevent the default form submission
    register();
  });

  function logout() {
    fetch("/api/logout/", {
      method: "POST",
    })
    .then((response) => {
      if (!response.ok) {
        console.error("Logout failed:", response.statusText);
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
    })
    .then((data) => {
      console.log("Logout successful:", data);
      document.cookie = `access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC; secure; samesite=strict; HttpOnly`;
      document.cookie = `refresh_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC; secure; samesite=strict; HttpOnly`;
      expenses = {};
      categoryColors = {};
      window.location.href = "/";
    })
    .catch((error) => {
      console.error("Error:", error);
    });
  }


// currency conversion methods

function convertCurrency() {
    var fromCurrencyAmount = document.getElementById("fromCurrencyAmount").value;
    var fromCurrency = document.getElementById("fromCurrency").value;
    var toCurrency = document.getElementById("toCurrency").value;
    
    if (fromCurrencyAmount.trim() === "" || fromCurrency.trim() == "" || toCurrency.trim() == "") {
        alert("Please enter the amount and select the currencies");
        return;
    }

    var url = new URL("/api/exchange/", window.location.origin);
    url.searchParams.append("fromCurrencyAmount", fromCurrencyAmount);
    url.searchParams.append("fromCurrency", fromCurrency);
    url.searchParams.append("toCurrency", toCurrency);

    fetch(url)
    .then((response) => {
        if (!response.ok) {
            console.error("Error:", response.json().errorData.message);
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        response.json().then((data) => {
            document.getElementById("toCurrencyAmount").value = data.toCurrencyAmount;
        });
    });
}