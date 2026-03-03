import { useState } from 'react'
import { Copy, Check } from 'lucide-react'

interface Props {
  name: string
  color: string
}

function isValidColor(str: string): boolean {
  return /^#([0-9a-fA-F]{3,8})$/.test(str) || /^rgba?\(/.test(str)
}

export function ColorToken({ name, color }: Props) {
  const [copied, setCopied] = useState(false)

  if (!isValidColor(color)) return null

  const handleCopy = async () => {
    await navigator.clipboard.writeText(color)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <span className="color-token" onClick={handleCopy} title={`Копировать ${color}`}>
      <span className="color-token__swatch" style={{ backgroundColor: color }} />
      {name && <span className="color-token__name">{name}</span>}
      <span className="color-token__value">{color}</span>
      {copied ? <Check size={12} /> : <Copy size={12} />}
    </span>
  )
}
