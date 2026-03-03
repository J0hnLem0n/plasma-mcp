import { useState, useMemo } from 'react'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { Copy, Check } from 'lucide-react'

interface Props {
  language: string
  children: string
}

const HEX_REGEX = /#([0-9a-fA-F]{3,8})\b/g

function extractColors(code: string): string[] {
  const matches = code.match(HEX_REGEX)
  if (!matches) return []
  return [...new Set(matches)]
}

function ColorChip({ color }: { color: string }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async (e: React.MouseEvent) => {
    e.stopPropagation()
    await navigator.clipboard.writeText(color)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <button className="color-chip" onClick={handleCopy} title={`Копировать ${color}`}>
      <span className="color-chip__swatch" style={{ backgroundColor: color }} />
      <span className="color-chip__value">{color}</span>
      {copied ? <Check size={10} /> : <Copy size={10} />}
    </button>
  )
}

export function CodeBlock({ language, children }: Props) {
  const [copied, setCopied] = useState(false)
  const colors = useMemo(() => extractColors(children), [children])

  const handleCopy = async () => {
    await navigator.clipboard.writeText(children)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="code-block">
      <div className="code-block__header">
        <span className="code-block__lang">{language || 'code'}</span>
        <button className="code-block__copy" onClick={handleCopy} title="Копировать код">
          {copied ? <Check size={14} /> : <Copy size={14} />}
          {copied ? 'Скопировано' : 'Копировать'}
        </button>
      </div>
      <SyntaxHighlighter
        language={language || 'text'}
        style={oneDark}
        customStyle={{
          margin: 0,
          borderRadius: colors.length ? '0' : '0 0 8px 8px',
          fontSize: '13px',
        }}
      >
        {children}
      </SyntaxHighlighter>
      {colors.length > 0 && (
        <div className="code-block__colors">
          {colors.map((c) => <ColorChip key={c} color={c} />)}
        </div>
      )}
    </div>
  )
}
