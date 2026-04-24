# Intercom API POC

This is a simple FastAPI-based integration with the Intercom REST API. This covers **Contacts**, **Conversations**, and **Webhooks**. This test was built to demonstrate the creation of contacts, starting and replying to conversations, and receiving real-time webhook events from Intercom. 

The original test was to use Fin AI API however the API threw up the error code **api_plan_restricted** and the message "Fin Agent API is not enabled for your app" with error code 403 which means that the /fin/start endpoint is gated behind Fin Agent API access.
Intercom’s current Fin Agent API docs say the API is for accessing Fin programmatically via /fin/start and /fin/reply, and they also say: "Please reach out to your accounts team to discuss access".

---

## Use Case
This is a fraud detection system that flags a suspicious transaction. The FastAPI service automatically creates an Intercom contact for the customer, opens a conversation in the Intercom inbox for the support team to review, and listens via webhook for when the analyst closes or resolves the case which feeds the outcome back to your system.
The steps to execute the use case can be found here: [Link Text](use_case_testing_steps.md). This should be executing after following the steps listed in this guide else the use case will not work.

---

## Project Structure

```
├── fin_agent.py            # FastAPI app entry point — registers all routers
├── config.py               # Loads environment variables via .env
├── internal_headers.py     # Builds Intercom auth headers for every request
├── contact.py              # Pydantic models for Contact request / response
├── conversation.py         # Pydantic models for Conversation request / response
├── routers/
│   ├── contact_router.py       # Contact endpoints (create, get by ID, get by email)
│   └── conversations_router.py # Conversation endpoints (start, search, reply, webhook)
├── requirements.txt        # This will install the required libraries
├── .env                    # ← You create this (not committed to git)
└── .gitignore
└── use_case_testing_steps.md   # This file contains the steps to run the use case
```
The fin_agent.py was suppose to test the Fin Agent AI API but kept the file name. 
In the future should there access be granted, this file will be adapted accordingly.

---

## Prerequisites

Make sure the following tools are installed before commencing:

| Tool | Minimum version | Check |
|------|----------------|-------|
| Python | 3.13+ | `python --version` |
| pip | 23+ | `pip --version` |
| Git | any | `git --version` |

---

## 1. Clone the Repository

```bash
git https://github.com/revglen/intercom-testo.git
cd intercom-testo
```
This bring down the Repo to your system and create a new folder.
Navigate to the this folder to start executing the test

---

## 2. Create a Virtual Environment

Creating a virtual environment is highly encouraged to keep dependencies isolated.

**macOS / Linux**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (Command Prompt)**
```cmd
python -m venv venv
.\venv\Scripts\activate.bat
```

After executing this command, one should see `(venv)` appearing at the start of the terminal prompt.
This incase that the virtual environment is working. Next, the dependencies need to be installed.

---

## 3. Install Dependencies
Run the below command to install the dependencies. If they are not installed, the test will fail to execute.

```bash
pip install -r requirements.txt
```

```cmd
pip install -r requirements.txt
```

This installs:

- **FastAPI** — the web framework
- **Uvicorn** — ASGI server to run FastAPI
- **httpx** — async HTTP client for outbound API calls
- **requests** — sync HTTP client which is primarily used for contact creation
- **python-dotenv** — loads `.env` file into environment variables
- **pydantic** — data validation and serialisation
- **pydantic[email]** — email validation support

---

## 4. Configure Environment Variables

Create a `.env` file in the root of the project (the same folder as `fin_agent.py`):

```bash
touch .env
```

```cmd
echo > .env
```

This file can also be created in Windows Explorer. 

Add the following variables:

```env
# Your Intercom Access Token (from Developer Hub → Authentication)
FIN_AGENT_ACCESS_TOKEN=your_intercom_access_token_here

# Intercom base API URL (do not change unless using a proxy)
INTERCOM_URL=https://api.intercom.io

# Intercom API version
INTERCOM_VERSION=2.14
```

> **Where to get your Access Token:**
> 1. Log in to [app.intercom.com](https://app.intercom.com)
> 2. Go to **Settings → Integrations → Developer Hub**
> 3. Create a new app (or open an existing one)
> 4. Go to **Authentication** and copy your **Access Token**

> **Important:** The `.env` file is listed in `.gitignore` and will not be committed.

---

## 5. Run the Application

```bash or cmd
python fin_agent.py
```

Or using uvicorn directly:

```bash or cmd
uvicorn fin_agent:app --host 0.0.0.0 --port 8000 --reload
```

The `--reload` flag automatically restarts the server when one makes changes in a file which is useful during development.

You should see output like:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Intercom configuration is completed...
```

This indicates that the server is up and running and there are no issues.

---

## 6. Verify the Server is Running

Open the browser or run:

```bash or cmd
curl http://localhost:8000/health
```

The expected response would be:

```json
{
  "status": "healthy",
  "service": "Fin AI Agent Testo"
}
```

---

## 7. Explore the API Docs

FastAPI automatically generates interactive documentation. With the server running, open:

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 8. Install and Configure ngrok (for Webhooks)

Intercom webhooks need to reach the local server over the public HTTPS URL. 
**ngrok** creates a secure tunnel from the internet to the `localhost`.

### Install ngrok

**macOS (Homebrew)**
```bash
brew install ngrok/ngrok/ngrok
```

**Windows (Chocolatey)**
```cmd
choco install ngrok
```

**Linux / Manual install**

Download the binary from [https://ngrok.com/download](https://ngrok.com/download) and move it to your PATH:

```bash
# Example for Linux amd64
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar -xzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/
```

Verify the install:

```bash
ngrok version
```

### Create a free ngrok account

Go to [https://dashboard.ngrok.com/signup](https://dashboard.ngrok.com/signup) and sign up for a free account.

### Authenticate ngrok

Copy your **Authtoken** from the ngrok dashboard and run:

```bash
ngrok config add-authtoken <your_authtoken>
```

This saves your token to `~/.config/ngrok/ngrok.yml` and only needs to be done once.

### Start the tunnel

With your FastAPI server already running on port 8000, open a **second terminal** and run:

```bash
ngrok http 8000
```

You will see output like:

```
Session Status     online
Account            your@email.com
Forwarding         https://a1b2-12-34-56-78.ngrok-free.app -> http://localhost:8000
```

Copy the `https://` forwarding URL — this is your public endpoint.

> **Note:** The free ngrok URL changes every time you restart ngrok. You will need to re-register it in Intercom each session. A paid ngrok plan gives you a fixed subdomain.

### Register the webhook in Intercom

1. Go to **Settings → Integrations → Developer Hub → Your App → Webhooks**
2. Set the **Endpoint URL** to:
   ```
   https://a1b2-12-34-56-78.ngrok-free.app/conversations/webhook
   ```
3. Select the topics you want to subscribe to, for example:
   - `conversation.created`
   - `conversation.admin.closed`
   - `contact.created`
4. Save. Intercom will send a verification ping to your endpoint immediately.

---

## API Endpoints Reference

### Contacts

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/contacts/` | Create a new contact |
| `GET` | `/contacts/{contact_id}` | Get a contact by Intercom ID |
| `GET` | `/contacts/email/{email}` | Find a contact by email address |

**Create contact — example request body:**
```json
{
  "role": "user",
  "external_id": "cust-001",
  "email": "glen@example.com",
  "name": "Rev Glen Saldanha"
}
```

---

### Conversations

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/conversations/` | Start a new conversation |
| `POST` | `/conversations/search/{created_at}` | Search conversations by timestamp |
| `POST` | `/conversations/{conversation_id}/reply` | Reply to an existing conversation |
| `POST` | `/conversations/webhook` | Receives incoming Intercom webhook events |
| `HEAD` | `/conversations/webhook` | Webhook verification ping from Intercom |

**Start conversation — example request body:**
```json
{
  "from_user": {
    "type": "user",
    "id": "<intercom_contact_id>"
  },
  "body": "I need help with my account."
}
```

**Reply to conversation — example request body:**
```json
{
  "message_type": "comment",
  "type": "user",
  "intercom_user_id": "<intercom_contact_id>",
  "body": "Thank you, I have reviewed my account."
}
```

---

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `401 Unauthorized` | Invalid or missing Access Token | Check `FIN_AGENT_ACCESS_TOKEN` in your `.env` |
| `409 Conflict` | Contact with that email already exists | The API returns a message — no crash |
| `404 Not Found` | Contact ID or conversation ID does not exist | Verify the ID is from your sandbox workspace |
| `422 Unprocessable Entity` | Request body fails validation | Check the required fields match the Pydantic model |
| `ngrok tunnel not found` | FastAPI is not running when ngrok starts | Start `python fin_agent.py` before running ngrok |
| Webhook not received | ngrok URL not registered in Intercom | Re-register the new ngrok URL in Developer Hub |

---

## Stopping the Server

Press `CTRL + C` in the terminal running uvicorn, and `CTRL + C` in the terminal running ngrok.

To deactivate the virtual environment when done:

```bash or cmd
deactivate
```
