document.getElementById('applyForm').addEventListener('submit', function(event) {
    event.preventDefault();

    let formData = new FormData();
    formData.append('resume', document.getElementById('resume').files[0]);
    formData.append('vacancy_requirements', document.getElementById('vacancy_requirements').value);

    fetch('/apply', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('assessment').textContent = `Оценка кандидата: ${data.assessment}`;
    })
    .catch(error => {
        console.error('Error:', error);
    });
});
