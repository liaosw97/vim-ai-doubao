# vim-ai

## 插件介绍

这个插件是 [vim-ai](https://github.com/madox2/vim-ai/wiki) 的中文大模型版,提供了额外的3种中文大语言的支持(目前),使得无需网络就可以实现在vim中的人工智能,以及完善了一些细节和体验

这个插件为你的 Vim 和 Neovim 添加了人工智能 (AI) 功能。

你可以使用 豆包,通义千问,讯飞星火,智谱,百川,kimi,OpenAI 的 API 生成代码、编辑文本或与 GPT 模型进行交互对话。

甚至只要是兼容openai api 的大模型都可以无缝接入

## 功能

- 使用 AI 生成文本或代码，回答问题
- 使用 AI 就地编辑选定的文本
- 提供直接在终端中运行命令的功能
- 与 ChatGPT 进行交互式对话
- 支持自定义角色等

### 工作原理

这个插件使用 兼容OpenAI 的 API 来生成回复。

你需要自己去获取这个api 的 token

请注意，该插件不会在后台发送任何代码。你只需要共享和支付你特别选择的内容，例如提示和聊天内容。

- 豆包: 参考 [https://www.volcengine.com/docs/82379/1222542](https://www.volcengine.com/docs/82379/1222542)
- openai: 参考 [https://platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys)
- 通问千义:  参考 [https://help.aliyun.com/zh/dashscope/developer-reference/use-qwen-by-api](https://help.aliyun.com/zh/dashscope/developer-reference/use-qwen-by-api)
- 迅飞星火: 参考 [https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html](https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html)
- 智谱: 参考 [https://open.bigmodel.cn/dev/api#http_call](https://open.bigmodel.cn/dev/api#http_call)
- 百川: 参考 [https://platform.baichuan-ai.com/docs/api#](https://platform.baichuan-ai.com/docs/api#)

### 安装

#### 前提条件

- 支持 python3 的 Vim 或 Neovim
- 获取 token 和 model(就是你需要调用的模型)

默认的 API 密钥文件位置是 `~/.config/vim-ai-token.json`，但你可以通过在 `.vimrc` 文件中设置 `g:vim_ai_config_file_path` 来更改它：

```vim
let g:vim_ai_config_file_path = '~/.config/vim-ai-token.json'
```

#### 使用 `vim-plug`

```vim
Plug 'chenxuan520/vim-ai-doubao'
```

#### 手动安装

使用内置的 Vim 包 `:help packages`

```sh
# vim
mkdir -p ~/.vim/pack/plugins/start
git clone https://github.com/chenxuan520/vim-ai-doubao.git ~/.vim/pack/plugins/start/vim-ai-doubao

# neovim
mkdir -p ~/.local/share/nvim/site/pack/plugins/start
git clone https://github.com/chenxuan520/vim-ai-doubao.git ~/.local/share/nvim/site/pack/plugins/start/vim-ai-doubao
```

### 配置


- 使用 `:AiConfigEdit` 打开配置文件,这是一个json文件,将你调用模型的 token 和 model 放到相应位置就完成配置了
- 默认使用豆包大模型补全,如果使用其他大模型添加配置

```vim
let g:vim_ai_name="xinhuo" " xinhuo ,doubao ,tongyi ,openai
```

### 用法

要使用 AI 命令，请在命令后输入指令提示。您还可以将其与视觉选择结合使用。以下是可用命令的简要概述：

```
========= Basic AI commands =========

:AI         complete text
:AIEdit     edit text
:AIChat     continue or open new chat

============= Utilities =============

:AIRedo     repeat last AI command
:AINewChat  open new chat

:help vim-ai
```

**提示：** 随时按 `Ctrl-c` 可取消补全。

**提示：** 设置自己的 [键绑定](#key-bindings) 或使用命令快捷键 - `:AIE`, `:AIC`, `:AIR`。

**提示：** 可以通过初始参数 `/{role}` 将 [自定义角色](#roles) {role} 传递给上述命令，例如 `:AIEdit /grammar`。

**提示：** 可以使用范围 `:help range` 组合命令，例如选择整个缓冲区 - `:%AIE fix grammar`。

如果您对更多提示感兴趣，或者想使用更多命令（如 `:GitCommitMessage`）来提升您的 Vim 水平 - 例如建议一个 Git 提交消息，请访问 [社区维基](https://github.com/madox2/vim-ai/wiki)。

## 参考

在下面的文档中，`<selection>`表示视觉选择或任何其他范围，`{instruction}`表示指令提示，`{role}`表示[自定义角色](#roles)，`?`符号表示可选参数。

### `:AI`

`:AI` - 完成当前行上的文本。

`:AI {prompt}` - 完成提示。

`<selection> :AI` - 完成选择。

`<selection> :AI {instruction}` - 使用指令完成选择。

`<selection>? :AI /{role} {instruction}?` - 使用角色完成

### `:AIEdit`

`<selection>? :AIEdit` - 编辑当前行或选择

`<selection>? :AIEdit {instruction}` - 使用指令编辑当前行或选择

`<selection>? :AIEdit /{role} {instruction}?` - 使用角色编辑

### `:AIChat`

`:AIChat` - 继续或开始新的对话。

`<selection>? :AIChat {instruction}?` - 根据选择、指令或两者开始新的对话

`<selection>? :AIChat /{role} {instruction}?` - 使用角色完成对话

当AI完成回答后，你可以通过进入插入模式，添加你的提示符，然后再次使用命令`:AIChat`来继续对话。

#### `.aichat`文件

你可以编辑并保存聊天对话到一个`.aichat`文件中，并在以后恢复它。
这允许你创建可重用的自定义提示符，例如：

```
# ./refactoring-prompt.aichat

>>> system

You are a Clean Code expert, I have the following code, please refactor it in a more clean and concise way so that my colleagues can maintain the code more easily. Also, explain why you want to refactor the code so that I can add the explanation to the Pull Request.

>>> user

[attach code]

```

要在聊天中包含文件，可以使用特殊的` include `角色：

```
>>> user

Generate documentation for the following files

>>> include

/home/user/myproject/requirements.txt
/home/user/myproject/**/*.py
```

每个文件的内容将被添加到一个额外的`user`角色消息中，文件之间用`==> {路径} <==`分隔，其中路径是文件的路径。通配符通过`glob.gob`展开，相对于当前工作目录（由`getcwd()`确定）的相对路径将被解析为绝对路径。

支持的聊天角色是 **`>>> system`**、**`>>> user`**、**`>>> include`** 和 **`<<< assistant`**。

### `:AINewChat`

`:AINewChat {preset shortname}?` - 开始一段新的对话

这个命令用于在特定情况下以特定方式生成一个新的聊天，或者在`:AIChat`通常会继续对话的情况下。

作为参数，你可以放入一个打开聊天的命令预设快捷方式 - `below`（下方）、`tab`（标签页）或`right`（右侧）。例如：`:AINewChat right`。

### `:AIRedo`

`:AIRedo` - 重复上一个AI命令

在`AI`/`AIEdit`/`AIChat`命令之后立即使用此命令，以便重新尝试或获取替代完成。
请注意，响应的随机性在很大程度上取决于[`temperature`](https://platform.openai.com/docs/api-reference/completions/create#completions/create-temperature)参数。

## 角色配置

在这个插件的上下文中，角色意味着一个可重用的AI指令和/或配置。角色在配置文件`.ini`文件中定义。例如，通过定义一个`grammar`角色:

```vim
let g:vim_ai_roles_config_file = '/path/to/my/roles.ini'
```

```ini
# /path/to/my/roles.ini

[grammar]
prompt = fix spelling and grammar

[grammar.options]
temperature = 0.4
```

现在您可以选择文本并使用命令`:AIEdit /grammar`运行它。

有关更多示例，请参阅[roles-example.ini](./roles-example.ini)。

## 按键绑定

这个插件没有设置任何快捷键绑定。你可以在`.vimrc`文件中创建自己的绑定来触发AI命令，例如：

```vim
" complete text on the current line or in visual selection
nnoremap <leader>a :AI<CR>
xnoremap <leader>a :AI<CR>

" edit text with a custom prompt
xnoremap <leader>s :AIEdit fix grammar and spelling<CR>
nnoremap <leader>s :AIEdit fix grammar and spelling<CR>

" trigger chat
xnoremap <leader>c :AIChat<CR>
nnoremap <leader>c :AIChat<CR>

" redo last AI command
nnoremap <leader>r :AIRedo<CR>
```

## 重要免责声明

**准确性**：GPT擅长生成乍一看正确的文本和代码，但可能完全错误。请务必仔细审查、阅读和测试此插件生成的所有输出！

**隐私**：此插件在生成补全和编辑时会向OpenAI发送文本。因此，不要在包含敏感信息的文件中使用它。

## 许可证

[MIT许可证](https://github.com/chenxuan520/vim-ai-doubao/blob/main/LICENSE)
