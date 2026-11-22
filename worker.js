export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // 1. CORS Proxy endpoint for Pluto TV & restricted streams
    if (url.pathname === "/proxy") {
      if (request.method === "OPTIONS") {
        return new Response(null, {
          headers: {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
            "Access-Control-Allow-Headers": "*"
          }
        });
      }

      const targetUrl = url.searchParams.get("url");
      if (!targetUrl) {
        return new Response("Missing 'url' parameter", { 
          status: 400,
          headers: { "Access-Control-Allow-Origin": "*" }
        });
      }

      try {
        const response = await fetch(targetUrl, {
          headers: {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Referer": "https://pluto.tv/"
          }
        });

        if (!response.ok) {
          return new Response(response.statusText, { 
            status: response.status,
            headers: { "Access-Control-Allow-Origin": "*" }
          });
        }

        const contentType = response.headers.get("content-type") || "";
        
        // If m3u8 playlist, rewrite internal sub-manifest links to also pass through proxy
        if (contentType.includes("mpegurl") || targetUrl.includes(".m3u8")) {
          const text = await response.text();
          const proxyBase = `${url.origin}/proxy`;
          const targetBase = targetUrl.substring(0, targetUrl.lastIndexOf("/") + 1);

          const lines = text.split("\n");
          const newLines = lines.map(line => {
            const trimmed = line.trim();
            if (!trimmed) return line;
            if (trimmed.startsWith("#")) {
              if (trimmed.includes('URI="')) {
                return trimmed.replace(/URI="([^"]+)"/g, (match, p1) => {
                  const fullUri = p1.startsWith("http") ? p1 : new URL(p1, targetBase).href;
                  return `URI="${proxyBase}?url=${encodeURIComponent(fullUri)}"`;
                });
              }
              return line;
            }
            const fullUrl = trimmed.startsWith("http") ? trimmed : new URL(trimmed, targetBase).href;
            if (fullUrl.includes(".m3u8")) {
              return `${proxyBase}?url=${encodeURIComponent(fullUrl)}`;
            }
            return fullUrl;
          });

          return new Response(newLines.join("\n"), {
            status: 200,
            headers: {
              "Content-Type": "application/vnd.apple.mpegurl",
              "Access-Control-Allow-Origin": "*",
              "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
              "Access-Control-Allow-Headers": "*",
              "Cache-Control": "public, max-age=10"
            }
          });
        }

        // Non-manifest responses (keys, headers)
        const newHeaders = new Headers(response.headers);
        newHeaders.set("Access-Control-Allow-Origin", "*");
        newHeaders.set("Access-Control-Allow-Methods", "GET, HEAD, OPTIONS");
        newHeaders.set("Access-Control-Allow-Headers", "*");

        return new Response(response.body, {
          status: response.status,
          headers: newHeaders
        });
      } catch (err) {
        return new Response(`Proxy Error: ${err.message}`, {
          status: 502,
          headers: { "Access-Control-Allow-Origin": "*" }
        });
      }
    }

    // 2. Serve static assets from player/
    if (env.ASSETS) {
      return env.ASSETS.fetch(request);
    }

    return new Response("Not found", { status: 404 });
  }
};
