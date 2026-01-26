import { AlertTriangle, RefreshCw } from "lucide-react";
import { Component, ErrorInfo, ReactNode } from "react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class GlobalErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught error:", error, errorInfo);
  }

  private handleReload = () => {
    window.location.reload();
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div className="flex h-screen w-screen flex-col items-center justify-center bg-black text-red-500 font-mono p-6">
          <div className="max-w-md w-full border border-red-900/50 bg-red-950/10 p-8 rounded-lg shadow-2xl backdrop-blur-sm">
            <div className="flex items-center gap-4 mb-6">
              <AlertTriangle className="w-12 h-12 text-red-600 animate-pulse" />
              <div>
                <h1 className="text-2xl font-black uppercase tracking-widest text-red-500">
                  Critical Failure
                </h1>
                <p className="text-xs text-red-400/60 uppercase tracking-widest">
                  System Integrity Compromised
                </p>
              </div>
            </div>

            <div className="bg-black/50 p-4 rounded border border-red-900/30 mb-8 font-mono text-sm overflow-auto max-h-48">
              <p className="text-red-400 mb-2">Error Details:</p>
              <code className="text-zinc-500 break-all">
                {this.state.error?.message || "Unknown Error"}
              </code>
            </div>

            <button
              onClick={this.handleReload}
              className="w-full flex items-center justify-center gap-2 bg-red-900/20 hover:bg-red-900/40 text-red-400 hover:text-red-200 py-3 px-4 rounded border border-red-800/50 transition-all group"
            >
              <RefreshCw className="w-4 h-4 group-hover:rotate-180 transition-transform duration-500" />
              <span className="uppercase tracking-wider font-bold text-sm">
                Reboot System
              </span>
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
