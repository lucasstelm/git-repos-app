document.getElementById('githubForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const username = formData.get('username');
    
    try {
        const response = await fetch('/get_repos', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `username=${encodeURIComponent(username)}`
        });
        
        if (!response.ok) {
            console.error("Response from server was not OK. Status code:", response.status);
            try {
                const errorData = await response.json();
                console.error("Error data from backend:", errorData);
                const errorMessage = errorData.detail && errorData.detail.message ? errorData.detail.message : 'Failed to fetch repository information';
                document.getElementById('results').innerHTML = `<p style="color:red;">Error: ${errorMessage}</p>`;
            } catch (error) {
                console.error("Error parsing JSON from backend:", error);
                document.getElementById('results').innerHTML = '<p style="color:red;">Error: Failed to fetch repository information</p>';
            }
            return;
        }

        const data = await response.json();
        const repos = data.repos;
        const fromCache = data.from_cache;

        let message = fromCache ? 'Data retrieved from cache. ' : 'Data fetched from GitHub API. ';
        document.getElementById('message').innerText = message;

        let tableHTML = '<table border="1"><tr><th>Name</th><th>URL</th><th>Description</th><th>Language</th></tr>';
        for (const repo of repos) {
            tableHTML += `<tr>
                <td>${repo.name}</td>
                <td><a href="${repo.html_url}" target="_blank">${repo.html_url}</a></td>
                <td>${repo.description || ''}</td>
                <td>${repo.language || ''}</td>
            </tr>`;
        }
        tableHTML += '</table>';
        document.getElementById('results').innerHTML = tableHTML;
    } catch (error) {
        console.error('There was an error!', error);
        document.getElementById('results').innerHTML = `<p style="color:red;">An unexpected error occurred. Please try again later.</p>`;
    }
});
