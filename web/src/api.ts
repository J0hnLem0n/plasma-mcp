import type { TokenInfo } from './types'

export async function sendMessage(
  message: string,
  history: { role: string; content: string }[],
): Promise<string> {
  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, history }),
  })
  const data = await res.json()
  if (data.error) throw new Error(data.error)
  return data.answer
}

export async function searchTokens(query: string): Promise<Record<string, TokenInfo>> {
  const res = await fetch(`/api/tokens?q=${encodeURIComponent(query)}`)
  const data = await res.json()
  return data.tokens
}
