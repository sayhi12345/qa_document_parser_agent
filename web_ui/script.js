document.addEventListener("DOMContentLoaded", () => {
  const urlInput = document.getElementById("doc-url");
  const parseBtn = document.getElementById("parse-btn");
  const uploadCheckbox = document.getElementById("upload-confluence");
  const folderSelection = document.getElementById("folder-selection");
  const confluenceSelect = document.getElementById("confluence-folder");
  const searchActivityCheckbox = document.getElementById(
    "search-activity-node"
  );
  const loadingDiv = document.getElementById("loading");
  const resultContainer = document.getElementById("result-container");
  const resultContent = document.getElementById("result-content");
  const copyBtn = document.getElementById("copy-btn");
  const themeToggle = document.getElementById("theme-toggle");

  let currentMarkdown = "";

  // ─────────────────────────────────────────────────────────────
  // THEME TOGGLE FUNCTIONALITY
  // ─────────────────────────────────────────────────────────────

  // Check for saved theme preference or default to dark
  const savedTheme = localStorage.getItem("theme");
  if (savedTheme) {
    document.documentElement.setAttribute("data-theme", savedTheme);
  }
  // If no saved preference, default is dark (no data-theme attribute needed)

  themeToggle.addEventListener("click", () => {
    const currentTheme = document.documentElement.getAttribute("data-theme");
    const newTheme = currentTheme === "light" ? "dark" : "light";

    if (newTheme === "dark") {
      document.documentElement.removeAttribute("data-theme");
    } else {
      document.documentElement.setAttribute("data-theme", newTheme);
    }

    localStorage.setItem("theme", newTheme);
  });

  // Toggle folder selection visibility based on upload checkbox
  uploadCheckbox.addEventListener("change", () => {
    if (uploadCheckbox.checked) {
      folderSelection.classList.remove("hidden");
    } else {
      folderSelection.classList.add("hidden");
    }
  });

  parseBtn.addEventListener("click", handleParse);
  urlInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      handleParse();
    }
  });

  copyBtn.addEventListener("click", () => {
    if (!currentMarkdown) return;

    navigator.clipboard.writeText(currentMarkdown).then(() => {
      const originalHtml = copyBtn.innerHTML;

      // Success State
      copyBtn.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#00ff9d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="20 6 9 17 4 12"></polyline>
        </svg>
        <span style="color: #00ff9d">Copied!</span>
      `;
      copyBtn.style.borderColor = "#00ff9d";
      copyBtn.style.background = "rgba(0, 255, 157, 0.1)";

      setTimeout(() => {
        copyBtn.innerHTML = originalHtml;
        copyBtn.style.borderColor = "";
        copyBtn.style.background = "";
      }, 2000);
    });
  });

  /**
   * Detect if a URL is a Confluence URL (contains atlassian.net)
   * @param {string} url - The URL to check
   * @returns {boolean} - True if Confluence URL
   */
  function isConfluenceUrl(url) {
    return url.includes("atlassian.net");
  }

  /**
   * Detect if a URL is a Figma URL (contains figma.com)
   * @param {string} url - The URL to check
   * @returns {boolean} - True if Figma URL
   */
  function isFigmaUrl(url) {
    return url.includes("figma.com");
  }

  async function handleParse() {
    const url = urlInput.value.trim();
    if (!url) {
      // Shake animation for empty input
      const wrapper = urlInput.closest(".input-wrapper");
      wrapper.style.animation = "shake 0.4s cubic-bezier(.36,.07,.19,.97) both";
      wrapper.style.borderColor = "#ff0055";
      setTimeout(() => {
        wrapper.style.animation = "";
        wrapper.style.borderColor = "";
      }, 400);
      return;
    }

    // Determine which endpoint to call based on URL type
    let endpoint;
    let requestBody;

    const publishConfluence = uploadCheckbox.checked;
    const confluenceFolderId = publishConfluence
      ? confluenceSelect.value
      : null;

    if (isConfluenceUrl(url)) {
      endpoint = "/confluence/parse";
      console.log("Confluence URL detected");
      requestBody = {
        url: url,
        publish_confluence: publishConfluence,
        confluence_folder_id: publishConfluence ? confluenceFolderId : null,
      };
    } else if (isFigmaUrl(url)) {
      endpoint = "/figma/parse";
      console.log("Figma URL detected");
      requestBody = {
        url: url,
        publish_confluence: publishConfluence,
        confluence_folder_id: publishConfluence ? confluenceFolderId : null,
        search_activity_node: searchActivityCheckbox.checked,
      };
    } else {
      alert("Unsupported URL. Please enter a Figma or Confluence URL.");
      return;
    }

    // Reset UI
    resultContainer.classList.add("hidden");
    loadingDiv.classList.remove("hidden");
    parseBtn.disabled = true;
    currentMarkdown = ""; // Reset stored markdown

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to parse file");
      }

      const data = await response.json();
      currentMarkdown = data.summary; // Store for copy button

      // Render Markdown
      resultContent.innerHTML = marked.parse(data.summary);

      if (data.confluence_url) {
        const linkContainer = document.createElement("div");
        linkContainer.className = "confluence-link-banner";
        linkContainer.innerHTML = `
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
            <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
          </svg>
          <div>
            <span class="confluence-label">已上傳到 Confluence</span>
            <a href="${data.confluence_url}" target="_blank" rel="noopener">${data.confluence_url}</a>
          </div>
        `;
        resultContent.prepend(linkContainer);
      }

      resultContainer.classList.remove("hidden");

      // Scroll to result
      resultContainer.scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (error) {
      alert(`Error: ${error.message}`);
    } finally {
      loadingDiv.classList.add("hidden");
      parseBtn.disabled = false;
    }
  }

  // Add shake keyframes dynamically if not present
  if (!document.getElementById("shake-style")) {
    const style = document.createElement("style");
    style.id = "shake-style";
    style.textContent = `
        @keyframes shake {
          10%, 90% { transform: translate3d(-1px, 0, 0); }
          20%, 80% { transform: translate3d(2px, 0, 0); }
          30%, 50%, 70% { transform: translate3d(-4px, 0, 0); }
          40%, 60% { transform: translate3d(4px, 0, 0); }
        }
      `;
    document.head.appendChild(style);
  }
});
