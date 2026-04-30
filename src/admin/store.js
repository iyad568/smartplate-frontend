// Simple localStorage-backed store for demo SOS/Dépannage requests + admin session + user accounts.
// In a real app this would talk to your backend.

const SOS_KEY = "spd_sos_requests";
const DEP_KEY = "spd_dep_requests";
const ADMIN_KEY = "spd_admin_session";
const USERS_KEY = "spd_users";
const SESSION_KEY = "spd_user_session";

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
    // Demo gate — accept anything non-empty.
    // Replace with a real backend check when wiring up.
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

// User account store
export const userStore = {
  list: () => readList(USERS_KEY),
  register: (userData) => {
    const users = readList(USERS_KEY);
    // Check if email already exists
    if (users.find((u) => u.email === userData.email)) {
      return { success: false, error: "Email already exists" };
    }
    const newUser = {
      id: Date.now(),
      createdAt: new Date().toISOString(),
      ...userData,
    };
    writeList(USERS_KEY, [...users, newUser]);
    return { success: true, user: newUser };
  },
  authenticate: (email, password) => {
    const users = readList(USERS_KEY);
    const user = users.find((u) => u.email === email && u.password === password);
    if (user) {
      localStorage.setItem(SESSION_KEY, JSON.stringify(user));
      return { success: true, user };
    }
    return { success: false, error: "Invalid credentials" };
  },
  getCurrentUser: () => {
    try {
      const session = localStorage.getItem(SESSION_KEY);
      return session ? JSON.parse(session) : null;
    } catch {
      return null;
    }
  },
  logout: () => {
    localStorage.removeItem(SESSION_KEY);
  },
};
