import time
import json

# Constants
dateformat = '%d-%m-%y'
timeformat = '%H:%M:%S'


class School:
	def __init__(self,
				 name: str,
				 classroom_list: list = []):
		self.name = name
		self.classroom_list = classroom_list
		self.created_datetime = time.strftime(f'{dateformat} {timeformat}')

	@property
	def classroom_names(self):
		class_names = []
		for classroom in self.classroom_list:
			class_names.append(classroom.name)
		return class_names

	@property
	def recorder_count(self):
		recorder_count = 0
		for classroom in self.classroom_list:
			recorder_count += len(classroom.attendance_recorders)
		return recorder_count

	def __repr__(self):
		return f'{self.__class__.__name__}({self.name}, {self.classroom_list})'

	def create_classroom(self,
						 name: str,
						 students: dict,
						 attendance_parameters: dict):
		if self.getclass(name) is not None:
			raise Exception('Classroom names can not be the same.')

		new_classroom = Classroom(name, students, attendance_parameters)
		self.classroom_list.append(new_classroom)
		return new_classroom

	def getclass(self,
				 classname:str):
		for classroom in self.classroom_list:
			if classroom.name == classname:
				return classroom
		return None


	def getdata(self):
		name = self.name
		created_datetime = self.created_datetime
		classroom_list = self.classroom_list
		classrooms_data = []
		for classroom in classroom_list:
			classroom_data = classroom.getdata()
			classrooms_data.append(classroom_data)

		data = {'name': name,
				'created_datetime': created_datetime,
				'classrooms_data': classrooms_data}
		return data


	def save(self,
			 filename):
		data = self.getdata()
		with open(filename, 'w') as file:
			json.dump(data, file, indent=4)
		return 0

	@staticmethod
	def load(data):
		name = data['name']
		created_datetime = data['created_datetime']
		classrooms_data = data['classrooms_data']
		classroom_list = []
		for data in classrooms_data:
			classroom_obj = Classroom.load(data)
			classroom_list.append(classroom_obj)

		obj = School(name, classroom_list)

		obj.created_datetime = created_datetime

		return obj

	@staticmethod
	def loadfromfile(filename):
		with open(filename, 'r') as file:
			data = json.load(file)

		obj = School.load(data)

		return obj


class Classroom:
	def __init__(self,
				 name: str,
				 students: dict,
				 attendance_parameters: dict):
		self.name = name
		self.students = students
		self.attendance_parameters = attendance_parameters
		self.attendance_recorders = []

	def __repr__(self):
		repr_syntax = f'{self.__class__.__name__}({self.name}, {self.students}, {self.attendance_parameters})'
		return repr_syntax

	def create_recorder(self,
						subject_name,
						date):
		attendance_recorder = Recorder(subject_name, self, date)
		self.attendance_recorders.append(attendance_recorder)
		return attendance_recorder

	def getrecorders(self,
					 subject_name: str = None,
					 date: str = None,
					 caseInsensitive: bool = False,
					 key: callable = None,
					 reverse: bool = False):
		recorder_list = self.attendance_recorders
		filtered_recorders = []

		if subject_name is None and date is None:
			filtered_recorders = recorder_list

		if subject_name is not None:
			for recorder in recorder_list:
				if caseInsensitive:
					if recorder.subject_name.lower() == subject_name.lower():
						filtered_recorders.append(recorder)
						continue
				if recorder.subject_name == subject_name:
					filtered_recorders.append(recorder)

		if date is not None:
			if filtered_recorders != []:
				recorder_list = filtered_recorders
				filtered_recorders = []

			for recorder in recorder_list:
				if recorder.date == date:
					filtered_recorders.append(recorder)

		if key is not None:
			filtered_recorders = sorted(filtered_recorders, key=key, reverse=reverse)

		return filtered_recorders

	def getdata(self):
		name = self.name
		students = self.students
		attendance_parameters = self.attendance_parameters
		recorders_data = self.get_recorders_data()

		data = {'name': name,
				'students': students,
				'attendance_parameters': attendance_parameters,
				'recorders_data': recorders_data}
		return data

	def get_recorders_data(self):
		recorders_data = []
		for recorder in self.attendance_recorders:
			recorder_data = recorder.getdata()
			recorders_data.append(recorder_data)
		return recorders_data

	def save(self,
			 filename:str):
		data = self.getdata()
		with open(filename, 'w') as file:
			json.dump(data, file, indent=4)

		return 0

	@staticmethod
	def load(data):
		name = data['name']
		students = data['students']
		attendance_parameters = data['attendance_parameters']
		recorders_data = data['recorders_data']

		obj = Classroom(name, students, attendance_parameters)

		for data in recorders_data:
			recorderobj = Recorder.load(data, obj)
			obj.attendance_recorders.append(recorderobj)

		return obj

	@staticmethod
	def loadfromfile(filename):
		with open(filename, 'r') as file:
			data = json.load(file)

		obj = Classroom.load(data)

		return obj


class Recorder:
	def __init__(self,
				 subject_name: str,
				 classroom: Classroom,
				 date: str):
		self.subject_name = subject_name
		self.classroom = classroom
		self.created_datetime = time.strftime(f'{dateformat} {timeformat}')
		self.modified_datetime = time.strftime(f'{dateformat} {timeformat}')
		self.date = date
		self.attendance_record = {}

	@property
	def parameters(self):
		return self.classroom.attendance_parameters

	@property
	def parameter_stats(self):
		parameter_stats = {}
		parameters = self.parameters
		recorded_params = list(self.attendance_record.values())

		for parameter in parameters.keys():
			paramCount = recorded_params.count(parameter)
			parameter_stats[parameter] = paramCount
		return parameter_stats

	@property
	def students(self):
		return self.classroom.students

	@property
	def human_readable(self):
		human_readable = {}

		for studentID, studentParam in self.attendance_record.items():
			student = self.students[studentID]
			parameter = self.parameters[studentParam]
			human_readable.update({student:parameter})
		return human_readable

	def __str__(self):
		return f"{self.__class__.__name__} Object of [{self.subject_name} | {self.date}] " \
			   f"Created on: {self.created_datetime} Last Modified on: {self.modified_datetime}"

	def __repr__(self):
		return f"{self.__class__.__name__}({self.subject_name}, {self.classroom.name}, ({self.date})"

	def load_record(self,
					attendance_record):
		parameters = self.classroom.attendance_parameters
		students = self.classroom.students

		for id, name in students.items():
			if name in attendance_record.keys():
				param = attendance_record.pop(name)
				attendance_record[id] = param

		for entryid, entryparam in attendance_record.items():
			try:
				parameters[entryparam]
				students[entryid]
			except KeyError:
				raise KeyError('Invalid Attendance Record')
		self.attendance_record = attendance_record
		self.modified_datetime = time.strftime(f'{dateformat} {timeformat}')
		return self

	def record(self,
			   attendance_record:dict=None,
			   InterfaceOnly=False,
			   InterfaceStoppers: list = ['stop']):
		if attendance_record is not None:
			return self.load_record(attendance_record)

		parameters = self.classroom.attendance_parameters
		attendance_record = {}

		print('--Attendance Parameters--')
		for param, value in parameters.items():
			print(f'{param} : {value}')
		print('\n')
		for id, name in self.classroom.students.items():
			while True:
				passed_param = input(f'{id}. {name}\nParameter:')
				try:
					if not InterfaceOnly:
						parameters[passed_param]
					data = {str(id): passed_param}
					break
				except KeyError:
					print('\nInvalid Parameter\n\n')
			if InterfaceOnly:
				if passed_param.lower() in [stopper.lower() for stopper in InterfaceStoppers]:
					break
			attendance_record.update(data)

		if not InterfaceOnly:
			if len(attendance_record) == len(self.classroom.students):
				self.attendance_record = attendance_record
				self.modified_datetime = time.strftime(f'{dateformat} {timeformat}')
				print('Successfully Written Attendance Record.')
				return self
		return attendance_record

	def update(self,
			   updater: dict):
		attendance_record = self.attendance_record
		attendance_record.update(updater)
		self.load_record(attendance_record)
		self.modified_datetime = time.strftime(f'{dateformat} {timeformat}')
		return self.attendance_record

	def getdata(self):
		subject_name = self.subject_name
		classroom = str(self.classroom.name)
		created_datetime = self.created_datetime
		modified_datetime = self.modified_datetime
		date = self.date
		attendance_record = self.attendance_record

		data = {'subject_name': subject_name,
				'classroom': classroom,
				'created_datetime': created_datetime,
				'modified_datetime': modified_datetime,
				'date': date,
				'attendance_record': attendance_record}
		return data

	@staticmethod
	def load(data,
			 classroom: Classroom):
		subject_name = data['subject_name']
		classroom = classroom
		created_datetime = data['created_datetime']
		modified_datetime = data['modified_datetime']
		date = data['date']
		attendance_record = data['attendance_record']

		obj = Recorder(subject_name, classroom, date)
		obj.created_datetime = created_datetime
		obj.modified_datetime = modified_datetime
		obj.attendance_record = attendance_record
		return obj


if __name__ == '__main__':
	import pprint

	# Testing Variables
	school_testfile = './test/schooldata.json'
	classroom_testfile = './test/classroomdata.json'

	# Base Variables for classrooms
	test_namelist = "Eldi Forsaken Freddy Kate John".split(' ')
	test_namedict = {str(i+1): name for i, name in enumerate(test_namelist)}
	test_paramdict = {'0': 'Present', '1': 'Alpa', '2': 'Sick', '3': 'Permit'}

	testschool = School('test')
