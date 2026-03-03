import ReactMarkdown from 'react-markdown'
import type { Components } from 'react-markdown'
import { Bot, User } from 'lucide-react'
import { CodeBlock } from './CodeBlock'
import { ColorToken } from './ColorToken'
import type { Message } from '../types'

interface Props {
  message: Message
}

const HEX_COLOR_REGEX = /^#([0-9a-fA-F]{3,8})$/

const markdownComponents: Components = {
  pre({ children }) {
    return <>{children}</>
  },
  code({ className, children, ...props }) {
    const match = /language-(\w+)/.exec(className || '')
    const code = String(children).replace(/\n$/, '')

    if (match || code.includes('\n')) {
      return <CodeBlock language={match ? match[1] : 'text'}>{code}</CodeBlock>
    }

    const colorMatch = HEX_COLOR_REGEX.exec(code.trim())
    if (colorMatch) {
      return <ColorToken name="" color={code.trim()} />
    }

    return (
      <code className="inline-code" {...props}>
        {children}
      </code>
    )
  },
}

export function ChatMessage({ message }: Props) {
  const isUser = message.role === 'user'

  return (
    <div className={`chat-message ${isUser ? 'chat-message--user' : 'chat-message--assistant'}`}>
      <div className="chat-message__avatar">
        {isUser ? <User size={18} /> : <Bot size={18} />}
      </div>
      <div className="chat-message__body">
        {isUser ? (
          <p>{message.content}</p>
        ) : (
          <div className="chat-message__content">
            <ReactMarkdown components={markdownComponents}>
              {message.content}
            </ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  )
}
