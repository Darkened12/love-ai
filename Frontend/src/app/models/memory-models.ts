export interface MemoryMetadata {
    user_id: string
    fact_id: string
    created_at: string | null
}

export interface Memory {
    id: string
    fact: string
    metadata: MemoryMetadata
}