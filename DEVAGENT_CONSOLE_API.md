# DevAgent Console API

**Added**: February 2, 2026  
**Version**: 5.1.0

DevAgent now exposes a **console API** that lets you interact with it directly from the browser DevTools console!

---

## 🚀 Quick Start

Open your browser console (F12) and type:

```javascript
DevAgent.help();
```

---

## 📚 Available Commands

### `DevAgent.analyze(errorMessage, context?)`

Analyze any error message manually.

```javascript
// Basic usage
DevAgent.analyze("Cannot read property 'subscribe' of null");

// With context
DevAgent.analyze("State update failed", {
  component: "DevAgentMonitor",
  line: 127,
  action: "store subscription",
});
```

**Returns**: Confirmation message and triggers AI analysis

---

### `DevAgent.showFix()`

Display the current fix suggestion in the console.

```javascript
DevAgent.showFix();
// Returns the full FixSuggestion object with:
// - issue_summary
// - root_cause
// - fix_code
// - fix_steps
// - confidence
// - prevention_tips
```

---

### `DevAgent.errors()`

View error history in a formatted table.

```javascript
DevAgent.errors();
// Shows last 10 errors with:
// - Type
// - Message (truncated)
// - Component
// - Timestamp
```

---

### `DevAgent.clear()`

Clear all errors and reset DevAgent state.

```javascript
DevAgent.clear();
// ✅ DevAgent cleared
```

---

### `DevAgent.show()`

Show the DevAgent UI overlay (bottom-right).

```javascript
DevAgent.show();
// 👁️ DevAgent UI shown
```

---

### `DevAgent.hide()`

Hide the DevAgent UI overlay.

```javascript
DevAgent.hide();
// 🙈 DevAgent UI hidden
```

---

### `DevAgent.health()`

Check if the DevAgent backend is connected and healthy.

```javascript
await DevAgent.health();
// Returns:
// { status: "healthy", backend: "connected" }
// or
// { status: "offline", error: Error }
```

---

### `DevAgent.help()`

Show the help message with all available commands.

```javascript
DevAgent.help();
```

---

## 🎯 Usage Examples

### Example 1: Analyze Console Errors

```javascript
// You see an error in console:
// TypeError: Cannot read property 'x' of undefined

// Ask DevAgent to analyze it:
DevAgent.analyze("Cannot read property 'x' of undefined", {
  file: "App.tsx",
  line: 42,
});

// Wait ~5 seconds, then check the fix:
DevAgent.showFix();
```

### Example 2: Batch Analysis

```javascript
// Analyze multiple errors
const errors = [
  "State is undefined",
  "Hook called outside component",
  "Cannot destructure property 'data'",
];

for (const err of errors) {
  DevAgent.analyze(err);
  await new Promise((r) => setTimeout(r, 6000)); // Wait for analysis
}

// View all errors
DevAgent.errors();
```

### Example 3: Health Monitoring

```javascript
// Check backend connection
const health = await DevAgent.health();
console.log("Backend status:", health.status);

if (health.status === "healthy") {
  DevAgent.analyze("My error message");
}
```

### Example 4: Debugging Workflow

```javascript
// 1. Clear previous errors
DevAgent.clear();

// 2. Trigger the problematic code
myBuggyFunction();

// 3. DevAgent auto-captures the error

// 4. Show the AI fix
DevAgent.showFix();

// 5. Apply the fix manually, then clear
DevAgent.clear();
```

---

## 🎨 Console Output Examples

### Success Case

```
🤖 DevAgent analyzing: Cannot read property 'subscribe' of null
📋 Current Fix: {
  issue_summary: "Null reference error when subscribing to store",
  root_cause: "Store not initialized before subscription",
  confidence: 95,
  fix_code: "if (store) { store.subscribe(...) }",
  ...
}
```

### Error Case

```
❌ DevAgent backend: OFFLINE
{ status: "offline", error: Error: Failed to fetch }
```

---

## 🔧 Integration Details

### Where It Works

- ✅ **Development mode only** (`import.meta.env.DEV`)
- ✅ Browser console (Chrome DevTools, Firefox DevTools, etc.)
- ✅ All pages where DevAgentMonitor is loaded
- ❌ Production builds (API not exposed)

### Backend Requirements

- Backend server must be running on `http://localhost:8000`
- Endpoints: `/api/dev/analyze-error`, `/api/context/summary`

---

## 🛡️ Safety Features

1. **Dev-only**: API only exists in development builds
2. **Auto-cleanup**: API removed when component unmounts
3. **Error boundaries**: Backend failures don't crash frontend
4. **Rate limiting**: Gemini API has built-in rate limits

---

## 🎭 Advanced Usage

### Intercept Console Errors Automatically

```javascript
// Override console.error to auto-analyze
const originalError = console.error;
console.error = function (...args) {
  originalError.apply(console, args);
  DevAgent.analyze(args.join(" "));
};
```

### Create Keyboard Shortcut

```javascript
// Press Ctrl+Shift+D to analyze last error
document.addEventListener("keydown", (e) => {
  if (e.ctrlKey && e.shiftKey && e.key === "D") {
    const lastError = DevAgent.errors()[0];
    if (lastError) {
      DevAgent.analyze(lastError.error_message);
    }
  }
});
```

### Export Errors to JSON

```javascript
// Save error history for later analysis
const errorLog = DevAgent.errors();
const blob = new Blob([JSON.stringify(errorLog, null, 2)], {
  type: "application/json",
});
const url = URL.createObjectURL(blob);
const a = document.createElement("a");
a.href = url;
a.download = "devagent-errors.json";
a.click();
```

---

## 📊 API Response Format

### FixSuggestion

```typescript
interface FixSuggestion {
  issue_summary: string; // One-line description
  root_cause: string; // Why it happened
  fix_code?: string; // Exact code to fix
  fix_steps: string[]; // Step-by-step instructions
  confidence: number; // 0-100
  prevention_tips: string[]; // How to avoid in future
  related_patterns: string[]; // Similar issues
  file_path?: string; // Affected file
  can_auto_apply?: boolean; // Safe for auto-fix?
}
```

### ErrorInfo

```typescript
interface ErrorInfo {
  error_type: string; // Error class name
  error_message: string; // Error text
  stack_trace?: string; // Full stack
  component?: string; // React component
  file_path?: string; // Source file
  line_number?: number; // Line number
  timestamp: string; // ISO 8601
  context?: Record<string, any>; // Additional data
}
```

---

## 🐛 Troubleshooting

### "DevAgent is not defined"

**Cause**: DevAgentMonitor component not mounted or production mode.  
**Fix**: Ensure you're in development mode and the app has loaded.

### "Failed to connect to DevAgent"

**Cause**: Backend server not running.  
**Fix**: Start backend with `PYTHONPATH=. python backend/server.py`

### "No fix available"

**Cause**: No error analyzed yet.  
**Fix**: Run `DevAgent.analyze("your error")` first.

---

## 🎓 Best Practices

1. **Clear between tests**: Use `DevAgent.clear()` to reset state
2. **Wait for analysis**: AI analysis takes ~5 seconds
3. **Check health first**: Run `DevAgent.health()` before analyzing
4. **Use context**: Provide file/line info for better fixes
5. **Review fixes**: Always review AI suggestions before applying

---

## 🚀 Performance

- **Console overhead**: ~0ms (lazy-loaded on first use)
- **Analysis time**: ~4-5 seconds (Gemini API call)
- **Memory impact**: ~2KB per error stored (max 10)
- **Backend load**: 1 API call per analysis

---

## 📝 Changelog

### v5.1.0 (February 2, 2026)

- ✅ Initial console API release
- ✅ 8 commands available
- ✅ Full TypeScript types
- ✅ Automatic error capture
- ✅ Health monitoring

---

## 🔗 Related Documentation

- [DEVAGENT_GUIDE.md](./DEVAGENT_GUIDE.md) - Complete guide
- [DEVAGENT_QUICKREF.md](./DEVAGENT_QUICKREF.md) - Quick reference
- [DIAGNOSTIC_REPORT.md](./DIAGNOSTIC_REPORT.md) - System status

---

**Made with ❤️ by Halilit ADK v5.1**  
**Powered by Google Gemini 2.0 Flash**
