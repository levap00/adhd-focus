const DEFAULT_NOTIFICATION_ICON = "/static/apple-touch-icon.png";

self.addEventListener("install", (event) => {
    event.waitUntil(self.skipWaiting());
});

self.addEventListener("activate", (event) => {
    event.waitUntil(self.clients.claim());
});

self.addEventListener("push", (event) => {
    let payload = {};
    if (event.data) {
        try {
            payload = event.data.json();
        } catch (error) {
            payload = { body: event.data.text() };
        }
    }

    const title = payload.title || "ADHD Focus";
    const options = {
        body: payload.body || "Masz nowe przypomnienie.",
        icon: payload.icon || DEFAULT_NOTIFICATION_ICON,
        badge: payload.badge || DEFAULT_NOTIFICATION_ICON,
        tag: payload.tag || `adhd-focus-${Date.now()}`,
        data: {
            url: payload.url || "/",
            ...(payload.data || {}),
        },
        renotify: Boolean(payload.renotify),
        requireInteraction: Boolean(payload.requireInteraction),
    };

    event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener("notificationclick", (event) => {
    event.notification.close();
    const targetUrl = new URL(event.notification.data?.url || "/", self.location.origin).href;

    event.waitUntil((async () => {
        const clientsList = await self.clients.matchAll({ type: "window", includeUncontrolled: true });
        for (const client of clientsList) {
            if ("focus" in client && client.url.startsWith(self.location.origin)) {
                await client.focus();
                if ("navigate" in client) {
                    return client.navigate(targetUrl);
                }
                return;
            }
        }
        if (self.clients.openWindow) {
            return self.clients.openWindow(targetUrl);
        }
    })());
});
