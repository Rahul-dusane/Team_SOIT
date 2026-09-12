import React from 'react'
import { AlertTriangle, RefreshCw } from 'lucide-react'

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, errorInfo) {
    console.error('HireLens UI ErrorBoundary caught an error:', error, errorInfo)
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null })
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="panel my-8 p-8 text-center shadow-panel animate-fade-in border border-rose-500/20 bg-rose-500/5">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-rose-500/10 text-rose-600">
            <AlertTriangle size={28} />
          </div>
          <h3 className="text-lg font-black text-slate-900 tracking-tight">Something went wrong in this section</h3>
          <p className="mt-1 text-xs font-semibold text-slate-500 max-w-md mx-auto">
            {this.state.error?.message || 'An unexpected rendering error occurred.'}
          </p>
          <button
            onClick={this.handleReset}
            className="mt-5 inline-flex items-center gap-2 rounded-full bg-slate-900 px-5 py-2.5 text-xs font-extrabold text-white transition hover:bg-slate-800 shadow-md"
          >
            <RefreshCw size={14} /> Try Again
          </button>
        </div>
      )
    }

    return this.props.children
  }
}
