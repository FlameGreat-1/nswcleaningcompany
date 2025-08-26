import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // This captures EVERYTHING
    console.group('🚨 COMPLETE ERROR DETAILS');
    console.error('Error:', error);
    console.error('Error Message:', error.message);
    console.error('Error Stack:', error.stack);
    console.error('Component Stack:', errorInfo.componentStack);
    console.error('Props:', this.props);
    console.groupEnd();
    
    // Log to external service if needed
    this.setState({ error, errorInfo });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '20px', backgroundColor: '#fee', border: '1px solid #fcc' }}>
          <h2>🚨 Error Caught!</h2>
          <details>
            <summary>Click for full error details</summary>
            <pre style={{ fontSize: '12px', overflow: 'auto', backgroundColor: '#f5f5f5', padding: '10px' }}>
              <strong>Error:</strong> {this.state.error?.toString()}
              <br/><br/>
              <strong>Stack Trace:</strong>
              <br/>{this.state.error?.stack}
              <br/><br/>
              <strong>Component Stack:</strong>
              <br/>{this.state.errorInfo?.componentStack}
            </pre>
          </details>
          <button onClick={() => window.location.reload()}>Reload Page</button>
        </div>
      );
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
