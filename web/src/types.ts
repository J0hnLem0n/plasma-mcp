export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

export interface TokenInfo {
  value: string
  comment: string
}
