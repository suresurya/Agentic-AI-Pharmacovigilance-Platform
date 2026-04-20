import type { WSEvent } from '../types'

type WSListener = (event: WSEvent) => void

class PipelineWebSocket {
  private ws: WebSocket | null = null
  private listeners: WSListener[] = []
  private narrativeId: string | null = null

  connect(narrativeId: string) {
    this.disconnect()
    this.narrativeId = narrativeId
    const base = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000'
    this.ws = new WebSocket(`${base}/ws/pipeline/${narrativeId}`)

    this.ws.onmessage = (e) => {
      try {
        const event: WSEvent = JSON.parse(e.data)
        this.listeners.forEach(l => l(event))
      } catch {}
    }

    this.ws.onclose = () => {
      // Auto-reconnect after 2s if still on same narrative
      setTimeout(() => {
        if (this.narrativeId === narrativeId) this.connect(narrativeId)
      }, 2000)
    }
  }

  disconnect() {
    if (this.ws) {
      this.narrativeId = null
      this.ws.close()
      this.ws = null
    }
  }

  onEvent(listener: WSListener) {
    this.listeners.push(listener)
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener)
    }
  }
}

export const pipelineWS = new PipelineWebSocket()
