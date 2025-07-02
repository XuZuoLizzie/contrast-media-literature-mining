# Gemini 批量PDF信息抽取脚本说明

本项目提供了一个 Python 脚本，用于批量调用 Google Gemini API，对指定文件夹下的 PDF 文件进行信息抽取，并将结果保存为 JSON 文件。

## 如何获取 Gemini API Key

1. 访问 [Google AI Studio](https://aistudio.google.com/app/apikey)；
2. 登录你的 Google 账号，创建 Gemini API 项目；
3. 在 API 密钥管理页面生成新的 API Key；
4. 复制该 Key，后续将写入 `.env` 文件。

## 在 GitHub Codespace + VS Code 中运行脚本

1. 在 GitHub 上 Clone 本仓库，并在 Codespace 中打开（需要先在VS Code中安装GitHub Codespaces插件）。
2. 在 Codespace 终端中，依次执行以下命令：
   - 创建并激活 Python 虚拟环境：
     ```bash
     conda create -n constrast-media python=3.10 -y
     conda activate constrast-media
     ```
   - 安装依赖：
     ```bash
     pip install -q -U google-genai dotenv
     ```
   - 配置 `.env` 文件，写入你的 Gemini API Key：
     ```bash
     echo 'GOOGLE_API_KEY=your_google_api_key_here' > .env
     ```
   - 将待处理的 PDF 文件上传到 `pdf-data/` 文件夹（可在 VS Code 文件树中拖拽上传）。
   - 确认 `prompts/IE-sample-prompt.md` 存在并已根据需求编辑。
   - 运行脚本：
     ```bash
     python gemini-extract.py
     ```
3. 处理完成后，结果 JSON 文件和错误日志文件会保存在 `output-json/` 目录。

## 文件结构说明

- `gemini-extract.py`：主脚本，批量处理 PDF 文件。
- `pdf-data/`：存放待处理的 PDF 文件。
- `output-json/`：脚本运行后，生成的 JSON 结果文件将保存在此目录。
- `prompts/IE-sample-prompt.md`：系统提示词（Prompt）文件。

## 注意事项

- 每次 API 调用后会自动延迟（默认20秒），以避免触发速率限制。
- 若遇到 API 错误或解析失败，相关错误信息会以 `_error.json` 文件形式保存。
- 请确保 `.env` 文件中的 API Key 正确无误。

## 常见问题

- **API Key 未配置或无效**：请检查 `.env` 文件内容。
- **PDF 文件未被处理**：请确认文件扩展名为 `.pdf` 且放在 `pdf-data/` 目录下。


