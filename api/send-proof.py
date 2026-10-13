from http.server import BaseHTTPRequestHandler
import os, json, base64, urllib.request, urllib.error, uuid

MAX_BYTES = 3 * 1024 * 1024
ALLOWED = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}

def multipart(fields, file_field, filename, content_type, data):
    boundary = "----NexaBoundary" + uuid.uuid4().hex
    b = boundary.encode()
    out = bytearray()
    for k, v in fields.items():
        out += b"--" + b + b"\r\n"
        out += f'Content-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode("utf-8")
    out += b"--" + b + b"\r\n"
    out += f'Content-Disposition: form-data; name="{file_field}"; filename="{filename}"\r\n'.encode("utf-8")
    out += f"Content-Type: {content_type}\r\n\r\n".encode()
    out += data + b"\r\n--" + b + b"--\r\n"
    return bytes(out), boundary

class handler(BaseHTTPRequestHandler):
    def reply(self, code, obj):
        raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_POST(self):
        webhook = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()
        if not webhook.startswith("https://discord.com/api/webhooks/"):
            return self.reply(500, {"ok": False, "error": "DISCORD_WEBHOOK_URL não configurada"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 4_200_000:
                return self.reply(413, {"ok": False, "error": "Requisição muito grande"})
            payload = json.loads(self.rfile.read(length))
            nick = str(payload.get("nick", "")).strip()
            pack = str(payload.get("packId", "")).strip()
            data_url = str(payload.get("image", ""))
            if not nick or len(nick) > 32 or not all(c.isalnum() or c == "_" for c in nick):
                return self.reply(400, {"ok": False, "error": "Nick inválido"})
            if "," not in data_url or not data_url.startswith("data:image/"):
                return self.reply(400, {"ok": False, "error": "Imagem inválida"})
            header, encoded = data_url.split(",", 1)
            mime = header[5:].split(";", 1)[0].lower()
            if mime not in ALLOWED:
                return self.reply(400, {"ok": False, "error": "Formato não permitido"})
            image = base64.b64decode(encoded, validate=True)
            if len(image) > MAX_BYTES:
                return self.reply(413, {"ok": False, "error": "Imagem acima de 3 MB"})

            content = f"**Novo comprovante**\n**Nick Roblox:** `{nick}`"
            if pack:
                content += f"\n**Pacote:** `{pack}`"
            discord_payload = json.dumps({"content": content}, ensure_ascii=False)
            body, boundary = multipart(
                {"payload_json": discord_payload}, "files[0]",
                f"comprovante_{nick}{ALLOWED[mime]}", mime, image
            )
            req = urllib.request.Request(webhook, data=body, method="POST", headers={
                "Content-Type": f"multipart/form-data; boundary={boundary}",
                "User-Agent": "NexaRobux/1.0"
            })
            with urllib.request.urlopen(req, timeout=12) as resp:
                if resp.status not in (200, 204):
                    raise RuntimeError(f"Discord HTTP {resp.status}")
            return self.reply(200, {"ok": True})
        except (ValueError, json.JSONDecodeError, base64.binascii.Error):
            return self.reply(400, {"ok": False, "error": "Dados inválidos"})
        except urllib.error.HTTPError as e:
            return self.reply(502, {"ok": False, "error": f"Discord recusou o envio ({e.code})"})
        except Exception as e:
            return self.reply(500, {"ok": False, "error": "Falha ao enviar comprovante"})
