#!/bin/bash
# Stop all AgentX services (shortcut for restart.sh --stop-only)
exec "$(dirname "$0")/restart.sh" --stop-only
