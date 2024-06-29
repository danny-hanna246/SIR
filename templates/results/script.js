// Define error_message variable globally
let error_message = "";

// Define results variable before fetching data
let results = [];

const resultsElement = document.getElementById('results');

function renderResults(searchResults) {
  // Clear previous results
  resultsElement.innerHTML = "";

  for (const result of searchResults) {
    // Declare error_message variable within the for loop

    // Check for error message in each result
    if (result.error_message) {
      // Use this.error_message to access the local variable
      this.error_message = result.error_message;
      break; // Stop rendering if error encountered
    }

    // Create result item elements
    const resultItem = document.createElement("li");
    resultItem.classList.add("result");

    // ...

    // Add result item to the list
    resultsElement.appendChild(resultItem);
  }

  // Handle errors after rendering
  if (this.error_message) { // Use this.error_message to access the local variable
    alert("Error retrieving search results: " + this.error_message);
  } else if (searchResults.length === 0) {
    alert("No results found for your query.");
  }
}



// Fetch results when the page loads
document.addEventListener("DOMContentLoaded", () => {
  const query = document.getElementById("query").value;
  const algorithm = document.getElementById("algorithm").value;

  fetch("/results", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      query,
      algorithm,
    }),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .then((data) => {
      // Check for server-side error message
      data.results = undefined;
      if (data.error_message) {
        error_message = data.error_message;
        alert("Error from server: " + data.error_message);
        return;
      }

      // Update received data and render results
      results = data.results;
      renderResults(results);
    })
    .catch((error) => {
      console.error("Error fetching search results:", error);
    });
});