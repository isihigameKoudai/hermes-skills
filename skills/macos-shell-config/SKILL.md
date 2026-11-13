---
name: macos-shell-config
description: Use when migrating or configuring the macOS login shell.
---

# macOS Shell Config

## When to Use

- User asks to change, migrate, or configure the macOS login shell (fish↔zsh↔bash).
- User wants to install or fully uninstall a shell, or replicate one shell's conveniences in another.

User's Mac: Apple Silicon, Homebrew at `/opt/homebrew`. Default shell is zsh (migrated from fish; fish fully uninstalled). Give shell commands in zsh form — heredoc `<<'EOF'` works, `VAR=x cmd` works directly, no `env VAR=x cmd` needed.

## Changing the default shell

```
chsh -s /bin/zsh              # macOS built-in
chsh -s /opt/homebrew/bin/zsh # Homebrew build
```

**Pitfall — `chsh` does not touch the running terminal.** `$SHELL` is set at login, so the current session keeps the old shell until the terminal app is quit (⌘Q) and relaunched. Verify in a fresh terminal: `echo $SHELL`. Visual cue: zsh prompt is `%`, fish is `~>`.

## fish → zsh syntax translation

| fish | zsh |
|---|---|
| `set -gx VAR val` | `export VAR="val"` |
| `env VAR=val cmd` | `VAR=val cmd` |
| `alias ll 'ls -lh'` | `alias ll='ls -lh'` |
| `abbr -a g git` | zsh-abbr plugin, or plain `alias` |
| `function foo ... end` | `foo() { ... }` |
| `fish_add_path /x` | `export PATH="/x:$PATH"` |
| `(cmd)` | `$(cmd)` |
| heredoc `<<'EOF'` | unsupported in fish, supported in zsh |

## Replicating fish conveniences in zsh

fish users miss autosuggestion (grey inline candidates) and syntax highlighting. Reproduce with Oh My Zsh + two plugins:

```
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
git clone https://github.com/zsh-users/zsh-syntax-highlighting ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
sed -i '' 's/^plugins=(git)$/plugins=(git zsh-autosuggestions zsh-syntax-highlighting)/' ~/.zshrc
source ~/.zshrc
```

## Uninstalling a shell completely (fish example)

Order is critical — change the default shell FIRST, or the removed binary leaves no login shell.

1. `chsh -s /bin/zsh` and confirm in a fresh terminal (`echo $SHELL` → `/bin/zsh`).
2. Uninstall the binary. Homebrew install → `brew uninstall fish`. Official pkg → `sudo pkgutil --forget com.fishshell.fish` + `rm` the binaries.
3. Remove the shell from `/etc/shells`: `sudo sed -i '' '/fish/d' /etc/shells`.
4. Delete config/data/cache: `rm -rf ~/.config/fish ~/.local/share/fish ~/.cache/fish`.
5. Verify: `which fish` → `command not found`, `echo $SHELL` → `/bin/zsh`.

## Pitfalls

- **Change the default shell before removing a shell** — `chsh` away from it first, or you lock yourself out with no login shell.
- **A shell migration deletes the source config by default** — dump or back up `~/.config/fish/` (aliases, abbrs, env vars, `fish_variables`) BEFORE uninstalling, or the aliases to translate are gone.
- **Homebrew's PATH entry lives in the shell's own config** — the brew installer writes `eval "$(/opt/homebrew/bin/brew shellenv)"` into the active shell's rc file. Deleting that shell's config (e.g. `~/.config/fish`) silently drops `brew` from PATH in the new shell. After migration, check `which brew` and re-add `eval "$(/opt/homebrew/bin/brew shellenv)"` to `~/.zprofile` if missing.
- **`which <shell>` tells you the uninstall path** — Homebrew installs to `/opt/homebrew/bin/` on Apple Silicon; the official pkg installs to `/usr/local/bin/`. Detect the install method (`brew list --formula | grep fish`, `pkgutil --pkgs | grep fish`) before choosing `brew uninstall` vs `rm`.
- **macOS `sed` is BSD sed** — in-place edit needs the empty `''` argument: `sed -i '' 's/.../.../'`, not GNU `sed -i`.
