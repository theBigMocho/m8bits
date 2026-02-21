
import os
import json
import shutil
import re
from datetime import datetime, timedelta, timezone

def create_chat_viewer():
    # Define paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    source_images_path = os.path.join(script_dir, "images")
    images_index_path = os.path.join(script_dir, "data", ".images_index.json")
    dest_images_path = os.path.join(script_dir, "chat_viewer", "images")

    # Create necessary directories
    os.makedirs(dest_images_path, exist_ok=True)

    # Copy images from source directory if it exists
    if os.path.exists(source_images_path):
        shutil.copytree(source_images_path, dest_images_path, dirs_exist_ok=True)

    # Load image index and parse timestamp from JSON
    images_by_time = {}
    if os.path.exists(images_index_path):
        with open(images_index_path, "r", encoding="utf-8") as f:
            try:
                images_data = json.load(f)
                for img in images_data.get("images", []):
                    filename = img.get("filename", "")
                    timestamp_str = img.get("timestamp", "")
                    if timestamp_str:
                        try:
                            # Parse ISO 8601 timestamp (UTC)
                            dt_utc = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                            # Convert to local time
                            dt_local = dt_utc.astimezone().replace(tzinfo=None)
                            images_by_time[dt_local] = filename
                        except (ValueError, AttributeError):
                            pass
            except json.JSONDecodeError:
                pass

    # Use a list to build HTML parts
    html_parts = ["""
<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat Viewer</title>
    <link id="hljs-theme" rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css">
    <style>
        :root {
            --bg-page: #f0f2f5;
            --bg-container: #ffffff;
            --bg-user-msg: #e7f3ff;
            --bg-assistant-msg: #f0f0f0;
            --bg-pre: #f6f8fa;
            --bg-code: rgba(175,184,193,0.2);
            --border-container: #dddfe2;
            --border-img: #ddd;
            --border-blockquote: #ddd;
            --color-text: #1c1e21;
            --color-divider: #65676b;
            --color-blockquote: #666;
            --color-user-role: #007bff;
            --color-assistant-role: #28a745;
        }
        [data-theme="dark"] {
            --bg-page: #18191a;
            --bg-container: #242526;
            --bg-user-msg: #0a3d6b;
            --bg-assistant-msg: #3a3b3c;
            --bg-pre: #1e1e1e;
            --bg-code: rgba(255,255,255,0.1);
            --border-container: #3a3b3c;
            --border-img: #555;
            --border-blockquote: #555;
            --color-text: #e4e6eb;
            --color-divider: #b0b3b8;
            --color-blockquote: #aaa;
            --color-user-role: #4da3ff;
            --color-assistant-role: #4caf70;
        }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; margin: 0; padding: 20px; background-color: var(--bg-page); color: var(--color-text); transition: background-color 0.2s, color 0.2s; }
        .chat-container { margin: auto; background-color: var(--bg-container); border: 1px solid var(--border-container); padding: 20px; border-radius: 8px; transition: background-color 0.2s, border-color 0.2s; }
        .message { margin-bottom: 20px; display: flex; }
        .role { font-weight: bold; margin-bottom: 5px; }
        .user { justify-content: flex-end; }
        .user .role { color: var(--color-user-role); }
        .assistant .role { color: var(--color-assistant-role); }
        .message-content { padding: 12px; border-radius: 18px; line-height: 1.4; max-width: 75%; transition: background-color 0.2s; }
        .user .message-content { background-color: var(--bg-user-msg); }
        .assistant .message-content { background-color: var(--bg-assistant-msg); }
        .message-text { white-space: pre-wrap; word-wrap: break-word; }
        .message-text h1, .message-text h2, .message-text h3 { margin-top: 1em; margin-bottom: 0.5em; }
        .message-text h1 { font-size: 1.5em; }
        .message-text h2 { font-size: 1.3em; }
        .message-text h3 { font-size: 1.1em; }
        .message-text ul, .message-text ol { margin: 0.5em 0; padding-left: 1.5em; }
        .message-text pre { background-color: var(--bg-pre); border-radius: 6px; padding: 16px; overflow-x: auto; margin: 1em 0; }
        .message-text code { background-color: var(--bg-code); padding: 0.2em 0.4em; border-radius: 3px; font-size: 0.9em; }
        .message-text pre code { background-color: transparent; padding: 0; }
        .message-text p { margin: 0.5em 0; }
        .message-text blockquote { border-left: 4px solid var(--border-blockquote); margin: 1em 0; padding-left: 1em; color: var(--color-blockquote); }
        .images-container { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px; }
        .images-container img { max-width: 250px; display: block; border-radius: 15px; border: 1px solid var(--border-img); cursor: pointer; }
        .session-divider { text-align: center; color: var(--color-divider); margin: 40px 15px 20px; font-weight: bold; font-size: 0.9em; }
        .lightbox { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); z-index: 1000; justify-content: center; align-items: center; }
        .lightbox.active { display: flex; }
        .lightbox img { max-width: 90vw; max-height: 90vh; object-fit: contain; border-radius: 8px; border: none; cursor: zoom-out; }
        .theme-toggle { position: fixed; top: 16px; right: 16px; z-index: 999; background: var(--bg-container); border: 1px solid var(--border-container); color: var(--color-text); padding: 6px 14px; border-radius: 20px; cursor: pointer; font-size: 0.85em; font-family: inherit; transition: background-color 0.2s, color 0.2s, border-color 0.2s; }
        .theme-toggle:hover { opacity: 0.75; }
    </style>
</head>
<body>
    <button class="theme-toggle" id="theme-toggle">Dark</button>
    <div id="lightbox" class="lightbox">
        <img id="lightbox-img" src="" alt="">
    </div>
    <div class="chat-container">
"""]

    log_file = os.path.join(script_dir, "logs", "prompt-chat-history.log")
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            content = f.read()

        sessions = re.split(r'================================================================================\n\[(.*?)\] \[Session: (.*?)\]\n================================================================================', content)
        
        for i in range(1, len(sessions), 3):
            timestamp_str, session_id, session_content = sessions[i].strip(), sessions[i+1].strip(), sessions[i+2]
            
            try:
                session_dt_local = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                continue

            html_parts.append(f'<div class="session-divider">Session: {session_id} &mdash; {session_dt_local.strftime("%B %d, %Y, %I:%M %p")} (Local)</div>')

            session_images_html = ""
            session_window_start = session_dt_local - timedelta(seconds=30)
            session_window_end = session_dt_local + timedelta(seconds=30)
            
            found_images_keys = []
            for img_dt, img_filename in images_by_time.items():
                if session_window_start <= img_dt < session_window_end:
                    session_images_html += f'<img src="images/{img_filename}" alt="{img_filename}">'
                    found_images_keys.append(img_dt)
            
            for key in found_images_keys:
                del images_by_time[key]
            
            if session_images_html:
                session_images_html = f'<div class="images-container">{session_images_html}</div>'

            # Split by role markers (USER: or ASSISTANT:)
            # First split captures initial USER message and subsequent messages
            parts = re.split(r'\n*(USER|ASSISTANT):\n', session_content.strip())

            # Remove empty first element if exists
            if parts and not parts[0].strip():
                parts = parts[1:]

            first_user_message_processed = False
            i = 0
            while i < len(parts) - 1:
                role = parts[i].lower()
                message_text = parts[i+1].strip()

                # Remove trailing separator if present
                message_text = re.sub(r'\n-+\s*$', '', message_text)

                image_html_to_inject = ""
                if role == "user" and not first_user_message_processed:
                    image_html_to_inject = session_images_html
                    first_user_message_processed = True

                # For user messages, escape HTML. For assistant, keep for markdown processing
                if role == "user":
                    message_text_safe = message_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                    html_parts.append(f"""
        <div class="message {role}">
            <div class="message-content">
                <div class="role">{role.capitalize()}</div>
                <div class="message-text">{message_text_safe}</div>
                {image_html_to_inject}
            </div>
        </div>
""")
                else:
                    # For assistant messages, use a data attribute for markdown processing
                    message_text_escaped = message_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
                    html_parts.append(f"""
        <div class="message {role}">
            <div class="message-content">
                <div class="role">{role.capitalize()}</div>
                <div class="message-text markdown-content" data-markdown="{message_text_escaped}"></div>
                {image_html_to_inject}
            </div>
        </div>
""")
                i += 2

    html_parts.append("""
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/marked/11.1.1/marked.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <script>
        // Configure marked with highlight.js
        marked.setOptions({
            highlight: function(code, lang) {
                if (lang && hljs.getLanguage(lang)) {
                    try {
                        return hljs.highlight(code, { language: lang }).value;
                    } catch (err) {}
                }
                return hljs.highlightAuto(code).value;
            },
            breaks: true,
            gfm: true
        });

        // Dark/light mode
        (function() {
            var html = document.documentElement;
            var toggle = document.getElementById('theme-toggle');
            var hljsTheme = document.getElementById('hljs-theme');

            function applyTheme(theme) {
                html.setAttribute('data-theme', theme);
                toggle.textContent = theme === 'dark' ? 'Light' : 'Dark';
                hljsTheme.href = theme === 'dark'
                    ? 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css'
                    : 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css';
                localStorage.setItem('chat-viewer-theme', theme);
            }

            applyTheme(localStorage.getItem('chat-viewer-theme') || 'dark');

            toggle.addEventListener('click', function() {
                applyTheme(html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
            });
        })();

        // Process all markdown content
        document.addEventListener('DOMContentLoaded', function() {
            document.querySelectorAll('.markdown-content').forEach(function(element) {
                var markdownText = element.getAttribute('data-markdown');
                if (markdownText) {
                    // Unescape HTML entities
                    var textarea = document.createElement('textarea');
                    textarea.innerHTML = markdownText;
                    var decodedText = textarea.value;

                    // Render markdown
                    element.innerHTML = marked.parse(decodedText);
                }
            });

            // Lightbox
            var lightbox = document.getElementById('lightbox');
            var lightboxImg = document.getElementById('lightbox-img');

            document.querySelectorAll('.images-container img').forEach(function(img) {
                img.addEventListener('click', function() {
                    lightboxImg.src = this.src;
                    lightboxImg.alt = this.alt;
                    lightbox.classList.add('active');
                });
            });

            lightbox.addEventListener('click', function(e) {
                if (e.target !== lightboxImg) {
                    lightbox.classList.remove('active');
                }
            });

            lightboxImg.addEventListener('click', function() {
                lightbox.classList.remove('active');
            });

            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape') lightbox.classList.remove('active');
            });
        });
    </script>
</body>
</html>
""")

    output_html = os.path.join(script_dir, "chat_viewer", "chat.html")
    with open(output_html, "w", encoding="utf-8") as f:
        f.write("".join(html_parts))

    print("Chat viewer HTML has been successfully generated.")

if __name__ == "__main__":
    create_chat_viewer()
