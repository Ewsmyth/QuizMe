document.getElementById('createUserForm').addEventListener('submit', async (event) => {
    event.preventDefault(); // Prevent the default form submission
  
    const form = event.target;
    const formData = new FormData(form);
  
    try {
      const response = await fetch(form.action, {
        method: 'POST',
        body: formData
      });
  
      const result = await response.json();
      const messageContainer = document.getElementById('message');
  
      if (response.ok) {
        // Success message
        messageContainer.innerHTML = `<p class="success">${result.success}</p>`;
      } else {
        // Error message
        messageContainer.innerHTML = `<p class="error">${result.error}</p>`;
      }
    } catch (error) {
      console.error('Error:', error);
      document.getElementById('message').innerHTML = `<p class="error">Something went wrong. Please try again later.</p>`;
    }
});
  