import json
import time

class Converter:
	def __init__(self, schoolname: str = '', classname: str = '', default_created_time: str = ''):
		self.schoolname = schoolname
		self.classname = classname
		self.default_created_time = default_created_time

	def convert_to_recorder(self, data):
		new_data = []

		for subject_name, subject_attendances in data.items():

			for date, attendance in subject_attendances.items():

				attendance = {str(k): str(v) for k, v in attendance.items()}

				recorder_data = {'subject_name': subject_name,
								 'classroom': self.classname,
								 'created_datetime': f'{date} {self.default_created_time}',
								 'modified_datetime': f'{date} {self.default_created_time}',
								 'date': date,
								 'attendance_record': attendance}
				new_data.append(recorder_data)

		return new_data

	def convert_to_classroom(self, data):

		studentlist = data.pop('names')
		reformatted_student = {str(i+1): name for i, name in enumerate(studentlist)}
		attendance_parameters = data.pop('presence')
		recorders_data = self.convert_to_recorder(data)

		new_data = {'name': self.classname,
					'students': reformatted_student,
					'attendance_parameters': attendance_parameters,
					'recorders_data': recorders_data}

		return new_data

	def convert_to_school(self, data):

		classrooms_data = [self.convert_to_classroom(data)]

		new_data = {'name': self.schoolname,
					'created_datetime': time.strftime('%d-%m-%y %H:%M:%S'),
					'classrooms_data': classrooms_data}

		return new_data


def FileLoader(filename):
	with open(filename, 'r') as file:
		data = json.load(file)
	return data


def FileSave(data, filename):
	with open(filename, 'w') as file:
		json.dump(data, file, indent=4)
	return 0


def main():
	old_file = 'old.json'
	new_file = 'new.json'
	print("--Welcome To Data Converter--")
	print("[0]Exit\n[1]Convert To Recorders\n[2]Convert To Classroom\n[3]Convert To School")
	choice = input("Choice:")
	intchoice = int(choice)
	if intchoice == 0:
		exit()
	elif intchoice == 1:
		classname = input('Label Class Name:')
		created_time = input('Created Time[default=HH:MM:SS]:') or 'HH:MM:SS'
		old_file = input('Old File:')
		new_name = input('New File:')
		conv = Converter(classname=classname, default_created_time=created_time)

		new_data = conv.convert_to_recorder(FileLoader(old_file))
		FileSave(new_data, new_name)

	elif intchoice == 2:
		classname = input('Class Name:')
		created_time = input('Created Time[default=HH:MM:SS]:') or 'HH:MM:SS'
		old_file = input('Old File:')
		new_name = input('New File:')
		conv = Converter(classname=classname, default_created_time=created_time)

		new_data = conv.convert_to_classroom(FileLoader(old_file))
		FileSave(new_data, new_name)


	elif intchoice == 3:
		schoolname = input('School Name:')
		classname = input('Class Name:')
		created_time = input('Created Time[default=HH:MM:SS]:') or 'HH:MM:SS'
		old_file = input('Old File:')
		new_name = input('New File:')
		conv = Converter(schoolname=schoolname, classname=classname, default_created_time=created_time)

		new_data = conv.convert_to_school(FileLoader(old_file))
		FileSave(new_data, new_name)


if __name__ == '__main__':
	main()
"""	
	old_file = 'old_attendance_data.json'
	new_file = 'converted_old_data.json'
	conv = Converter('SMPKKKA', '9C', '14:00:00')

	with open(old_file, 'r') as file:
		data = json.load(file)
	newdata = conv.convert_to_classroom(data)
	with open(new_file, 'w') as file:
		json.dump(newdata, file, indent=4)
	print('Done.')
"""
