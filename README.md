# GitHub Repositories Info API

This project provides a FastAPI application to fetch and display GitHub user repositories. The data is fetched from GitHub API and stored in MongoDB. The application also updates the data every hour.

## Features

- Fetch GitHub user repositories
- Cache repositories data in MongoDB
- Update cached data every hour
- Frontend to search and display repositories
- Handle GitHub API errors

## Prerequisites

Before you begin, ensure you have Docker installed.

## Usage

```sh
    git clone https://github.com/lucasstelm/git-repos-app.git
    cd git-repos-app
    docker compose up --build
```

The last command will build the Docker images and start the containers.

After the containers are up and running, you can access the application by navigating to http://localhost:80 in your web browser.

## API Endpoints

### GET /
Description: Serve the main page of the application.
Response: HTMLResponse - the main page.

### POST /get_repos
Description: Fetch the repositories of a given GitHub username.
Body: username - the GitHub username.
Response: JSON object containing the repositories information and a boolean indicating if the data was retrieved from cache.

## Development

For development purposes, you might want to:

### Access the FastAPI Documentation
Navigate to http://localhost:80/docs in your browser to access the automatically generated API documentation.

### Connect to MongoDB

The MongoDB instance is running in a Docker container. You can connect to it using any MongoDB client with the following connection string:

```sh
mongodb://localhost:27017/repoinfo
```
