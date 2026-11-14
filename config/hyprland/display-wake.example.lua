-- Preserve the installed recovery binding. Example only; review key conflicts.
o.bind("SUPER + ALT + W", "Wake displays", [[hyprctl dispatch 'hl.dsp.dpms({ action = "enable" })']], { locked = true })
