const resultsElement = document.getElementById('results');

function renderResults(searchResults) {
  // Clear previous results
  resultsElement.innerHTML = "";

  for (const result of searchResults) {
    // Create result item elements
    const resultItem = document.createElement('li');
    resultItem.classList.add('result');

    const titleLink = document.createElement('a');
    titleLink.href = result.url;
    titleLink.textContent = result.title;

    const snippetText = document.createTextNode(result.snippet);

    // Append elements to result item
    resultItem.appendChild(titleLink);
    resultItem.appendChild(document.createElement('br'));
    resultItem.appendChild(snippetText);

    // Add result item to the list
    resultsElement.appendChild(resultItem);
  }
}

// Fetch results when the form is submitted
document.addEventListener('submit', (event) => {
  event.preventDefault();

  const query = document.getElementById('query').value;
  const algorithm = document.getElementById('algorithm').value;

  fetch('/documents', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query,
      algorithm,
    }),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then((data) => {
      // Check for server-side error message
      if (data.error_message) {
        alert('Error from server: ' + data.error_message);
        return;
      }

      // Update received data and render results
      renderResults(data.results);
    })
    .catch((error) => {
      console.error('Error fetching search results:', error);
    });
});

// Check for night theme preference from localStorage
const nightThemeEnabled = localStorage.getItem('nightTheme') === 'true';

// Apply night theme styles if enabled
if (nightThemeEnabled) {
  document.documentElement.classList.add('night-theme');
}