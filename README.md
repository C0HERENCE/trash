# 和平精英精彩集锦下载脚本

这个脚本会把最近 24 小时内的和平精英对局中检测到的精彩时刻，自动在哔哩哔哩直播录像中裁剪成独立的 MP4 文件。整套流程只需准备一次环境，之后只要更新 cookie 并双击批处理即可。

## 1. 环境准备

1. **安装 Python 3.10+**  
   - 建议从 [python.org](https://www.python.org/downloads/windows/) 下载 “Windows installer (64-bit)” 安装包。  
   - 安装时务必勾选 “Add python.exe to PATH”。  
   - 安装完成后，按 `Win + R` 输入 `cmd`，在弹出的黑框中输入 `py --version`。看到版本号说明安装成功。  
   - 如果系统弹出 Microsoft Store，请重新运行安装包，或在“应用和功能”里卸载 `Python 3.x App Installer` 再重新安装。

2. **解压/放置脚本**  
   这个 README 所在的目录需要包含以下文件（默认已经准备好）：  
   - `main.py`、`auto_cut.py`、`bili_replay_min.py`、`g4p_battles.py` 和 `game_for_peace` 目录  
   - `bin/ffmpeg`（已在仓库中）  
   - `cookie.txt`（首次运行会自动生成占位内容）  
   - `requirements.txt`（列出依赖包）  
   - `run_highlight_downloader.bat`（批处理入口）  
   请把整个文件夹放在一个不含中文和空格的路径下（例如 `D:\g4p_highlights`），方便命令执行。

## 2. 获取并配置哔哩哔哩 Cookie

Cookie 用于访问你的直播录像，步骤（以 Chrome 为例）：

1. 在浏览器中访问 https://space.bilibili.com 并登录账号。  
2. 按 `F12` 打开开发者工具，切换到 `Console`（控制台）。  
3. 在输入栏中键入 `document.cookie` 并回车，控制台会输出整段 Cookie。  
4. 选中输出的 Cookie 文本并复制。  
5. 打开脚本目录下的 `cookie.txt`，把其中的 `PUT_YOUR_BILIBILI_COOKIE_HERE` 替换为刚刚复制的内容并保存。    
   - 只要账号 Cookie 失效（通常几天到一周），重复以上步骤替换即可。

## 3. 首次运行（启动本地 Web 服务）

1. 在资源管理器中双击 `run_highlight_downloader.bat`。  
2. 批处理会自动：  
   - 检查 `py` 或 `python` 命令。  
   - 如果还没有 `venv` 文件夹，自动创建虚拟环境。  
   - 进入虚拟环境后执行 `pip install -r requirements.txt`。  
   - 安装完毕后运行 `python main.py` 并启动一个本地 Web 服务（默认 http://127.0.0.1:8000）。命令行里出现 “Uvicorn running on ...” 就表示已经就绪。  
3. 打开浏览器访问 `http://127.0.0.1:8000`，页面只有一个“开始导出”按钮。  
4. 首次登录和平精英接口时，点按钮后会弹出 WeChat 扫码流程：  
   - 终端中会显示二维码。  
   - 用与游戏绑定的微信扫描二维码并确认登录。  
   - 登录信息会缓存到 `LoginInfo.txt`，下次运行无需再扫码。

> 终端窗口需保持开启，按 `Ctrl + C` 可停止服务。

## 4. 日常使用

1. 如果 Cookie 过期，只需更新 `cookie.txt` 后重新打开网页即可（无需重装环境）。  
2. 双击 `run_highlight_downloader.bat`（或在命令行运行 `python main.py`）以启动 Web 服务，然后访问 `http://127.0.0.1:8000`。  
3. 点击“开始导出”按钮，后台会自动：  
   - 拉取最近 24 小时的对局，定位每一局里的精彩击杀时间点。  
   - 获取最新的一场直播录像，并根据精彩时间裁剪片段。  
   - 在 `clips/<live_key>/` 目录下生成若干 `clip_开始时间_时长.mp4` 文件，并在页面上展示结果。  
4. 如果页面提示 “cookie.txt 未配置” 或 “未找到 cookie.txt”，说明需要重新粘贴 Cookie。  
5. 关闭窗口或按 `Ctrl + C` 可停止服务，随时可再次双击批处理重新启动。

## 5. 常见问题

- **`py` 或 `python` 仍然打开 Microsoft Store**：卸载系统自带的 “Python 3.x” App，然后重新安装官方版本。  
- **依赖安装失败**：确认网络可访问 PyPI，或提前下载离线包放到本目录后自行 `pip install`。  
- **输出 MP4 没有内容**：请确认直播录像里确实包含脚本识别到的时间段，必要时调整 `main.py` 里的 `recording_tab_modes` 或 `query_range`。  
- **登录过期**：删除 `LoginInfo.txt`，再次运行批处理重新扫码即可。

## 6. 手动运行（可选）

如果更喜欢命令行，效果与双击批处理一致：

```powershell
cd D:\g4p_highlights
py -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python main.py  # 会启动同样的 Web 服务
```

但对没有编程经验的朋友，仍推荐直接双击批处理并在浏览器里点击按钮即可。
## 7. Git 使用指南（仓库：https://github.com/C0HERENCE/trash）

面向初次接触 Git 的朋友，可以按照下面的流程协作和备份代码。示例仍以 Windows PowerShell 为准。

1. **首次克隆仓库**
   ```powershell
   cd D:\Projects
   git clone https://github.com/C0HERENCE/trash.git
   cd trash
   ```
   之后所有操作都在 `trash` 目录中完成。

2. **每日开始前先同步远端**
   ```powershell
   git pull
   ```
   确保本地代码与 GitHub 保持一致，避免提交冲突。

3. **查看本地改动**
   ```powershell
   git status
   git diff
   ```
   `git status` 会列出被修改/新增的文件；`git diff` 可查看具体内容。

4. **提交自己的修改**
   ```powershell
   git add README.md web/index.html  # 根据实际修改的文件替换
   git commit -m "feat: 支持多录像勾选导出"
   ```
   建议一次提交只包含一组相关变更，并写清楚说明。被 `.gitignore` 排除的文件（如 `cookie.txt`、`clips/` 等敏感或体积较大的内容）不会被提交。

5. **推送到 GitHub**
   ```powershell
   git push origin main
   ```
   首次推送需要登录 GitHub，出现浏览器弹窗时按提示授权即可。

6. **新增文件或本地分支**
   - 添加新文件同样需要 `git add <文件>`。
   - 如果想在独立分支上开发，可 `git checkout -b feature/ui`，完成后用 `git push origin feature/ui` 推送，并在 GitHub 上发起 Pull Request。

7. **常见问题**
   - *推送被拒绝*：说明远端有更新，先 `git pull --rebase` 再重新 `git push`。
   - *忘记跟踪新文件*：`git status` 显示 `Untracked files` 时别忘了 `git add`。
   - *误提交敏感文件*：立即 `git rm --cached <文件>` 并重新提交；同时确认 `.gitignore` 已包含该文件。

按照以上步骤即可把本项目安全地维护在 GitHub 上，并与好友同步最新功能。
