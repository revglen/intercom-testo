# Postman Testing Guide

This is an end-to-end test guide for the Intercom Fraud Detection POC. Covers contact creation, conversation management and webhook simulation.

---

## Prerequisites

- FastAPI server running locally (`python fin_agent.py`)
- Postman installed — [download here](https://www.postman.com/downloads/)
- `.env` file configured with a valid `FIN_AGENT_ACCESS_TOKEN`. Please check README.md
- *(For webhook tests only)* ngrok running and registered in Intercom Developer Hub. This is crucial.

---

## Setup — Import and Configure

### A. Import the collection

1. Open Postman
2. Click **Import** (top left)
3. Drag and drop `Intercom_Fraud_POC.postman_collection.json`
4. Click **Import**

The collection will appear in the left sidebar with all requests pre-configured.

### B. Confirm of Postman variables

In the collection sidebar, click the three dots next to the collection name → **Edit** → **Variables** tab.

| Variable | Default value | Description |
|----------|--------------|-------------|
| `base_url` | `http://localhost:8000` | FastAPI local server |
| `contact_id` | *(auto-populated)* | Saved from Step 2 response |
| `conversation_id` | *(auto-populated)* | Saved from Step 3 response |

> **Webhook testing:** Replace `base_url` with your ngrok URL before running Step 5:
> ```
> https://xxxx.ngrok-free.app
> ```

### C. Start your FastAPI server

```bash or cmd
python fin_agent.py
```

Wait for the following line to appear before sending any requests:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```
This line indicates that the server is up and running.

---

## Run the test in the following sequence

> **Important:** Steps must be run in the following order. `contact_id` is auto-saved from Step 2 and injected into Step 3. `conversation_id` is auto-saved from Step 3 and injected into Step 4. This avoids any copy-paste process as the values are auto-populated from the API calls.

---

### Step 1 — Health check

Confirms the server is running before executing any other requests.

| | |
|---|---|
| Method | `GET` |
| Endpoint | `/health` |
| Expected status | `200 OK` |
| Expected body | `{"status": "healthy", "service": "Fin AI Agent Testo"}` |

---

### Step 2 — Create contact (fraud customer)

Creates a new Intercom contact representing the flagged customer. The `contact_id` returned is saved automatically to the collection variable.

| | |
|---|---|
| Method | `POST` |
| Endpoint | `/contacts/` |
| Expected status | `200` or `201` |
| Auto-saved variable | `contact_id` |

**Request body:**
```json
{
  "role": "user",
  "external_id": "fraud-cust-001",
  "email": "glen.test@fraudpoc.com",
  "name": "Glen Saldanha"
}
```

**Tests run automatically:**
- Contact created successfully
- Response contains `id`
- `contact_id` saved to collection variable
- Role equals `user`
- Response time under 3 seconds

> After this step, open the collection **Variables** tab and confirm `contact_id` is populated. If it is empty, the `FIN_AGENT_ACCESS_TOKEN` in the `.env` is invalid or missing.

---

### Step 2b — Verify contact by email

One can search Intercom for the contact by email to confirm whether if it was created correctly. This will also validate the search endpoint.

| | |
|---|---|
| Method | `GET` |
| Endpoint | `/contacts/email/glen.test@fraudpoc.com` |
| Expected status | `200` |

**Tests run automatically:**
- Contact found by email
- Email field matches `glen.test@fraudpoc.com`
- Returned `id` matches saved `contact_id` variable

---

### Step 3 — Start fraud conversation

Opens a new Intercom conversation for the flagged customer. Uses `{{contact_id}}` from Step 2. The `conversation_id` is saved automatically for use in Step 4.

| | |
|---|---|
| Method | `POST` |
| Endpoint | `/conversations/` |
| Expected status | `200` |
| Auto-saved variable | `conversation_id` |

**Request body:**
```json
{
  "from_user": {
    "type": "user",
    "id": "{{contact_id}}"
  },
  "body": "FRAUD ALERT: Suspicious transaction detected on account fraud-cust-001. Transaction amount: €4,850. Location: Lalox, Kamus <fiction city and country>. Risk score: 0.94. Please review immediately."
}
```

**Tests run automatically:**
- Conversation created successfully
- Response contains `id`
- `conversation_id` saved to collection variable
- Response contains `created_at` timestamp
- Response time under 5 seconds

> After this step, open the Intercom sandbox inbox where one should see the conversation appear with the fraud alert message.

---

### Step 4 — Reply to conversation (analyst decision)

Posts an analyst decision reply to the open fraud conversation. Uses both `{{contact_id}}` and `{{conversation_id}}` saved from previous steps.

| | |
|---|---|
| Method | `POST` |
| Endpoint | `/conversations/{{conversation_id}}/reply` |
| Expected status | `200` |

**Request body:**
```json
{
  "message_type": "comment",
  "type": "user",
  "intercom_user_id": "{{contact_id}}",
  "body": "Case reviewed. Transaction confirmed as fraudulent. Account has been flagged and card blocked. Customer notified via email. Case ID: FRAUD-2026-001."
}
```

**Tests run automatically:**
- Reply posted successfully
- Response is valid JSON

> Verify in the Intercom inbox that the reply appears in the conversation thread.

---

### Step 5 — Simulate the webhook to close conversation

Simulates Intercom firing a `conversation.admin.closed` webhook event to your endpoint.

| | |
|---|---|
| Method | `POST` |
| Endpoint | `/conversations/webhook` |
| Expected status | `200` |
| Expected body | `{"message": "Webhook received successfully"}` |
| Expected response time | Under 2 seconds |

**Request body:**
```json
{
  "type": "notification_event",
  "topic": "conversation.admin.closed",
  "data": {
    "type": "notification_event_data",
    "item": {
      "type": "conversation",
      "id": "{{conversation_id}}",
      "state": "closed"
    }
  }
}
```

**Tests run automatically:**
- Webhook accepted with `200`
- Response message confirms receipt
- Response time under 2 seconds

> **Real end-to-end webhook test:** Replace `base_url` with the ngrok URL and register it in Intercom's Developer Hub under Settings → Integrations → Developer Hub → Your App → Webhooks. Then close the conversation manually in your Intercom sandbox — the real webhook fires automatically to your endpoint.

---

### Step 5b — Webhook HEAD verification

Intercom sends a HEAD request to verify the endpoint is reachable before registering it in the Developer Hub. Confirms the endpoint responds correctly.

| | |
|---|---|
| Method | `HEAD` |
| Endpoint | `/conversations/webhook` |
| Expected status | `200` |

---

### Step 6 — Final contact verification

Retrieves the contact by ID to confirm the full record is intact in Intercom after the end-to-end flow.

| | |
|---|---|
| Method | `GET` |
| Endpoint | `/contacts/{{contact_id}}` |
| Expected status | `200` |

**Tests run automatically:**
- Contact retrieved successfully
- Returned `id` matches saved `contact_id` variable
- Name equals `Glen Saldanha`

---

## Run the Entire Collection at Once

Use the **Collection Runner** to run all requests in a single pass:

1. Right-click the collection name in the sidebar
2. Select **Run collection**
3. Set **Iterations** to `1`
4. Set **Delay** to `500ms` — this gives Intercom time to process between requests
5. Click **Run Intercom Fraud Detection Testo**

The runner respects auto-saved variables — `contact_id` from Step 2 flows into Step 3, and `conversation_id` from Step 3 flows into Step 4. All 11 requests run in order and a pass/fail summary is shown at the end.

---

## Expected Test Results Summary

| Request | Tests | Expected result |
|---------|-------|----------------|
| Step 1 — Health check | 2 | All pass |
| Step 2 — Create contact | 4 | All pass |
| Step 2b — Verify by email | 3 | All pass |
| Step 2c — Duplicate contact | 2 | All pass (409 handled) |
| Step 3 — Start conversation | 4 | All pass |
| Step 4 — Reply | 2 | All pass |
| Step 5 — Simulate webhook | 3 | All pass |
| Step 5b — HEAD verification | 1 | All pass |
| Step 6 — Final verify | 3 | All pass |