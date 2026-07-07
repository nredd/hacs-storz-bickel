#!/bin/bash
# Shared helpers for the card/* scripts (Bun toolchain).
# Source this file after output.sh: source "$SCRIPT_DIR/.lib/card.sh"

# Fail fast with an installation hint when Bun is unavailable.
require_bun() {
    if ! command -v bun >/dev/null 2>&1; then
        log_error "bun is required for card tooling but was not found"
        log_info "Install it: https://bun.sh (or: brew install oven-sh/bun/bun)"
        exit 1
    fi
}

# Install the card's dependencies from the committed lockfile (no-op when fresh).
card_install() {
    (cd card && bun install --frozen-lockfile)
}
