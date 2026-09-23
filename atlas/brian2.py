# Lightweight stub to prevent importing the heavy 'brian2' package during tests.
# We intentionally raise ImportError so code paths that check for availability
# treat brian2 as unavailable instead of importing the real package.
raise ImportError("brian2 is not available in test environment (stub)")
