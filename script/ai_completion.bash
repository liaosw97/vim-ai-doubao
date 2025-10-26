#!/bin/bash
# 检查当前 shell 是否为 Zsh，如果是则初始化 bashcompinit
if [[ -n "${ZSH_VERSION}" ]]; then
    autoload -U +X bashcompinit && bashcompinit
fi

# 解析 ini 文件，返回所有 section 名称，添加 '/' 前缀
parse_ini_sections() {
    local ini_file="$1"
    if [[ -f "$ini_file" ]]; then
        # 使用 grep 提取所有 section 名称，移除左括号并替换为 '/'，移除右括号，添加 '/' 前缀
        grep '^\[.*\]' "$ini_file" | sed 's/^\[//; s/\].*$//' | sed 's/^/\//'
    else
        echo 'wrong'
    fi
}

# 补全函数
_ai() {
    local cur prev ini_file sections
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD - 1]}"
    # 请将此处修改为你实际的 ini 文件路径
    ini_file="${HOME}/.vim/plugged/vim-ai-doubao/roles-example.ini"
    sections=$(parse_ini_sections "$ini_file")

    COMPREPLY=( $(compgen -W "$sections" -- "$cur") )
    return 0
}

# 关联补全函数和命令，这里假设命令名为 ai
complete -F _ai ai
