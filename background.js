// Minimal Background Script
chrome.runtime.onInstalled.addListener(() => {
  console.log("EasyReaderADHD Installed");
  chrome.storage.local.set({
    enabled: true,
    highlightingToggles: {
      noun: true,
      verb: true,
      adj: true,
      comparative: true,
    },
  });
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "tabStartup") {
    // Just acknowledge
    sendResponse({ received: true });
  }

  if (message.action === "callLLM") {
    // Perform the API call in the background to avoid CORS
    (async () => {
      try {
        let { endpoint, apiKey } = message;
        let model = message.body.model;

        // Update body model
        if (model) message.body.model = model;

        // Auto-fix endpoint
        if (endpoint) {
          if (endpoint.endsWith("/")) endpoint = endpoint.slice(0, -1);
          if (endpoint.endsWith("/v1")) endpoint += "/chat/completions";
        }

        const response = await fetch(endpoint, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${apiKey}`,
          },
          body: JSON.stringify(message.body),
        });

        if (!response.ok) {
          const errText = await response.text();
          sendResponse({
            success: false,
            error: errText,
            status: response.status,
          });
          return;
        }

        const data = await response.json();
        sendResponse({ success: true, data: data });
      } catch (error) {
        sendResponse({ success: false, error: error.message });
      }
    })();
    return true; // Keep the message channel open for async response
  }
});
