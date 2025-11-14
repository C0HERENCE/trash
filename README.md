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
   - `run_highlight_downloader.bat`（稍后创建）  
   请把整个文件夹放在一个不含中文和空格的路径下（例如 `D:\g4p_highlights`），方便命令执行。

## 2. 获取并配置哔哩哔哩 Cookie

Cookie 用于访问你的直播录像，步骤（以 Chrome 为例）：

1. 打开浏览器，登录哔哩哔哩账号。  
2. 进入任意网页，按 `F12` 打开开发者工具。  
3. 点击 `Network`，勾选 `Preserve log` 并刷新页面。  
4. 在请求列表中随便点一个（例如 `space.bilibili.com`），在右侧 `Headers` → `Request Headers` 找到 `cookie`。  
5. 双击 `cookie` 后面的整段内容，复制到剪贴板。  
6. 在脚本文件夹里找到 `cookie.txt`，用记事本打开，把里面的 `PUT_YOUR_BILIBILI_COOKIE_HERE` 替换成刚才复制的整段 Cookie，然后保存。  
   - 只要账号 Cookie 失效（通常几天到一周），重复以上步骤替换即可。

## 3. 首次运行（自动创建虚拟环境）

1. 在资源管理器中双击 `run_highlight_downloader.bat`。  
2. 批处理会自动执行以下动作：  
   - 检查 `py` 或 `python` 命令。  
   - 如果还没有 `venv` 文件夹，自动创建虚拟环境。  
   - 进入虚拟环境后执行 `pip install -r requirements.txt`。  
3. 首次登录和平精英接口时，会弹出一个 WeChat 扫码流程：  
   - 终端中会显示二维码，也会在脚本目录生成 `qrq.png`。  
   - 用与游戏绑定的微信扫描二维码并确认登录。  
   - 登录信息会缓存到 `LoginInfo.txt`，下次运行无需再扫码。

## 4. 日常使用

1. 每次准备好新的哔哩哔哩 Cookie 后，直接双击 `run_highlight_downloader.bat`。  
2. 程序会自动：  
   - 拉取最近 24 小时的对局，定位每一局里的精彩击杀时间点。  
   - 获取最新的一场直播录像，并根据精彩时间裁剪片段。  
   - 在当前目录下输出若干 `clip_开始时间_时长.mp4` 文件。  
3. 如果执行过程中看到 “cookie.txt 未配置” 或 “未找到 cookie.txt”，说明需要重新粘贴 Cookie。  
4. 若批处理中断，可再次双击继续运行；虚拟环境和依赖只会在缺失时才会重新安装。

## 5. 常见问题

- **`py` 或 `python` 仍然打开 Microsoft Store**：卸载系统自带的 “Python 3.x” App，然后重新安装官方版本。  
- **依赖安装失败**：确认网络可访问 PyPI，或提前下载离线包放到本目录后自行 `pip install`。  
- **输出 MP4 没有内容**：请确认直播录像里确实包含脚本识别到的时间段，必要时调整 `main.py` 里的 `recording_tab_modes` 或 `query_range`。  
- **登录过期**：删除 `LoginInfo.txt`，再次运行批处理重新扫码即可。

## 6. 手动运行（可选）

如果更喜欢命令行：

```powershell
cd D:\g4p_highlights
py -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

但对没有编程经验的朋友，仍推荐直接双击批处理。
