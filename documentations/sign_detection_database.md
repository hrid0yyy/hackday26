# Sign Detection - Conversations Database

## Create Table in Supabase

Run this SQL in your Supabase SQL Editor:

```sql
-- Create chat_conversation table
CREATE TABLE IF NOT EXISTS chat_conversation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sender_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    receiver_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    raw_text TEXT NOT NULL,
    cleaned_text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_chat_conversation_sender_id ON chat_conversation(sender_id);
CREATE INDEX IF NOT EXISTS idx_chat_conversation_receiver_id ON chat_conversation(receiver_id);
CREATE INDEX IF NOT EXISTS idx_chat_conversation_created_at ON chat_conversation(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_conversation_users ON chat_conversation(sender_id, receiver_id, created_at DESC);

-- Enable RLS
ALTER TABLE chat_conversation ENABLE ROW LEVEL SECURITY;

-- Policies
CREATE POLICY "Users can view their conversations"
    ON chat_conversation FOR SELECT
    USING (auth.uid() = sender_id OR auth.uid() = receiver_id);

CREATE POLICY "Users can send messages"
    ON chat_conversation FOR INSERT
    WITH CHECK (auth.uid() = sender_id);
```

## Table Schema

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Message ID (auto-generated) |
| `sender_id` | UUID | User who sent the message |
| `receiver_id` | UUID | User receiving the message |
| `raw_text` | TEXT | Original text from sign detection (e.g., "iaammmliikee") |
| `cleaned_text` | TEXT | LLM-cleaned text (e.g., "i am like") |
| `created_at` | TIMESTAMP | When message was sent |
| `updated_at` | TIMESTAMP | Last updated timestamp |

## Usage

### Frontend: When User Stops Recording

```javascript
async function stopRecording() {
  const rawText = accumulatedText; // "iaammmliikee"
  
  // Stop WebSocket
  ws.close();
  
  // Process and save message (sender_id automatically from JWT)
  const response = await fetch('http://localhost:8000/sign-detection/process-text', {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accessToken}`  // JWT token required
    },
    body: JSON.stringify({
      raw_text: rawText,
      receiver_id: recipientUserId   // Who receives it
    })
  });
  
  const result = await response.json();
  console.log('Message sent:', result.cleaned_text);
  
  // Display in chat
  addMessageToChat(result.cleaned_text, 'sent');
}
```

### Get Conversation History

```javascript
// Query all messages between two users
const { data, error } = await supabase
  .from('chat_conversation')
  .select('*')
  .or(`and(sender_id.eq.${user1},receiver_id.eq.${user2}),and(sender_id.eq.${user2},receiver_id.eq.${user1})`)
  .order('created_at', { ascending: true });
```

## API Endpoint

**POST** `/sign-detection/process-text`

**Request Body:**
```json
{
  "raw_text": "iaammmliikee",
  "receiver_id": "660e8400-e29b-41d4-a716-446655440111"
}
```

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

**Note:** `sender_id` is automatically extracted from the JWT token.

**Response:**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440222",
  "sender_id": "550e8400-e29b-41d4-a716-446655440000",
  "receiver_id": "660e8400-e29b-41d4-a716-446655440111",
  "raw_text": "iaammmliikee",
  "cleaned_text": "i am like",
  "created_at": "2026-01-08T12:34:56.789Z"
}
```

## Query Examples

```sql
-- Get all messages between two users
SELECT * FROM chat_conversation 
WHERE (sender_id = $1 AND receiver_id = $2) 
   OR (sender_id = $2 AND receiver_id = $1)
ORDER BY created_at DESC;
```
