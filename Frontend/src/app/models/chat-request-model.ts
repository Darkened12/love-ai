export interface ChatRequest {
    message: string;
    session_id: string;
    system_prompt: string | null;
}