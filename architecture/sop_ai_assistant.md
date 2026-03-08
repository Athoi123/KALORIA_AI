# SOP: AI Diet Assistant (Layer 1 Architecture)

## 1. Goal
Respond to user queries about their diet, progress, and mental well-being while adhering strictly to behavioral rules.

## 2. Inputs
- `user_id` (uuid)
- `message` (string)
- `context` (dict containing goals and recent meals)

## 3. Tool Logic Sequence (Layer 3 mapping)
1. **Tool 1: `context_builder.py`**
   - Input: `user_id`
   - Action: Query MongoDB for today's calorie status and recent food logs. 
   - Output: Structured context dictionary.
2. **Tool 2: `ai_responder.py`**
   - Input: `message`, structured context dict, `goal_type`.
   - Action: Pass data to OpenAI/Gemini with system prompt enforcing Tone Rules (Friendly, Supportive) and MUST NOTs (No medical diagnosis).
   - Output: AI text response string.
3. **Tool 3: `chat_logger.py`**
   - Input: `user_id`, `message`, AI response.
   - Action: Save to MongoDB `chat_history`.

## 4. Edge Cases & Fallbacks
- **User requests medical advice:** LLM must gracefully pivot, stating it is an AI assistant, not a doctor, and recommend seeking professional medical help.
- **Toxicity/Self-Harm detected:** Trigger fail-safe response immediately providing mental health helpline resources. Send alert notification via Firebase.
