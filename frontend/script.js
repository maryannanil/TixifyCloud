document.getElementById('verification-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const ticketId = document.getElementById('ticket-id').value;
    const fileInput = document.getElementById('ticket-file');
    const file = fileInput.files[0];

    const formData = new FormData();
    formData.append('ticket_id', ticketId);
    if (file) {
        formData.append('file', file);
    }

    // ✅ FETCH call to Flask backend
    const BACKEND_URL = process.env.BACKEND_URL || 'http://52.72.174.66:8000';
    const response = await fetch(`${BACKEND_URL}/validate_ticket`, {  
    method: 'POST',
    body: formData
    });

    

    const data = await response.json();
    document.getElementById('result').innerHTML = data.message;
});
