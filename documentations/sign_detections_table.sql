-- Create chat_conversation table in Supabase

CREATE TABLE IF NOT EXISTS chat_conversation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sender_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    receiver_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    raw_text TEXT NOT NULL,
    cleaned_text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_chat_conversation_sender_id ON chat_conversation(sender_id);
CREATE INDEX IF NOT EXISTS idx_chat_conversation_receiver_id ON chat_conversation(receiver_id);
CREATE INDEX IF NOT EXISTS idx_chat_conversation_created_at ON chat_conversation(created_at DESC);

-- Composite index for conversation threads between two users
CREATE INDEX IF NOT EXISTS idx_chat_conversation_users ON chat_conversation(sender_id, receiver_id, created_at DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE chat_conversation ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view messages where they are sender or receiver
CREATE POLICY "Users can view their conversations"
    ON chat_conversation
    FOR SELECT
    USING (
        auth.uid() = sender_id OR 
        auth.uid() = receiver_id
    );

-- Policy: Users can insert messages as sender
CREATE POLICY "Users can send messages"
    ON chat_conversation
    FOR INSERT
    WITH CHECK (auth.uid() = sender_id);

-- Policy: Users can delete messages they sent
CREATE POLICY "Users can delete own messages"
    ON chat_conversation
    FOR DELETE
    USING (auth.uid() = sender_id);

-- Optional: Create a trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_chat_conversation_updated_at
    BEFORE UPDATE ON chat_conversation
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Optional: Create a view to get conversation threads
CREATE OR REPLACE VIEW conversation_threads AS
SELECT 
    CASE 
        WHEN sender_id < receiver_id THEN sender_id
        ELSE receiver_id
    END as user1_id,
    CASE 
        WHEN sender_id < receiver_id THEN receiver_id
        ELSE sender_id
    END as user2_id,
    MAX(created_at) as last_message_at,
    COUNT(*) as message_count
FROM chat_conversation
GROUP BY user1_id, user2_id;
