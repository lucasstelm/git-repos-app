import httpx
import datetime
import motor.motor_asyncio
from fastapi import FastAPI, HTTPException,Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from models.pydantic_models import UserRepos, Repository
from typing import List, Optional
from fastapi_utils.tasks import repeat_every

# Create the FastAPI app
app = FastAPI()

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Setup MongoDB client
client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://db/repoinfo")
db = client.github_repos

# Returns the index.html template when the user visits the root path
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Main API endpoint. Returns the user's repositories
@app.post("/get_repos")
async def get_repos(username: str = Form(...)):

    # Check if username already exists in the database
    cached_data = await db.repositories.find_one({"username": username})
    if cached_data:
        repos_info = [Repository(**repo) for repo in cached_data["repos"]]
        return {"repos": repos_info, "from_cache": True}
    
    # If not, fetch the data from GitHub and update the database
    repos_info = await update_user_data(username)
    if repos_info is None:
        raise HTTPException(status_code=404, detail="GitHub user not found")

    return {"repos": repos_info, "from_cache": False}

# Updates the database with the user's repositories and returns the data
async def update_user_data(username: str) -> Optional[List[Repository]]:
    repos_info = await fetch_github_repos(username)
    if repos_info is not None:
        user_repos = UserRepos(username=username, repos=repos_info)
        await db.repositories.update_one(
            {"username": username},
            {"$set": user_repos.dict()},
            upsert=True
        )
    return repos_info

# Fetches the user's repositories from GitHub
async def fetch_github_repos(username: str) -> Optional[List[Repository]]:
    
    # GitHub API endpoint
    url = f"https://api.github.com/users/{username}/repos"

    # Fetch the data
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            content = response.json()
            message = content.get('message', 'Failed to fetch repository information')
            detail = {'status_code': response.status_code, 'message': message}
            print("Sending error to frontend:", detail)
            raise HTTPException(status_code=400, detail=detail)

        # Parse the reponse data and validate it with Pydantic before returning
        repos = response.json()
        repos_info: List[Repository] = []
        for repo in repos[:5]:
            repo_info = Repository(
                name=repo["name"],
                html_url=repo["html_url"],
                description=repo.get("description"),
                language=repo.get("language")
            )
            repos_info.append(repo_info)
            
        return repos_info
    
# This function is called every hour to update the database
async def fetch_and_update_data():
    # Using an async cursor to iterate over the database documents
    async for user in db.repositories.find({}, {"username": 1, "_id": 0}):
        await update_user_data(user["username"])

# This function is called when the app starts and then every hour
@app.on_event("startup")
@repeat_every(seconds=60 * 60, wait_first=True)  # 60 seconds * 60 minutes = 1 hour
async def periodic_task() -> None:
    await fetch_and_update_data()
    now = datetime.datetime.now()
    print(f"Data updated successfully. {now}")