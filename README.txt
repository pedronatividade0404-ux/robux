VERCEL
1. Suba esta pasta para um repositório GitHub.
2. Importe o repositório na Vercel.
3. Em Settings > Environment Variables crie:
   DISCORD_WEBHOOK_URL = seu webhook do Discord
4. Deploy.

LINK TIKTOK SEM REDEPLOY
O index.html já lê:
https://raw.githubusercontent.com/pedronatividade0404-ux/hhh/refs/heads/main/tiktok-link.txt

Para trocar o link, edite SOMENTE o conteúdo de tiktok-link.txt nesse repositório GitHub.
Coloque uma única URL HTTPS do TikTok em uma linha. O site consulta o TXT novamente sem precisar redeploy.

COMPROVANTE
Ao clicar em "Aceitar e enviar", o navegador envia o nick salvo + imagem para /api/send-proof.
A função Python envia ambos ao webhook do Discord.
PNG/JPG/WEBP, máximo 3 MB.
