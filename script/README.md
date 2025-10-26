# Completion Scripts for vim-ai-doubao

This directory contains shell completion scripts for the `ai` command that works with vim-ai-doubao.

## Zsh Completion

The `_ai_completion` file is a zsh completion script for the `ai` command. To use it:

1. Place the `_ai_completion` file in your zsh completion directory. Common locations include:
   - `~/.zsh/completion/`
   - `~/.local/share/zsh/site-functions/`
   - `/usr/local/share/zsh/site-functions/` (system-wide)
   - `~/.oh-my-zsh/completions/` (if using oh-my-zsh)

2. Make sure the directory is in your zsh fpath by adding this to your `~/.zshrc`:
   ```
   fpath=(~/.zsh/completion $fpath)
   ```

3. Reload your shell:
   ```
   exec zsh
   ```

After these steps, you should get auto-completion when typing `ai` followed by a tab, using the section names from your roles-example.ini file.

## Bash Completion

The `ai_completion.bash` file is a bash completion script for the `ai` command. To use it:

1. Source the script in your `~/.bashrc` or `~/.bash_profile`:
   ```
   source /path/to/vim-ai-doubao/script/ai_completion.bash
   ```

2. Reload your shell:
   ```
   source ~/.bashrc
   ```
   or
   ```
   exec bash
   ```
 Or just copy/ln to `~/.bash_completion` file is ok `ln -s $PWD/ai_completion.bash ~/.bash_completion`

After these steps, you should get auto-completion when typing `ai` followed by a tab, using the section names from your roles-example.ini file.

Note that these scripts assume there's an `ai` command that accepts the section names as arguments. The completion will provide the section names defined in:
`${HOME}/.vim/plugged/vim-ai-doubao/roles-example.ini`
