-- Example only: merge reviewed rules into your existing configuration.
-- Connector names vary by physical port. Do not copy without identifying them.
hl.monitor({ output = "eDP-1", mode = "preferred", position = "0x0", scale = 2 })
hl.monitor({ output = "DP-3", mode = "3840x1080@60", position = "1512x0", scale = 1, disabled = false })
-- Preserve existing Omarchy lid/clamshell handlers; do not add suspend here.
