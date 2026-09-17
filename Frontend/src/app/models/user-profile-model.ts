export interface UserProfile {
    id: number
    username: string
    system_prompt: string | null
    profile_picture: string | null
    assistant_profile_picture: string | null
}