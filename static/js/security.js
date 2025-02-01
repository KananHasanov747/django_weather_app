(function () {
  let devToolsCheckActive = false;
  let baseThreshold = 100;

  // Calibrate initial threshold
  (function calibrateThreshold() {
    const start = performance.now();
    debugger;
    baseThreshold = (performance.now() - start) * 2;
  })();

  //function detectDevTools() {
  //  try {
  //    const start = performance.now();
  //    debugger;
  //    debugger; // Double debugger for better detection
  //    const diff = performance.now() - start;
  //
  //    // Additional detection methods
  //    const widthDiff = window.outerWidth - window.innerWidth;
  //    const heightDiff = window.outerHeight - window.innerHeight;
  //    const screenCheck = widthDiff > 200 || heightDiff > 200;
  //
  //    if (diff > baseThreshold || screenCheck) {
  //      if (!devToolsCheckActive) {
  //        devToolsCheckActive = true;
  //
  //        // Cleanup and obstruction
  //        document.body.innerHTML =
  //          '<div style="padding:20px;font-size:24px"></div>';
  //        window.stop();
  //
  //        // Redirect with delay
  //        setTimeout(() => {
  //          window.location.replace("about:blank");
  //        }, 1000);
  //      }
  //    }
  //  } catch (e) {
  //    // Silent error handling
  //  }
  //}

  // Randomized interval check
  setInterval(
    () => {
      detectDevTools();

      // Console bait check
      (function () {
        const trapElement = document.createElement("div");
        trapElement.__secretTrap = true;
        console.log(trapElement);
      })();
    },
    Math.random() * 1000 + 500,
  );

  // Enhanced console protection
  const consoleMethods = [
    "log",
    "error",
    "warn",
    "info",
    "debug",
    "dir",
    "table",
    "trace",
    "_commandLineAPI",
  ];

  consoleMethods.forEach((method) => {
    try {
      Object.defineProperty(console, method, {
        get: () => () => {
          throw new Error("Console access disabled");
        },
        set: () => {},
      });
    } catch (e) {}
  });

  // Input protection
  document.addEventListener("keydown", (event) => {
    const isDevToolsShortcut =
      event.key === "F12" ||
      (event.ctrlKey && event.shiftKey && event.key === "I") ||
      (event.metaKey &&
        event.altKey &&
        (event.key === "i" || event.code === "KeyI"));

    if (isDevToolsShortcut) {
      event.preventDefault();
      event.stopImmediatePropagation();
      document.body.innerHTML = '<div style="padding:20px"></div>';
    }
  });

  // UI protection
  document.addEventListener("contextmenu", (event) => {
    event.preventDefault();
    document.body.insertAdjacentHTML(
      "beforeend",
      '<div style="position:fixed;top:0;left:0;right:0;background:red;color:white;padding:10px"></div>',
    );
    return false;
  });

  // Frame protection
  if (window.top !== window.self) {
    window.top.location = window.self.location;
  }
})();
