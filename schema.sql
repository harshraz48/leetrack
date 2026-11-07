USE leetcode_tracker;

CREATE TABLE problems(
    problem_name TEXT NOT NULL,
    leetcode_num INT,
    difficulty TEXT,
    id INTEGER PRIMARY KEY AUTO_INCREMENT
) COMMENT 'table for problems';

CREATE TABLE tags(
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    tag_name TEXT NOT NULL,
    UNIQUE KEY tag_name (tag_name(255))
) COMMENT 'table for tags';

CREATE TABLE problem_tags(
    problem_id INTEGER,
    tag_id INTEGER,
    FOREIGN KEY (problem_id) REFERENCES problems(id),
    FOREIGN KEY (tag_id) REFERENCES tags(id),
    PRIMARY KEY (problem_id, tag_id)
);

CREATE TABLE solutions(
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    problem_id INTEGER,
    FOREIGN KEY (problem_id) REFERENCES problems(id),
    intuition TEXT NOT NULL,
    code TEXT,
    time_taken INT,
    time_complexity TEXT,
    space_complexity TEXT,
    property TEXT,
    need_to_revisit ENUM('yes', 'no') DEFAULT 'no',
    date_solved DATE
);

SHOW TABLES;
