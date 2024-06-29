const queryInput = document.getElementById('query');
const algorithmSelect = document.getElementById('algorithm');

// Submit form on Enter key press
queryInput.addEventListener('keyup', function(event) {
  if (event.key === 'Enter') {
    event.preventDefault(); // Prevent default form submission behavior
    document.querySelector('form').submit(); // Manually trigger form submission
  }
});

// Log selected algorithm on change
algorithmSelect.addEventListener('change', function() {
  const selectedAlgorithm = algorithmSelect.options[algorithmSelect.selectedIndex].value;
  console.log('Selected algorithm:', selectedAlgorithm);
});

// Add any additional JavaScript functionalities specific to the index page

// Example: Focus on the search query input field on page load
window.onload = function() {
  document.getElementById('query').focus();
};