export function createSocket(url, onMessage) {
    let socket;

    function connect() {
        try {
            socket = new WebSocket(url);
        } catch (e) {
            console.warn(`WebSocket failed to create: ${url}`, e);
            return;
        }

        socket.onmessage = function(event) {
            try {
                const data = JSON.parse(event.data);
                onMessage(data);
            } catch (e) {
                console.warn(`WebSocket message parse error: ${url}`, e);
            }
        };

        socket.onerror = function(e) {
            console.warn(`WebSocket error: ${url}`, e);
        };

        socket.onclose = function(e) {
            console.warn(`WebSocket closed: ${url} — code: ${e.code}`);
        };
    }

    connect();
}