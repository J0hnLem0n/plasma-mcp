import { useState, useRef, useEffect } from 'react'
import { Sparkles } from 'lucide-react'
import { ChatMessage } from './components/ChatMessage'
import { ChatInput } from './components/ChatInput'
import { sendMessage } from './api'
import type { Message } from './types'
import './App.css'

const EXAMPLES = [
  'Как использовать компонент Button?',
  'Какие есть токены для цветов текста?',
  'Покажи пример карточки с ценой',
  'Какие компоненты есть в Plasma?',
]

function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async (text: string) => {
    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: text,
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, userMsg])
    setLoading(true)

    try {
      const history = messages.map((m) => ({ role: m.role, content: m.content }))
      const answer = await sendMessage(text, history)
      const assistantMsg: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: answer,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, assistantMsg])
    } catch (err) {
      const errorMsg: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: `Ошибка: ${err instanceof Error ? err.message : 'Неизвестная ошибка'}`,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMsg])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="app__header">
        <Sparkles size={22} />
        <h1>Plasma AI Assistant</h1>
      </header>

      <main className="app__chat">
        {messages.length === 0 ? (
          <div className="welcome">
            <div className="welcome__icon">
              <Sparkles size={40} />
            </div>
            <h2>Привет! Я помощник по Plasma UI Kit</h2>
            <p>Спросите меня о компонентах, токенах, стилях или гайдлайнах</p>
            <div className="welcome__examples">
              {EXAMPLES.map((ex) => (
                <button key={ex} className="welcome__example" onClick={() => handleSend(ex)}>
                  {ex}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="messages">
            {messages.map((msg) => (
              <ChatMessage key={msg.id} message={msg} />
            ))}
            {loading && (
              <div className="chat-message chat-message--assistant">
                <div className="chat-message__avatar"><Sparkles size={18} /></div>
                <div className="chat-message__body">
                  <div className="typing-indicator">
                    <span /><span /><span />
                  </div>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        )}
      </main>

      <footer className="app__footer">
        <ChatInput onSend={handleSend} disabled={loading} />
      </footer>
    </div>
  )
}

export default App
