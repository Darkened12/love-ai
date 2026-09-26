export interface WebsocketsMessage {
    type: string,
    chat_id: string,
    role: "user" | "assistant",
    message_id: number,
    message: string,
    timestamp: string
}