(function () {
  const TOKEN_KEY = "access_token";
  const REFRESH_KEY = "refresh_token";
  const ROLE_KEY = "user_role";

  const STATUS_CLASSES = {
    approved: "status-approved",
    pending: "status-pending",
    closed: "status-closed",
    applied: "status-applied",
    shortlisted: "status-shortlisted",
    selected: "status-selected",
    rejected: "status-rejected",
    failed: "status-failed",
  };

  function getToken() {
    return localStorage.getItem(TOKEN_KEY);
  }

  function getRefreshToken() {
    return localStorage.getItem(REFRESH_KEY);
  }

  function setTokens(access, refresh) {
    if (access) {
      localStorage.setItem(TOKEN_KEY, access);
    }
    if (refresh) {
      localStorage.setItem(REFRESH_KEY, refresh);
    }
  }

  function getRole() {
    return localStorage.getItem(ROLE_KEY);
  }

  function setRole(role) {
    if (role) {
      localStorage.setItem(ROLE_KEY, role);
    }
  }

  function clearAuth() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
    localStorage.removeItem(ROLE_KEY);
  }

  function logout() {
    clearAuth();
    window.location.href = "/login/";
  }

  function requireAuth() {
    if (!getToken()) {
      window.location.href = "/login/";
      return false;
    }
    return true;
  }

  async function refreshAccessToken() {
    const refresh = getRefreshToken();
    if (!refresh) {
      return false;
    }

    const response = await fetch("/api/token/refresh/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ refresh }),
    });

    if (!response.ok) {
      clearAuth();
      return false;
    }

    const data = await response.json();
    setTokens(data.access);
    return Boolean(data.access);
  }

  async function request(url, options = {}) {
    const result = await sendRequest(url, options);

    if (
      result.response.status === 401 &&
      options.auth !== false &&
      !options.skipRefresh &&
      (await refreshAccessToken())
    ) {
      return sendRequest(
        url,
        Object.assign({}, options, { skipRefresh: true }),
      );
    }

    if (result.response.status === 401 && options.auth !== false) {
      clearAuth();
    }

    return result;
  }

  async function sendRequest(url, options = {}) {
    const headers = new Headers(options.headers || {});
    const authEnabled = options.auth !== false;
    const token = getToken();

    if (authEnabled && token) {
      headers.set("Authorization", "Bearer " + token);
    }

    const hasBody = Object.prototype.hasOwnProperty.call(options, "body");
    if (
      hasBody &&
      !(options.body instanceof FormData) &&
      !headers.has("Content-Type")
    ) {
      headers.set("Content-Type", "application/json");
    }

    try {
      const response = await fetch(url, {
        method: options.method || "GET",
        body: options.body,
        headers,
      });

      const contentType = response.headers.get("content-type") || "";
      let data = null;

      if (contentType.includes("application/json")) {
        try {
          data = await response.json();
        } catch (error) {
          data = null;
        }
      } else {
        try {
          data = await response.text();
        } catch (error) {
          data = null;
        }
      }

      return { response, data };
    } catch (error) {
      const fakeResponse = new Response(null, {
        status: 0,
        statusText: "Network Error",
      });
      return { response: fakeResponse, data: null, error };
    }
  }

  function escapeHtml(value) {
    if (value === null || value === undefined) {
      return "";
    }

    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  let currentNotifications = [];

  async function fetchNotifications() {
    if (!localStorage.getItem("access_token")) return;
    try {
        const res = await request("/api/notifications/", { method: "GET" });
        if (res.response && res.response.ok && res.data) {
            currentNotifications = res.data.notifications || [];
            const count = res.data.count || 0;
            const badge = document.getElementById("notificationBadge");
            if (badge) {
                if (count > 0) {
                    badge.textContent = count;
                    badge.style.display = "flex";
                } else {
                    badge.style.display = "none";
                }
            }
        }
    } catch (err) {
        console.error("Failed to fetch notifications", err);
    }
  }

  function startNotificationPolling() {
      fetchNotifications();
      setInterval(fetchNotifications, 15000); // Poll every 15 seconds
  }

  function toggleNotificationSidebar() {
      let sidebar = document.getElementById("notificationSidebar");
      let overlay = document.getElementById("notificationOverlay");
      
      if (!sidebar) {
          overlay = document.createElement("div");
          overlay.id = "notificationOverlay";
          overlay.style.cssText = "position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.5);z-index:999;display:none;animation:fadeIn 0.3s ease;";
          overlay.onclick = toggleNotificationSidebar;
          document.body.appendChild(overlay);

          sidebar = document.createElement("div");
          sidebar.id = "notificationSidebar";
          sidebar.style.cssText = "position:fixed;top:0;right:-350px;width:350px;height:100vh;background:#ffffff;box-shadow:-2px 0 10px rgba(0,0,0,0.3);z-index:1000;transition:right 0.3s ease;display:flex;flex-direction:column;border-left:1px solid var(--line);";
          sidebar.innerHTML = `
              <div style="padding:20px;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;align-items:center;">
                  <h3 style="margin:0;color:var(--text-primary);">Notifications</h3>
                  <button onclick="AppUI.toggleNotificationSidebar()" style="background:transparent;border:none;font-size:1.5rem;color:var(--text-muted);cursor:pointer;">&times;</button>
              </div>
              <div id="notificationList" style="flex:1;overflow-y:auto;"></div>
          `;
          document.body.appendChild(sidebar);
      }

      if (sidebar.style.right === "0px") {
          sidebar.style.right = "-350px";
          overlay.style.display = "none";
      } else {
          sidebar.style.right = "0px";
          overlay.style.display = "block";
          renderNotificationsInSidebar();
          // Mark as read after a short delay
          setTimeout(() => {
              request("/api/notifications/", { method: "POST" }).then(() => fetchNotifications());
          }, 1000);
      }
  }

  function renderNotificationsInSidebar() {
      const list = document.getElementById("notificationList");
      if (!list) return;
      
      if (currentNotifications.length === 0) {
          list.innerHTML = '<div style="padding:30px 20px;text-align:center;color:var(--text-muted);">No notifications yet.</div>';
          return;
      }

      list.innerHTML = currentNotifications.map(n => `
          <div style="padding:16px 20px;border-bottom:1px solid var(--line);background:${n.is_read ? 'transparent' : 'rgba(255,125,73,0.05)'};">
              <div style="font-size:0.95rem;color:var(--text-primary);margin-bottom:6px;line-height:1.4;">${AppUI.escapeHtml(n.message)}</div>
              <div style="font-size:0.8rem;color:var(--text-muted);">${new Date(n.created_at).toLocaleString()}</div>
          </div>
      `).join("");
  }

  // Start polling when script loads (if authenticated)
  setTimeout(startNotificationPolling, 1000);

  function openSupportModal() {
      let modal = document.getElementById("supportModal");
      if (!modal) {
          const overlay = document.createElement("div");
          overlay.id = "supportModalOverlay";
          overlay.style.cssText = "position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.5);z-index:1000;display:flex;align-items:center;justify-content:center;animation:fadeIn 0.3s ease;";
          
          modal = document.createElement("div");
          modal.id = "supportModal";
          modal.style.cssText = "background:#ffffff;border:1px solid var(--line);border-radius:var(--radius-lg);padding:24px;width:90%;max-width:550px;max-height:80vh;overflow-y:auto;box-shadow:var(--shadow-lg);animation:slideUp 0.4s cubic-bezier(0.4, 0, 0.2, 1);";
          modal.innerHTML = `
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
                  <h2 style="margin:0;">Support Center</h2>
                  <div>
                      <button class="btn btn-ghost btn-sm" id="btnNewTicket" onclick="AppUI.toggleSupportView('new')">New Ticket</button>
                      <button class="btn btn-ghost btn-sm" id="btnMyTickets" onclick="AppUI.toggleSupportView('history')">My Tickets</button>
                  </div>
              </div>
              
              <div id="supportNewTicketView">
                  <div class="form-group">
                      <label class="form-label">Subject</label>
                      <input type="text" id="supportSubject" class="form-control" placeholder="Briefly describe your issue">
                  </div>
                  <div class="form-group">
                      <label class="form-label">Message</label>
                      <textarea id="supportMessage" class="form-control" rows="4" placeholder="How can we help?"></textarea>
                  </div>
                  <div class="actions-row" style="justify-content:flex-end;margin-top:20px;gap:10px;">
                      <button class="btn btn-ghost" onclick="document.getElementById('supportModalOverlay').style.display='none'">Cancel</button>
                      <button class="btn btn-primary" onclick="AppUI.submitSupportRequest(this)">Submit Request</button>
                  </div>
              </div>
              
              <div id="supportHistoryView" style="display:none;">
                  <div id="supportHistoryList">Loading...</div>
              </div>
          `;
          overlay.appendChild(modal);
          document.body.appendChild(overlay);
          
          overlay.onclick = function(e) {
              if (e.target === overlay) overlay.style.display = 'none';
          }
      }
      document.getElementById("supportSubject").value = "";
      document.getElementById("supportMessage").value = "";
      document.getElementById("supportModalOverlay").style.display = "flex";
      toggleSupportView("new");
  }

  function toggleSupportView(view) {
      if (view === 'new') {
          document.getElementById('supportNewTicketView').style.display = 'block';
          document.getElementById('supportHistoryView').style.display = 'none';
          document.getElementById('btnNewTicket').style.fontWeight = 'bold';
          document.getElementById('btnMyTickets').style.fontWeight = 'normal';
      } else {
          document.getElementById('supportNewTicketView').style.display = 'none';
          document.getElementById('supportHistoryView').style.display = 'block';
          document.getElementById('btnNewTicket').style.fontWeight = 'normal';
          document.getElementById('btnMyTickets').style.fontWeight = 'bold';
          loadSupportHistory();
      }
  }

  async function loadSupportHistory() {
      const list = document.getElementById("supportHistoryList");
      list.innerHTML = '<span class="loader"></span> Loading tickets...';
      const res = await request("/api/support/history/");
      if (res.response.ok) {
          if (res.data.length === 0) {
              list.innerHTML = '<div style="color:var(--text-muted);text-align:center;padding:20px;">No support tickets submitted yet.</div>';
              return;
          }
          list.innerHTML = res.data.map(q => `
              <div style="background:#f9fafb;border:1px solid var(--line);border-radius:var(--radius-md);padding:16px;margin-bottom:12px;">
                  <div style="display:flex;justify-content:space-between;margin-bottom:8px;">
                      <strong>${AppUI.escapeHtml(q.subject)}</strong>
                      ${AppUI.statusBadge(q.is_resolved ? 'resolved' : 'pending', q.is_resolved ? 'Resolved' : 'Pending')}
                  </div>
                  <div style="color:var(--text-muted);font-size:0.9rem;margin-bottom:8px;">${AppUI.escapeHtml(q.message)}</div>
                  ${q.admin_reply ? `<div style="background:rgba(17,185,129,0.1);padding:10px;border-radius:6px;font-size:0.9rem;"><strong>Admin Reply:</strong> ${AppUI.escapeHtml(q.admin_reply)}</div>` : ''}
              </div>
          `).join('');
      } else {
          list.innerHTML = '<div style="color:var(--danger);">Failed to load history.</div>';
      }
  }

  async function submitSupportRequest(btn) {
      const subject = document.getElementById("supportSubject").value.trim();
      const message = document.getElementById("supportMessage").value.trim();
      
      if (!subject || !message) {
          showToast("Please fill in both subject and message", "error");
          return;
      }
      
      btn.disabled = true;
      btn.textContent = "Submitting...";
      
      try {
          const res = await request("/api/support/", {
              method: "POST",
              body: JSON.stringify({ subject, message })
          });
          
          if (res.response.ok) {
              document.getElementById('supportModalOverlay').style.display = 'none';
              showToast("Support request submitted successfully!", "success");
          } else {
              showToast(errorText(res.data) || "Failed to submit request", "error");
          }
      } catch (err) {
          showToast("Network error submitting request", "error");
      }
      
      btn.disabled = false;
      btn.textContent = "Submit Request";
  }

  function errorText(payload) {
    if (!payload) {
      return "Something went wrong. Please try again.";
    }

    if (typeof payload === "string") {
      return payload;
    }

    if (Array.isArray(payload)) {
      return payload.join(" ");
    }

    if (typeof payload === "object") {
      if (payload.detail) {
        return payload.detail;
      }

      const parts = [];
      Object.keys(payload).forEach((key) => {
        const value = payload[key];
        if (Array.isArray(value)) {
          parts.push(value.join(", "));
          return;
        }
        if (typeof value === "object" && value !== null) {
          parts.push(errorText(value));
          return;
        }
        parts.push(String(value));
      });

      return parts.join(" ");
    }

    return "Request failed. Please verify your input and try again.";
  }

  function statusClass(status) {
    if (!status) {
      return "status-pending";
    }
    return STATUS_CLASSES[String(status).toLowerCase()] || "status-pending";
  }

  function statusBadge(status, customLabel) {
    const label = customLabel || String(status || "pending");
    return (
      '<span class="badge-status ' +
      statusClass(status) +
      '">' +
      escapeHtml(label) +
      "</span>"
    );
  }

  function listResults(payload) {
    if (!payload) {
      return [];
    }
    if (Array.isArray(payload)) {
      return payload;
    }
    if (Array.isArray(payload.results)) {
      return payload.results;
    }
    return [];
  }

  function formatDate(rawDate) {
    if (!rawDate) {
      return "N/A";
    }

    const parsed = new Date(rawDate);
    if (Number.isNaN(parsed.getTime())) {
      return rawDate;
    }

    return parsed.toLocaleDateString(undefined, {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  }

  function formatCtc(value) {
    if (value === null || value === undefined || value === "") {
      return "Not disclosed";
    }
    const numeric = Number(value);
    if (Number.isNaN(numeric)) {
      return value;
    }
    return numeric.toFixed(2).replace(/\.00$/, "") + " LPA";
  }

  function labelize(value) {
    if (!value) {
      return "N/A";
    }
    return String(value)
      .replaceAll("_", " ")
      .replace(/\b\w/g, function (letter) {
        return letter.toUpperCase();
      });
  }

  function showToast(message, type = "info", duration = 3000) {
    const stack = document.getElementById("toastStack");
    if (!stack) {
      return;
    }

    const toast = document.createElement("div");
    toast.className = "toast " + type;
    toast.textContent = message;
    stack.appendChild(toast);

    window.setTimeout(function () {
      toast.remove();
    }, duration);
  }

  function renderLoading(target, message = "Loading...") {
    const container =
      typeof target === "string" ? document.getElementById(target) : target;
    if (!container) {
      return;
    }

    if (container.classList.contains("stats-grid") || container.id === "studentStats" || container.id === "applicationStats" || container.id === "adminContent") {
      container.innerHTML = Array(4).fill(0).map(() => `
        <div class="skeleton-shimmer skeleton-tile"></div>
      `).join("");
      return;
    }

    container.innerHTML = `
      <div class="skeleton-card-container">
        ${Array(2).fill(0).map(() => `
          <div class="card-shell skeleton-card-item">
            <div class="skeleton-shimmer skeleton-line title"></div>
            <div class="skeleton-shimmer skeleton-line subtitle"></div>
            <div style="display:flex; flex-direction:column; gap:8px; margin-top:8px;">
              <div class="skeleton-shimmer skeleton-line meta"></div>
              <div class="skeleton-shimmer skeleton-line meta" style="width: 60%;"></div>
            </div>
            <div style="display:flex; gap:10px; margin-top:10px;">
              <div class="skeleton-shimmer skeleton-line button"></div>
              <div class="skeleton-shimmer skeleton-line button" style="width:25%;"></div>
            </div>
          </div>
        `).join("")}
      </div>
    `;
  }

  function renderEmpty(target, message) {
    const container =
      typeof target === "string" ? document.getElementById(target) : target;
    if (!container) {
      return;
    }

    let illustration = "📁";
    let title = "No records found";
    let text = message || "There are no records in this list yet.";
    let ctaHtml = "";

    if (container.id === "availableDrives") {
      illustration = "💼";
      title = "No Available Drives";
      text = "There are no open placement drives matching your criteria right now.";
    } else if (container.id === "myApplications") {
      illustration = "📝";
      title = "No Applications Yet";
      text = "Explore the available placement drives and submit your first application!";
    } else if (container.id === "drivesList") {
      illustration = "⚡";
      title = "Post Your First Drive";
      text = "Create a placement drive to start recruiting talented students from our college.";
      ctaHtml = `<a href="/company/add-drive/" class="btn btn-primary btn-sm empty-state-cta">+ Add Drive</a>`;
    } else if (container.id === "pendingCompanies") {
      illustration = "🏢";
      title = "All Caught Up!";
      text = "There are no company verification requests pending review.";
    } else if (container.id === "pendingDrives") {
      illustration = "📋";
      title = "No Pending Drives";
      text = "All company job posting requests have been reviewed and approved.";
    } else if (container.id === "supportQueries" || container.id === "supportHistoryList") {
      illustration = "✨";
      title = "All Clear!";
      text = "No support tickets are waiting or created in this view.";
    } else if (container.id === "applications") {
      illustration = "👥";
      title = "No Applicants Found";
      text = message || "No candidates have applied to this hiring drive yet.";
    }

    container.innerHTML = `
      <article class="empty-state fade-in">
        <div class="empty-state-illustration">${illustration}</div>
        <div class="empty-state-title">${title}</div>
        <div class="empty-state-text">${text}</div>
        ${ctaHtml}
      </article>
    `;
  }

  function renderError(target, message) {
    const container =
      typeof target === "string" ? document.getElementById(target) : target;
    if (!container) {
      return;
    }

    container.innerHTML = `<article class="feedback error">${escapeHtml(message)}</article>`;
  }

  function dashboardPathByRole(role) {
    if (role === "student") {
      return "/student/dashboard/";
    }
    if (role === "company") {
      return "/company/dashboard/";
    }
    return "/admin-panel/dashboard/";
  }

  async function hydrateRole() {
    if (!getToken()) {
      return null;
    }

    const storedRole = getRole();
    if (storedRole) {
      return storedRole;
    }

    const result = await request("/api/me/");
    if (result.response.ok && result.data && result.data.role) {
      setRole(result.data.role);
      return result.data.role;
    }

    if (result.response.status === 401) {
      clearAuth();
    }

    return null;
  }

  const ROLE_LINKS = {
    student: [
      { label: "Dashboard", url: "/student/dashboard/", icon: `<svg viewBox="0 0 24 24"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/></svg>` },
      { label: "Analytics", url: "/student/analytics/", icon: `<svg viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/></svg>` },
      { label: "History", url: "/student/placement-history/", icon: `<svg viewBox="0 0 24 24"><path d="M13 3c-4.97 0-9 4.03-9 9H1l3.89 3.89.07.14L9 12H6c0-3.87 3.13-7 7-7s7 3.13 7 7-3.13 7-7 7c-1.93 0-3.68-.79-4.94-2.06l-1.42 1.42C8.27 19.99 10.51 21 13 21c4.97 0 9-4.03 9-9s-4.03-9-9-9zm-1 5v5l4.28 2.54.72-1.21-3.5-2.08V8H12z"/></svg>` },
      { label: "Profile", url: "/student/edit-profile/", icon: `<svg viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>` }
    ],
    company: [
      { label: "Dashboard", url: "/company/dashboard/", icon: `<svg viewBox="0 0 24 24"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/></svg>` },
      { label: "Create Drive", url: "/company/add-drive/", icon: `<svg viewBox="0 0 24 24"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>` },
      { label: "Analytics", url: "/company/analytics/", icon: `<svg viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/></svg>` },
      { label: "Profile", url: "/company/edit-profile/", icon: `<svg viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>` }
    ],
    admin: [
      { label: "Dashboard", url: "/admin-panel/dashboard/", icon: `<svg viewBox="0 0 24 24"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/></svg>` },
      { label: "Deep Analytics", url: "/admin-panel/analytics/", icon: `<svg viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/></svg>` }
    ]
  };

  function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute("data-theme") || "light";
    const newTheme = currentTheme === "dark" ? "light" : "dark";
    
    document.documentElement.setAttribute("data-theme", newTheme);
    if (newTheme === "dark") {
      document.body.classList.add("dark-theme");
      localStorage.setItem("app_theme", "dark");
    } else {
      document.body.classList.remove("dark-theme");
      localStorage.setItem("app_theme", "light");
    }
    
    updateThemeUI(newTheme);
  }

  function updateThemeUI(theme) {
    const texts = document.querySelectorAll("#themeText");
    const icons = document.querySelectorAll("#themeIcon");
    
    texts.forEach(txt => {
      txt.textContent = theme === "dark" ? "Light Mode" : "Dark Mode";
    });
    
    icons.forEach(ico => {
      if (theme === "dark") {
        ico.innerHTML = `<path d="M12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zM2 13h2c.55 0 1-.45 1-1s-.45-1-1-1H2c-.55 0-1 .45-1 1s.45 1 1 1zm18 0h2c.55 0 1-.45 1-1s-.45-1-1-1h-2c-.55 0-1 .45-1 1s.45 1 1 1zM11 2v2c0 .55.45 1 1 1s1-.45 1-1V2c0-.55-.45-1-1-1s-1 .45-1 1zm0 18v2c0 .55.45 1 1 1s1-.45 1-1v-2c0-.55-.45-1-1-1s-1 .45-1 1zM5.99 4.58c-.39-.39-1.03-.39-1.41 0s-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0s.39-1.03 0-1.41L5.99 4.58zm12.37 12.37c-.39-.39-1.03-.39-1.41 0s-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0s.39-1.03 0-1.41L5.99 4.58zm1.06-12.37c-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06c.39-.38.39-1.02 0-1.41zm-12.37 12.37c-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06c.39-.38.39-1.02 0-1.41z"/>`;
      } else {
        ico.innerHTML = `<path d="M12 3c-4.97 0-9 4.03-9 9s4.03 9 9 9 9-4.03 9-9c0-.46-.04-.92-.1-1.36-.98 1.37-2.58 2.26-4.4 2.26-3.03 0-5.5-2.47-5.5-5.5 0-1.82.89-3.42 2.26-4.4-.44-.06-.9-.1-1.36-.1z"/>`;
      }
    });
  }

  async function renderNavbar() {
    const nav = document.getElementById("navButtons");
    const sidebar = document.getElementById("appSidebar");
    const trigger = document.getElementById("sidebarTrigger");
    const mobileBtn = document.getElementById("mobileMenuBtn");
    
    if (!nav) {
      return;
    }

    const token = getToken();
    const currentPath = window.location.pathname;
    const isAuthPage = /^\/(login|signup)/.test(currentPath);

    if (isAuthPage) {
      nav.innerHTML = "";
      if (sidebar) sidebar.style.display = "none";
      if (trigger) trigger.style.display = "none";
      if (mobileBtn) mobileBtn.style.display = "none";
      return;
    }

    if (!token) {
      nav.innerHTML = [
        '<a class="btn btn-ghost btn-sm" href="/login/">Login</a>',
        '<a class="btn btn-primary btn-sm" href="/signup/student/">Student Sign Up</a>',
        '<a class="btn btn-secondary btn-sm" href="/signup/company/">Company Sign Up</a>',
      ].join("");
      if (sidebar) sidebar.style.display = "none";
      if (trigger) trigger.style.display = "none";
      if (mobileBtn) mobileBtn.style.display = "none";
      return;
    }

    const role = await hydrateRole();
    const dashPath = dashboardPathByRole(role);
    const isAdminPath = currentPath.startsWith("/admin-panel/");

    const currentTheme = document.documentElement.getAttribute("data-theme") || "light";
    const isDark = currentTheme === "dark";
    const themeIcon = isDark 
      ? `<path d="M12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zM2 13h2c.55 0 1-.45 1-1s-.45-1-1-1H2c-.55 0-1 .45-1 1s.45 1 1 1zm18 0h2c.55 0 1-.45 1-1s-.45-1-1-1h-2c-.55 0-1 .45-1 1s.45 1 1 1zM11 2v2c0 .55.45 1 1 1s1-.45 1-1V2c0-.55-.45-1-1-1s-1 .45-1 1zm0 18v2c0 .55.45 1 1 1s1-.45 1-1v-2c0-.55-.45-1-1-1s-1 .45-1 1zM5.99 4.58c-.39-.39-1.03-.39-1.41 0s-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0s.39-1.03 0-1.41L5.99 4.58zm12.37 12.37c-.39-.39-1.03-.39-1.41 0s-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0s.39-1.03 0-1.41L5.99 4.58zm1.06-12.37c-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06c.39-.38.39-1.02 0-1.41zm-12.37 12.37c-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06c.39-.38.39-1.02 0-1.41z"/>`
      : `<path d="M12 3c-4.97 0-9 4.03-9 9s4.03 9 9 9 9-4.03 9-9c0-.46-.04-.92-.1-1.36-.98 1.37-2.58 2.26-4.4 2.26-3.03 0-5.5-2.47-5.5-5.5 0-1.82.89-3.42 2.26-4.4-.44-.06-.9-.1-1.36-.1z"/>`;

    // Populate Desktop Left Sidebar
    if (sidebar && role && ROLE_LINKS[role]) {
      sidebar.style.display = "flex";
      if (trigger) trigger.style.display = "block";
      if (mobileBtn) mobileBtn.style.display = "block";

      const navContainer = document.getElementById("sidebarNav");
      if (navContainer) {
        navContainer.innerHTML = ROLE_LINKS[role].map(link => {
          const isActive = currentPath === link.url;
          return `
            <a href="${link.url}" class="sidebar-link ${isActive ? 'active' : ''}">
              ${link.icon}
              <span>${escapeHtml(link.label)}</span>
            </a>
          `;
        }).join("");
      }

      // Populate Desktop Left Sidebar Footer
      const footerContainer = document.getElementById("sidebarFooter");
      if (footerContainer) {
        let footerParts = [];
        
        // Theme Toggle Button
        footerParts.push(`
          <button class="footer-btn" onclick="AppUI.toggleTheme()" title="Toggle Theme">
            <svg viewBox="0 0 24 24" id="themeIcon">${themeIcon}</svg>
            <span id="themeText">${isDark ? "Light Mode" : "Dark Mode"}</span>
          </button>
        `);

        // Notification Bell inside Sidebar Footer
        footerParts.push(`
          <button class="footer-btn" onclick="AppUI.toggleNotificationSidebar()" title="Notifications" style="position: relative;">
            <svg viewBox="0 0 448 512" style="fill:currentColor;"><path d="M224 0c-17.7 0-32 14.3-32 32V49.9C119.5 61.4 64 124.2 64 200v33.4c0 45.4-15.5 89.5-43.8 124.9L5.3 377c-5.8 7.2-6.9 17.1-2.9 25.4S14.8 416 24 416H424c9.2 0 17.6-5.3 21.6-13.6s2.9-18.2-2.9-25.4l-14.9-18.6C399.5 322.9 384 278.8 384 233.4V200c0-75.8-55.5-138.6-128-150.1V32c0-17.7-14.3-32-32-32zm0 96h8c57.4 0 104 46.6 104 104v33.4c0 47.9 13.9 94.6 39.7 134.6H72.3C98.1 328 112 281.3 112 233.4V200c0-57.4 46.6-104 104-104h8zm64 352H224 160c0 17 6.7 33.3 18.7 45.3s28.3 18.7 45.3 18.7s33.3-6.7 45.3-18.7s18.7-28.3 18.7-45.3z"></path></svg>
            <span>Notifications</span>
            <span id="notificationBadge" style="position: absolute; top: 6px; left: 24px; background: var(--danger); color: white; border-radius: 50%; width: 14px; height: 14px; display: none; align-items: center; justify-content: center; font-size: 0.6rem; font-weight: bold; border: 2px solid var(--bg-2);">0</span>
          </button>
        `);

        // Support Button inside Sidebar Footer
        if (!isAdminPath) {
          footerParts.push(`
            <button class="footer-btn" onclick="AppUI.openSupportModal()" title="Support">
              <svg viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-1.99.9-1.99 2L2 22l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-7 12h-2v-2h2v2zm0-4h-2V6h2v4z"/></svg>
              <span>Support</span>
            </button>
          `);
        }

        // Logout Button inside Sidebar Footer
        footerParts.push(`
          <button class="footer-btn" onclick="AppUI.logout()" title="Logout" style="color:var(--danger);">
            <svg viewBox="0 0 24 24"><path d="M13 3h-2v10h2V3zm4.83 2.17l-1.42 1.42C17.99 7.86 19 9.81 19 12c0 3.87-3.13 7-7 7s-7-3.13-7-7c0-2.19 1.01-4.14 2.58-5.42L6.17 5.17C4.23 6.82 3 9.26 3 12c0 4.97 4.03 9 9 9s9-4.03 9-9c0-2.74-1.23-5.18-3.17-6.83z"/></svg>
            <span>Logout</span>
          </button>
        `);

        footerContainer.innerHTML = footerParts.join("");
      }

      // Populate Mobile Bottom Sheet Menu
      const mobileContent = document.getElementById("mobileMenuContent");
      if (mobileContent) {
        let mobileParts = ROLE_LINKS[role].map(link => {
          return `
            <a href="${link.url}" class="bottom-sheet-link" onclick="toggleMobileMenu()">
              ${link.icon}
              <span>${escapeHtml(link.label)}</span>
            </a>
          `;
        });
        
        mobileParts.push(`
          <a href="#" class="bottom-sheet-link" onclick="toggleMobileMenu(); AppUI.toggleTheme();">
            <svg viewBox="0 0 24 24" id="themeIcon">${themeIcon}</svg>
            <span id="themeText">${isDark ? "Light Mode" : "Dark Mode"}</span>
          </a>
        `);

        if (!isAdminPath) {
          mobileParts.push(`
            <a href="#" class="bottom-sheet-link" onclick="toggleMobileMenu(); AppUI.openSupportModal();">
              <svg viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-1.99.9-1.99 2L2 22l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-7 12h-2v-2h2v2zm0-4h-2V6h2v4z"/></svg>
              <span>Support</span>
            </a>
          `);
        }

        mobileParts.push(`
          <a href="#" class="bottom-sheet-link" style="color:var(--danger);" onclick="toggleMobileMenu(); AppUI.logout();">
            <svg viewBox="0 0 24 24"><path d="M13 3h-2v10h2V3zm4.83 2.17l-1.42 1.42C17.99 7.86 19 9.81 19 12c0 3.87-3.13 7-7 7s-7-3.13-7-7c0-2.19 1.01-4.14 2.58-5.42L6.17 5.17C4.23 6.82 3 9.26 3 12c0 4.97 4.03 9 9 9s9-4.03 9-9c0-2.74-1.23-5.18-3.17-6.83z"/></svg>
            <span>Logout</span>
          </a>
        `);

        mobileContent.innerHTML = mobileParts.join("");
      }
    }

    let navParts = [];
    if (!isAdminPath) {
      navParts.push('<button type="button" class="btn btn-ghost btn-sm" onclick="AppUI.openSupportModal()">Support</button>');
    }
    
    navParts.push(`
      <button class="nav-notification-btn" id="notificationBtn" onclick="AppUI.toggleNotificationSidebar()" style="margin-left: 8px; width: 36px; height: 36px;">
         <svg viewBox="0 0 448 512" class="bell"><path d="M224 0c-17.7 0-32 14.3-32 32V49.9C119.5 61.4 64 124.2 64 200v33.4c0 45.4-15.5 89.5-43.8 124.9L5.3 377c-5.8 7.2-6.9 17.1-2.9 25.4S14.8 416 24 416H424c9.2 0 17.6-5.3 21.6-13.6s2.9-18.2-2.9-25.4l-14.9-18.6C399.5 322.9 384 278.8 384 233.4V200c0-75.8-55.5-138.6-128-150.1V32c0-17.7-14.3-32-32-32zm0 96h8c57.4 0 104 46.6 104 104v33.4c0 47.9 13.9 94.6 39.7 134.6H72.3C98.1 328 112 281.3 112 233.4V200c0-57.4 46.6-104 104-104h8zm64 352H224 160c0 17 6.7 33.3 18.7 45.3s28.3 18.7 45.3 18.7s33.3-6.7 45.3-18.7s18.7-28.3 18.7-45.3z"></path></svg>
         <span id="notificationBadge" style="position: absolute; top: -2px; right: -2px; background: var(--danger); color: white; border-radius: 50%; width: 14px; height: 14px; display: none; align-items: center; justify-content: center; font-size: 0.6rem; font-weight: bold; border: 2px solid white;">0</span>
      </button>
    `);
    
    navParts.push('<button type="button" class="btn btn-danger btn-sm" id="logoutButton" style="margin-left: 8px;">Logout</button>');

    nav.innerHTML = navParts.join("");

    const logoutButton = document.getElementById("logoutButton");
    if (logoutButton) {
      logoutButton.addEventListener("click", logout);
    }
  }

  window.AppUI = {
    clearAuth,
    errorText,
    escapeHtml,
    formatCtc,
    formatDate,
    getRefreshToken,
    getRole,
    getToken,
    logout,
    listResults,
    labelize,
    request,
    requireAuth,
    renderEmpty,
    renderError,
    renderLoading,
    setRole,
    setTokens,
    showToast,
    statusBadge,
    statusClass,
    renderNavbar,
    toggleNotificationSidebar,
    openSupportModal,
    submitSupportRequest,
    toggleSupportView,
    toggleTheme,
    updateThemeUI,
  };

  window.logout = logout;

  document.addEventListener("DOMContentLoaded", function () {
    renderNavbar();
    const currentTheme = document.documentElement.getAttribute("data-theme") || "light";
    updateThemeUI(currentTheme);
  });
})();
