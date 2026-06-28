from flask import Flask, render_template,request
from emojis import emojis
import re
from waitress import serve

# code is shit i know but it works?
# note: i have taken some help from some llm for the advanced regex

app = Flask(__name__)

def listparse(text):
    lines = text.split("\n")
    out = []
    i = 0

    while i < len(lines):
        # unordered list (- - - etc.)
        if lines[i].startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(lines[i][2:].lstrip())
                i += 1
            out.append("<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>")
            continue
        # ordered list (1. 2. 3. etc.)
        if re.match(r"^\d+\. ", lines[i]):
            items = []
            while i < len(lines) and re.match(r"^\d+\. ", lines[i]):
                items.append(re.sub(r"^\d+\. ", "", lines[i]))
                i += 1
            out.append("<ol>" + "".join(f"<li>{x}</li>" for x in items) + "</ol>")
            continue

        out.append(lines[i])
        i += 1
    
    return "\n".join(out)

def parse(text):
    codeblocks = []
    def code(match):
        codeblocks.append(f'<code>{match.group(1).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")}</code>')
        return f"@@CODE{len(codeblocks)-1}@@"

    # raw first
    text = text.replace("&", "&amp;")
    text = text.replace("\"", "&quot;")
    text = text.replace("\'", "&#x27;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = re.sub(r"`(.+?)`", code, text)
    for k, v in emojis.items():
        text = text.replace(f":{k}:", v)

    # heading thingy after

    text = re.sub(r"^###### (.+)", r"<h6>\1</h6>", text, flags=re.MULTILINE)
    text = re.sub(r"^##### (.+)", r"<h5>\1</h5>", text, flags=re.MULTILINE)
    text = re.sub(r"^#### (.+)", r"<h4>\1</h4>", text, flags=re.MULTILINE)
    text = re.sub(r"^### (.+)", r"<h3>\1</h3>", text, flags=re.MULTILINE)
    text = re.sub(r"^## (.+)", r"<h2>\1</h2>", text, flags=re.MULTILINE)
    text = re.sub(r"^# (.+)", r"<h1>\1</h1>", text, flags=re.MULTILINE)

    # inline
    text = listparse(text)
    text = text.replace("&lt;br&gt;", "<br>")
    text = re.sub(r'''img:(https?://[^\s"'&<>]+)''', r'<img src="\1">', text)
    text = re.sub(r'''link:(https?://[^\s"'&<>]+)''', r'<a href="\1">\1</a>', text)
    text = re.sub(r"\*\*\*(.*?)\*\*\*", r"<i><b>\1</b></i>", text)
    text = re.sub(r"(?<!\w)_(.+?)_(?!\w)", r"<i>\1</i>", text)
    text = re.sub(r"(?<!\w)\*(.+?)\*(?!\w)", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\w)~~(.+?)~~(?!\w)", r"<s>\1</s>", text)
    text = re.sub(r"(?<!\w)\|\|(.+?)\|\|(?!\w)", r'<span class="spoiler">\1</span>', text)
    # hr
    text = re.sub(r"^---$", "<hr>", text, flags=re.MULTILINE)
    for i, block in enumerate(codeblocks):
        text = text.replace(f"@@CODE{i}@@", block)
    return text



@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/render", methods=["POST"])
def render():
    mltext = request.form.get("bd", "")
    html = parse(mltext)
    return render_template("render.html", render=html)

serve(app, host="0.0.0.0", port=2048)