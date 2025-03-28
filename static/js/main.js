document.addEventListener("DOMContentLoaded", () => {
  // Handle browser back/forward navigation
  window.addEventListener("popstate", (event) => {
    // Reload main content from current URL
    htmx.ajax("GET", window.location.href, {
      target: "#content",
      swap: "innerHTML",
      headers: {
        "HX-Request": "true", // Force partial responses
      },
    });
  });
});

document.addEventListener("alpine:init", () => {
  Alpine.store("navigation", {
    currentPath: window.location.pathname,
  });
});

htmx.on("htmx:afterSwap", (event) => {
  Alpine.store("navigation").currentPath = new URL(
    event.detail.xhr.responseURL,
  ).pathname;
});
