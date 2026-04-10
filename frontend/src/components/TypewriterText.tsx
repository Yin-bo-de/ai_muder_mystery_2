import { useState, useEffect, useRef, useCallback } from 'react'

interface TypewriterTextProps {
  text: string
  speed?: number  // 毫秒/字符
  onComplete?: () => void
  mood?: string
}

const TypewriterText = ({
  text,
  speed = 30,
  onComplete,
  mood
}: TypewriterTextProps) => {
  const [displayText, setDisplayText] = useState('')
  const [isComplete, setIsComplete] = useState(false)
  const [isSkipped, setIsSkipped] = useState(false)
  const indexRef = useRef(0)
  const timeoutRef = useRef<NodeJS.Timeout | null>(null)

  // 根据mood调整速度
  const getSpeed = useCallback(() => {
    let baseSpeed = speed
    if (mood === 'nervous' || mood === 'scared') {
      baseSpeed *= 0.7  // 紧张时语速快
    } else if (mood === 'calm') {
      baseSpeed *= 1.2  // 冷静时语速慢
    }
    return baseSpeed
  }, [speed, mood])

  const typeNextChar = useCallback(() => {
    if (indexRef.current >= text.length) {
      setIsComplete(true)
      onComplete?.()
      return
    }

    setDisplayText(text.slice(0, indexRef.current + 1))
    indexRef.current += 1

    timeoutRef.current = setTimeout(typeNextChar, getSpeed())
  }, [text, getSpeed, onComplete])

  const skipAnimation = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }
    setDisplayText(text)
    setIsComplete(true)
    setIsSkipped(true)
    onComplete?.()
  }, [text, onComplete])

  useEffect(() => {
    // 重置
    indexRef.current = 0
    setDisplayText('')
    setIsComplete(false)
    setIsSkipped(false)

    // 开始打字
    timeoutRef.current = setTimeout(typeNextChar, 100)

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [text, typeNextChar])

  return (
    <span
      onClick={!isComplete ? skipAnimation : undefined}
      style={{
        cursor: !isComplete ? 'pointer' : 'default'
      }}
    >
      {displayText}
      {!isComplete && !isSkipped && (
        <span
          style={{
            display: 'inline-block',
            width: '0.6em',
            animation: 'blink 1s step-end infinite'
          }}
        >
          |
        </span>
      )}
      <style>{`
        @keyframes blink {
          50% { opacity: 0; }
        }
      `}</style>
    </span>
  )
}

export default TypewriterText
