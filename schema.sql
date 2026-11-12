-- ============================================================
-- Kirkuk Emergency Blood Donor Matcher - Database Schema (SQLite)
-- ============================================================
PRAGMA foreign_keys = ON;

CREATE TABLE blood_types (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name  TEXT NOT NULL UNIQUE
);

CREATE TABLE blood_compatibility (
    donor_type_id      INTEGER NOT NULL,
    recipient_type_id  INTEGER NOT NULL,
    PRIMARY KEY (donor_type_id, recipient_type_id),
    FOREIGN KEY (donor_type_id)     REFERENCES blood_types(id),
    FOREIGN KEY (recipient_type_id) REFERENCES blood_types(id)
);

CREATE TABLE districts (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name_ar  TEXT NOT NULL,
    name_en  TEXT NOT NULL
);

CREATE TABLE users (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name      TEXT NOT NULL,
    phone          TEXT NOT NULL UNIQUE,
    email          TEXT UNIQUE,
    password_hash  TEXT NOT NULL,
    role           TEXT NOT NULL CHECK (role IN ('donor', 'hospital', 'admin')),
    is_active      INTEGER NOT NULL DEFAULT 1,
    created_at     TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE donors (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             INTEGER NOT NULL UNIQUE,
    blood_type_id       INTEGER NOT NULL,
    district_id         INTEGER NOT NULL,
    gender              TEXT NOT NULL CHECK (gender IN ('male', 'female')),
    birth_date          TEXT NOT NULL,
    weight_kg           REAL NOT NULL CHECK (weight_kg >= 30),
    last_donation_date  TEXT,
    is_available        INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (user_id)       REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (blood_type_id) REFERENCES blood_types(id),
    FOREIGN KEY (district_id)   REFERENCES districts(id)
);

CREATE TABLE hospitals (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL UNIQUE,
    name         TEXT NOT NULL,
    district_id  INTEGER NOT NULL,
    address      TEXT,
    phone        TEXT,
    is_approved  INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (user_id)     REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (district_id) REFERENCES districts(id)
);

CREATE TABLE blood_requests (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    hospital_id     INTEGER NOT NULL,
    blood_type_id   INTEGER NOT NULL,
    units_needed    INTEGER NOT NULL CHECK (units_needed > 0),
    units_received  INTEGER NOT NULL DEFAULT 0,
    urgency         TEXT NOT NULL DEFAULT 'urgent'
                    CHECK (urgency IN ('critical', 'urgent', 'normal')),
    status          TEXT NOT NULL DEFAULT 'open'
                    CHECK (status IN ('open', 'fulfilled', 'cancelled')),
    notes           TEXT,
    created_at      TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hospital_id)   REFERENCES hospitals(id),
    FOREIGN KEY (blood_type_id) REFERENCES blood_types(id)
);

CREATE TABLE request_matches (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id   INTEGER NOT NULL,
    donor_id     INTEGER NOT NULL,
    status       TEXT NOT NULL DEFAULT 'notified'
                 CHECK (status IN ('notified', 'accepted', 'declined', 'donated')),
    matched_at   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    responded_at TEXT,
    UNIQUE (request_id, donor_id),
    FOREIGN KEY (request_id) REFERENCES blood_requests(id) ON DELETE CASCADE,
    FOREIGN KEY (donor_id)   REFERENCES donors(id)         ON DELETE CASCADE
);

CREATE TABLE donations (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    donor_id    INTEGER NOT NULL,
    hospital_id INTEGER NOT NULL,
    request_id  INTEGER,
    units       INTEGER NOT NULL DEFAULT 1,
    donated_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (donor_id)    REFERENCES donors(id),
    FOREIGN KEY (hospital_id) REFERENCES hospitals(id),
    FOREIGN KEY (request_id)  REFERENCES blood_requests(id)
);

CREATE TABLE notifications (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    message     TEXT NOT NULL,
    is_read     INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_donors_match    ON donors (blood_type_id, is_available, district_id);
CREATE INDEX idx_requests_status ON blood_requests (status, urgency);
CREATE INDEX idx_matches_donor   ON request_matches (donor_id, status);
CREATE INDEX idx_notif_user      ON notifications (user_id, is_read);

INSERT INTO blood_types (id, name) VALUES
 (1,'A+'), (2,'A-'), (3,'B+'), (4,'B-'), (5,'AB+'), (6,'AB-'), (7,'O+'), (8,'O-');

INSERT INTO blood_compatibility (donor_type_id, recipient_type_id) VALUES
 (8,1),(8,2),(8,3),(8,4),(8,5),(8,6),(8,7),(8,8),
 (7,7),(7,1),(7,3),(7,5),
 (2,2),(2,1),(2,6),(2,5),
 (1,1),(1,5),
 (4,4),(4,3),(4,6),(4,5),
 (3,3),(3,5),
 (6,6),(6,5),
 (5,5);

INSERT INTO districts (name_ar, name_en) VALUES
 ('وسط كركوك','Kirkuk Center'), ('رحيم آوه','Rahimawa'), ('واسطي','Wasiti'),
 ('عرفة','Arafa'), ('شورجة','Shorja'), ('الحويجة','Hawija'),
 ('داقوق','Daquq'), ('الدبس','Dibis');
