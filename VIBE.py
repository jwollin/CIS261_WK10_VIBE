
# Jesse Wollin
# CIS261
# VIBE Coding
# Revision: 1.0

"""Student Grade Calculator: manage, calculate, and save student grades."""


from dataclasses import dataclass


FILE_NAME = "student_grades.txt"


@dataclass
class Student:
	"""A student with three test scores and calculated grade information."""

	name: str
	student_id: str
	test1: float
	test2: float
	test3: float

	@property
	def average(self) -> float:
		return (self.test1 + self.test2 + self.test3) / 3

	@property
	def grade(self) -> str:
		if self.average >= 90:
			return "A"
		if self.average >= 80:
			return "B"
		if self.average >= 70:
			return "C"
		if self.average >= 60:
			return "D"
		return "F"

	def to_file_line(self) -> str:
		return (
			f"{self.name}|{self.student_id}|{self.test1:.2f}|"
			f"{self.test2:.2f}|{self.test3:.2f}|{self.average:.2f}|{self.grade}\n"
		)


class StudentRecordManager:
	"""Manage student records and persistence."""

	def __init__(self) -> None:
		self.students: list[Student] = []

	def add(self, student: Student) -> None:
		if any(existing.student_id == student.student_id for existing in self.students):
			raise ValueError("That student ID already exists.")
		self.students.append(student)

	def find_by_name(self, name: str) -> list[Student]:
		search_name = name.casefold()
		return [student for student in self.students if search_name in student.name.casefold()]

	def save(self, file_name: str = FILE_NAME) -> bool:
		try:
			with open(file_name, "w", encoding="utf-8") as file:
				file.writelines(student.to_file_line() for student in self.students)
		except OSError as error:
			print(f"Unable to save records: {error}")
			return False
		return True

	def load(self, file_name: str = FILE_NAME) -> None:
		try:
			with open(file_name, "r", encoding="utf-8") as file:
				for line_number, line in enumerate(file, start=1):
					try:
						fields = line.rstrip("\n").split("|")
						if len(fields) != 7:
							raise ValueError("expected seven pipe-delimited fields")
						name, student_id = fields[0], fields[1]
						scores = [float(value) for value in fields[2:5]]
						if not name or not student_id or any(not 0 <= score <= 100 for score in scores):
							raise ValueError("invalid name, ID, or score")
						self.add(Student(name, student_id, *scores))
					except (ValueError, TypeError) as error:
						print(f"Skipping invalid record on line {line_number}: {error}")
		except FileNotFoundError:
			return
		except OSError as error:
			print(f"Unable to load records: {error}")


def is_exit(value: str) -> bool:
	"""Accept the escape character or the word ESC as an exit command."""
	return value.strip().upper() in {"ESC", "\x1b"}


def read_score(test_number: int) -> float | None:
	while True:
		value = input(f"Test {test_number} score (0-100), or ESC to exit: ")
		if is_exit(value):
			return None
		try:
			score = float(value)
		except ValueError:
			print("Please enter a number from 0 to 100.")
			continue
		if 0 <= score <= 100:
			return score
		print("Score must be between 0 and 100.")


def read_student(manager: StudentRecordManager) -> Student | None:
	name = input("Student name (or ESC to exit): ").strip()
	if is_exit(name):
		return None
	while not name:
		print("Name cannot be blank.")
		name = input("Student name (or ESC to exit): ").strip()
		if is_exit(name):
			return None

	student_id = input("Student ID (or ESC to exit): ").strip()
	if is_exit(student_id):
		return None
	while not student_id:
		print("Student ID cannot be blank.")
		student_id = input("Student ID (or ESC to exit): ").strip()
		if is_exit(student_id):
			return None
	if any(student.student_id == student_id for student in manager.students):
		print("That student ID already exists.")
		return None

	scores: list[float] = []
	for test_number in range(1, 4):
		score = read_score(test_number)
		if score is None:
			return None
		scores.append(score)
	return Student(name, student_id, *scores)


def display_student(student: Student) -> None:
	print(
		f"{student.name:<24} {student.student_id:<12} "
		f"{student.test1:>7.2f} {student.test2:>7.2f} {student.test3:>7.2f} "
		f"{student.average:>8.2f} {student.grade:>5}"
	)


def display_header() -> None:
	print(f"{'Name':<24} {'ID':<12} {'Test 1':>7} {'Test 2':>7} {'Test 3':>7} {'Average':>8} {'Grade':>5}")
	print("-" * 80)


def display_all(manager: StudentRecordManager) -> None:
	if not manager.students:
		print("No student records found.")
		return
	display_header()
	for student in manager.students:
		display_student(student)


def display_statistics(manager: StudentRecordManager) -> None:
	if not manager.students:
		print("No student records available for statistics.")
		return
	highest = max(manager.students, key=lambda student: student.average)
	lowest = min(manager.students, key=lambda student: student.average)
	class_average = sum(student.average for student in manager.students) / len(manager.students)
	print(f"Highest average: {highest.average:.2f} ({highest.name})")
	print(f"Lowest average:  {lowest.average:.2f} ({lowest.name})")
	print(f"Class average:   {class_average:.2f}")


def search_students(manager: StudentRecordManager) -> None:
	name = input("Enter a name to search (or ESC to exit): ").strip()
	if is_exit(name):
		return
	matches = manager.find_by_name(name)
	if not matches:
		print("No matching students found.")
		return
	display_header()
	for student in matches:
		display_student(student)


def run() -> None:
	manager = StudentRecordManager()
	manager.load()
	print("Student Grade Calculator")
	print(f"Loaded {len(manager.students)} student record(s).")

	while True:
		print("\n1. Add student\n2. Display all students\n3. Class statistics\n4. Search by name")
		print("Type ESC at any prompt to save and exit.")
		try:
			choice = input("Choose an option: ")
		except EOFError:
			manager.save()
			print("\nRecords saved. Goodbye.")
			break
		if is_exit(choice):
			manager.save()
			print("Records saved. Goodbye.")
			break
		if choice == "1":
			student = read_student(manager)
			if student is not None:
				manager.add(student)
				print(f"Record added for {student.name}.")
		elif choice == "2":
			display_all(manager)
		elif choice == "3":
			display_statistics(manager)
		elif choice == "4":
			search_students(manager)
		else:
			print("Please choose 1, 2, 3, or 4, or type ESC to exit.")


if __name__ == "__main__":
	run()

