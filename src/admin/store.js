// Simple localStorage-backed store for demo SOS/Dépannage requests + admin session + user accounts.
// In a real app this would talk to your backend.

const SOS_KEY = "spd_sos_requests";
const DEP_KEY = "spd_dep_requests";
const ADMIN_KEY = "spd_admin_session";
const USERS_KEY = "spd_users";
const SESSION_KEY = "spd_user_session";
const PENDING_KEY = "spd_pending_verifications";
const UPLOADS_KEY = "spd_service_uploads";

function readList(key) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function writeList(key, list) {
  localStorage.setItem(key, JSON.stringify(list));
}

function readObj(key) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

function writeObj(key, obj) {
  localStorage.setItem(key, JSON.stringify(obj));
}

function generateCode() {
  return String(Math.floor(100000 + Math.random() * 900000));
}

export const sosStore = {
  list: () => readList(SOS_KEY),
  add: (entry) => {
    const list = readList(SOS_KEY);
    const newEntry = {
      id: Date.now(),
      createdAt: new Date().toISOString(),
      status: "pending",
      ...entry,
    };
    writeList(SOS_KEY, [newEntry, ...list]);
    return newEntry;
  },
  update: (id, patch) => {
    const list = readList(SOS_KEY).map((e) =>
      e.id === id ? { ...e, ...patch } : e
    );
    writeList(SOS_KEY, list);
  },
  remove: (id) => {
    writeList(
      SOS_KEY,
      readList(SOS_KEY).filter((e) => e.id !== id)
    );
  },
};

export const depStore = {
  list: () => readList(DEP_KEY),
  add: (entry) => {
    const list = readList(DEP_KEY);
    const newEntry = {
      id: Date.now(),
      createdAt: new Date().toISOString(),
      status: "pending",
      ...entry,
    };
    writeList(DEP_KEY, [newEntry, ...list]);
    return newEntry;
  },
  update: (id, patch) => {
    const list = readList(DEP_KEY).map((e) =>
      e.id === id ? { ...e, ...patch } : e
    );
    writeList(DEP_KEY, list);
  },
  remove: (id) => {
    writeList(
      DEP_KEY,
      readList(DEP_KEY).filter((e) => e.id !== id)
    );
  },
};

export const adminAuth = {
  isLoggedIn: () => localStorage.getItem(ADMIN_KEY) === "true",
  login: (email, password) => {
    if (email && password) {
      localStorage.setItem(ADMIN_KEY, "true");
      localStorage.setItem("spd_admin_email", email);
      return true;
    }
    return false;
  },
  logout: () => {
    localStorage.removeItem(ADMIN_KEY);
    localStorage.removeItem("spd_admin_email");
  },
  email: () => localStorage.getItem("spd_admin_email") || "",
};

// ---------- User account store with email verification + password reset ----------

export const userStore = {
  list: () => readList(USERS_KEY),

  register: (userData) => {
    const users = readList(USERS_KEY);
    if (users.find((u) => u.email === userData.email)) {
      return { success: false, error: "Email déjà utilisé" };
    }
    const newUser = {
      id: Date.now(),
      createdAt: new Date().toISOString(),
      verified: false,
      ...userData,
    };
    writeList(USERS_KEY, [...users, newUser]);
    return { success: true, user: newUser };
  },

  // Step 1 of login: verify credentials only. Don't open a session yet.
  checkCredentials: (email, password) => {
    const users = readList(USERS_KEY);
    const user = users.find(
      (u) => u.email === email && u.password === password
    );
    if (!user) return { success: false, error: "Identifiants invalides" };
    return { success: true, user };
  },

  // Generate a 6-digit verification code for a user, save it, return it (so the
  // demo UI can show it; in production you'd email it instead).
  issueCode: (email, reason = "login") => {
    const code = generateCode();
    const pending = readObj(PENDING_KEY);
    pending[email] = {
      code,
      reason, // "signup" | "login" | "reset"
      issuedAt: Date.now(),
    };
    writeObj(PENDING_KEY, pending);
    return code;
  },

  pendingFor: (email) => {
    const pending = readObj(PENDING_KEY);
    return pending[email] || null;
  },

  // Verify a code. On success: opens a session for login/signup, marks signup as verified.
  verifyCode: (email, code) => {
    const pending = readObj(PENDING_KEY);
    const entry = pending[email];
    if (!entry) {
      return { success: false, error: "Aucun code en attente" };
    }
    // 10-minute expiry
    if (Date.now() - entry.issuedAt > 10 * 60 * 1000) {
      delete pending[email];
      writeObj(PENDING_KEY, pending);
      return { success: false, error: "Code expiré" };
    }
    if (entry.code !== code) {
      return { success: false, error: "Code incorrect" };
    }

    // Code is valid — clear it
    delete pending[email];
    writeObj(PENDING_KEY, pending);

    const users = readList(USERS_KEY);
    const idx = users.findIndex((u) => u.email === email);
    if (idx === -1) {
      return { success: false, error: "Utilisateur introuvable" };
    }

    if (entry.reason === "signup") {
      users[idx] = { ...users[idx], verified: true };
      writeList(USERS_KEY, users);
    }

    if (entry.reason === "signup" || entry.reason === "login") {
      localStorage.setItem(SESSION_KEY, JSON.stringify(users[idx]));
    }

    return { success: true, user: users[idx], reason: entry.reason };
  },

  // Used by the reset-password flow.
  resetPassword: (email, code, newPassword) => {
    const v = userStore.verifyCode(email, code);
    if (!v.success && v.error !== "Aucun code en attente") {
      // verifyCode already cleared on success; but if the reason wasn't reset
      // we still want to handle that. Re-check below.
    }
    // Above call already cleared the pending entry. We need a different path:
    // re-issue: instead, do the check inline here without clearing first.

    const pending = readObj(PENDING_KEY);
    const entry = pending[email];
    if (!entry || entry.reason !== "reset") {
      return { success: false, error: "Aucun code de réinitialisation" };
    }
    if (Date.now() - entry.issuedAt > 10 * 60 * 1000) {
      delete pending[email];
      writeObj(PENDING_KEY, pending);
      return { success: false, error: "Code expiré" };
    }
    if (entry.code !== code) {
      return { success: false, error: "Code incorrect" };
    }

    const users = readList(USERS_KEY);
    const idx = users.findIndex((u) => u.email === email);
    if (idx === -1) {
      return { success: false, error: "Utilisateur introuvable" };
    }

    users[idx] = { ...users[idx], password: newPassword };
    writeList(USERS_KEY, users);

    delete pending[email];
    writeObj(PENDING_KEY, pending);

    return { success: true };
  },

  emailExists: (email) => {
    return readList(USERS_KEY).some((u) => u.email === email);
  },

  getCurrentUser: () => {
    try {
      const session = localStorage.getItem(SESSION_KEY);
      return session ? JSON.parse(session) : null;
    } catch {
      return null;
    }
  },

  setCurrentUser: (user) => {
    localStorage.setItem(SESSION_KEY, JSON.stringify(user));
  },

  logout: () => {
    localStorage.removeItem(SESSION_KEY);
  },
};
