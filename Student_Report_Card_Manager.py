#!/usr/bin/env python3
"""
Student Report Card Manager
---------------------------
A tiny console app that lets you add students, record scores,
see averages & grades, delete records, and save everything to JSON.
"""

import json
from pathlib import Path

DATA_FILE = Path("grades.json")   # change if you want another filename


class Student:
    """Single student with subject‑score pairs."""

    def __init__(self, student_id: int, name: str):
        self.id = student_id             # int, auto‑assigned by GradeManager
        self.name = name.strip()
        self.subjects: dict[str, float] = {}

    # ── score handling ──────────────────────────────────────────────
    def set_score(self, subject: str, score: float) -> None:
        """Add or update a score (0‑100)."""
        if not (0 <= score <= 100):
            raise ValueError("Score must be between 0 and 100.")
        self.subjects[subject.strip()] = score

    # ── calculations ───────────────────────────────────────────────
    def average(self) -> float:
        if not self.subjects:
            return 0.0
        return sum(self.subjects.values()) / len(self.subjects)

    def grade(self) -> str:
        avg = self.average()
        if avg >= 90:
            return "A"
        if avg >= 75:
            return "B"
        if avg >= 50:
            return "C"
        return "Fail"

    # ── JSON helpers ────────────────────────────────────────────────
    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "subjects": self.subjects}

    @classmethod
    def from_dict(cls, data: dict) -> "Student":
        stu = cls(data["id"], data["name"])
        stu.subjects = data.get("subjects", {})
        return stu


class GradeManager:
    """Holds all students and handles persistence."""

    def __init__(self) -> None:
        self.students: list[Student] = []
        self._next_id = 1                # start IDs at 1

    # ── CRUD operations ─────────────────────────────────────────────
    def add_student(self, name: str, scores: dict[str, float]) -> Student:
        stu = Student(self._next_id, name)
        for sub, sc in scores.items():
            stu.set_score(sub, sc)
        self.students.append(stu)
        self._next_id += 1
        return stu

    def find(self, student_id: int) -> Student | None:
        return next((s for s in self.students if s.id == student_id), None)

    def delete(self, student_id: int) -> bool:
        before = len(self.students)
        self.students = [s for s in self.students if s.id != student_id]
        return len(self.students) < before

    # ── file I/O ────────────────────────────────────────────────────
    def save(self, file: Path = DATA_FILE) -> None:
        data = [s.to_dict() for s in self.students]
        file.write_text(json.dumps(data, indent=4))
        print(f"✅ Data saved to {file.resolve()}")

    def load(self, file: Path = DATA_FILE) -> None:
        if not file.exists():
            print("ℹ️  No saved data found. Starting fresh.")
            return
        data = json.loads(file.read_text())
        self.students = [Student.from_dict(d) for d in data]
        if self.students:
            self._next_id = max(s.id for s in self.students) + 1
        print(f"✅ Loaded {len(self.students)} student(s) from {file.resolve()}")


# ────────────────────────── CLI helpers ────────────────────────────
def ask_scores() -> dict[str, float]:
    """Prompt user for subject & score pairs."""
    scores = {}
    while True:
        sub = input("Subject name (or press Enter to finish): ").strip()
        if not sub:
            break
        try:
            sc = float(input(f"Score for {sub}: "))
            scores[sub] = sc
        except ValueError:
            print("⚠️  Enter a number between 0 and 100.")
    return scores


def show_report(stu: Student) -> None:
    """Pretty print a single student's report."""
    print("\n" + "=" * 40)
    print(f" Report for {stu.name} (ID {stu.id})")
    print("-" * 40)
    if not stu.subjects:
        print("  No subjects recorded yet.")
    else:
        for sub, sc in stu.subjects.items():
            print(f"  {sub:<20} {sc:>6.2f}")
    print("-" * 40)
    print(f"  Average: {stu.average():.2f}")
    print(f"  Grade  : {stu.grade()}")
    print("=" * 40 + "\n")


def main() -> None:
    gm = GradeManager()
    gm.load()                        # try to restore previous session

    MENU = """
--- Student Report Card Manager ---
1. Add student
2. Update / add a score
3. View a student's report
4. Delete a student
5. Save data
6. Load data
7. List all students
0. Exit
"""
    try:
        while True:
            print(MENU)
            choice = input("Choose an option: ").strip()

            if choice == "1":
                name = input("Student name: ").strip()
                scores = ask_scores()
                stu = gm.add_student(name, scores)
                print(f"✅ Added {stu.name} with ID {stu.id}")

            elif choice == "2":
                try:
                    sid = int(input("Student ID: "))
                    stu = gm.find(sid)
                    if not stu:
                        print("⚠️  ID not found.")
                        continue
                    subject = input("Subject to change/add: ").strip()
                    score = float(input("New score: "))
                    stu.set_score(subject, score)
                    print("✅ Score updated.")
                except ValueError:
                    print("⚠️  Invalid input.")

            elif choice == "3":
                try:
                    sid = int(input("Student ID: "))
                    stu = gm.find(sid)
                    if stu:
                        show_report(stu)
                    else:
                        print("⚠️  ID not found.")
                except ValueError:
                    print("⚠️  Invalid ID.")

            elif choice == "4":
                try:
                    sid = int(input("Student ID: "))
                    if gm.delete(sid):
                        print("🗑️  Student deleted.")
                    else:
                        print("⚠️  ID not found.")
                except ValueError:
                    print("⚠️  Invalid ID.")

            elif choice == "5":
                gm.save()

            elif choice == "6":
                gm.load()

            elif choice == "7":
                if not gm.students:
                    print("ℹ️  No students yet.")
                else:
                    print("\nCurrent students:")
                    for s in gm.students:
                        print(f"  ID {s.id:>3}: {s.name} ({len(s.subjects)} subjects)")
                    print()

            elif choice == "0":
                gm.save()             # always save on exit
                print("Good-bye!")
                break

            else:
                print("⚠️  Please choose a valid option (0-7).")

    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting gracefully...")
        gm.save()


if __name__ == "__main__":
    main()
