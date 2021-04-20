import platform
from os import system as shexec
import json
import time
from utils import pause

import attendance


ConfigFile = './config.json'
mainMenuLen = 30
attendance.dateformat

def classroomConstructor(constructorData: dict,
						 filename: str):
	className = constructorData['class_name']
	students_file = constructorData['students_file']
	attendance_parameters = constructorData['attendance_parameters']

	try:
		with open(students_file, 'r') as file:
			students = json.load(file)
			if not isinstance(students, dict):
				raise json.decoder.JSONDecodeError
	except json.decoder.JSONDecodeError:
		print('Students NameFile Not Valid. Using Name Dictionary Generator...')
		with open(students_file, 'r') as file:
			students_list = file.read().splitlines()

			# generator for students dictionary
			students = {str(i): name for i, name in enumerate(students_list)}
		print('Students Name Dictionary Generated.\n')

	classroom = attendance.Classroom(name=className, students=students, attendance_parameters=attendance_parameters)
	recorders = [str(recorder) for recorder in classroom.getrecorders()]

	classroomInfo(classroom, detailed=True, clearscreen=False)
	print('\nSaving Classroom data to designated file...')
	classroom.save(filename)
	print('Classroom Saved.')
	return classroom


def loadConfig(ConfigFile: str):
	with open(ConfigFile, 'r') as file:
		config = json.load(file)
	globals()['config'] = config
	globals()['databaseFile'] = config['database_filename']
	globals()['subject_list'] = config['subject_list'].split(', ')
	try:
		classroom = attendance.Classroom.loadfromfile(databaseFile)
		globals()['classroom'] = classroom
	except:
		print('Classroom file does not exist.')
		print('Creating Classroom With Classroom Constructor Values...')
		classroom = classroomConstructor(config['classroom_constructor'], config['database_filename'])
		globals()['classroom'] = classroom
		print('Loaded Classroom.')
		pause(wait_cycle=10, NoInput=True)
	return classroom

#loadConfig(ConfigFile)

clear_cmd = "cls" if platform.system() == "Windows" else "clear"
def clearScreen():
	shexec(clear_cmd)


def currdate():
	return time.strftime(attendance.dateformat)


def saveData(school: attendance.School = None,
			 classroom: attendance.Classroom = None):
	if school is not None:
		school.save(databaseFile)
	if classroom is not None:
		classroom.save(databaseFile)


def record(classroom:attendance.Classroom,
		   subject_name, date=None):
	recorder = classroom.create_recorder(subject_name=subject_name, date=currdate() or date)
	recorder.record()
	saveData(classroom)
	return classroom


def edit(classroom:attendance.Classroom,
		 recorder:attendance.Recorder):
	print(f"""
	Updating {recorder.subject_name} Recorder
	Press Enter to skip an entry.
	Enter [Stop] or [S] to end entering parameters.
""".replace('\t', ''))
	data = recorder.record(InterfaceOnly=True, InterfaceStoppers=['stop', 's'])
	data = {id:param for id, param in data.items() if param != ''}
	recorder.update(data)
	saveData(classroom)
	return recorder


def formatter(recorder:attendance.Recorder,
			  detailed = False):
	subject = recorder.subject_name
	date = recorder.date

	entries = recorder.human_readable
	paramStats = recorder.parameter_stats
	paramStats = {recorder.parameters[param]: paramCount
				  for param, paramCount in paramStats.items()
				  if paramCount > 0}


	maxlen_student = len(max(recorder.students.values(), key=len))
	maxlen_param = len(max(paramStats, key=paramStats.get))
	formatting_len = maxlen_student + len(' | ') + maxlen_param + 4

	formatted_borders = f"{'':_<{formatting_len}}"
	formatted_splitter = f"{'':-<{formatting_len}}"

	formatted_strings = ['',formatted_borders,
						 f"{f'Showing [{subject}] Recorder On {date}':-^{formatting_len}}"]

	for name, param in entries.items():
		formatted_strings += [f"""{f"{name:^{maxlen_student}} | {param:<{maxlen_param}}":<{formatting_len}}"""]

	formatted_strings += [formatted_splitter,
						  f"{'Statistics':^{formatting_len}}"]

	formatted_strings += [f"{f'{param} : {paramCount}':^{formatting_len}}" for param, paramCount in paramStats.items()]

	formatted_strings += [formatted_borders]

	if detailed:
		formatted_strings += [f"Created on       : {recorder.created_datetime}",
							  f"Last Modified On : {recorder.modified_datetime}",
							  f"Recorder Repr    : {recorder}"]

	formatted_string = "\n".join(formatted_strings)

	return formatted_string


def Timestamp(datetime: str = None,
			  date: str = None,
			  time: str = None):
	datefmt = attendance.dateformat.split('-')
	timefmt = attendance.timeformat.split(':')

	fmtIdx = lambda format, val: format.index(val)

	timestamp = 0
	consts = {'sec': 1, 'min': 60, 'hour': 3600, 'day': 86400, 'month': 2629743, 'year': 31556926}

	datetimedict = {}

	calc = lambda datetime, consts: sum([int(datetime[key])*int(consts[key]) for key in datetime.keys()])

	if datetime is not None:
		date, time = datetime.split(' ')

	if date is not None:
		date = date.split('-', 2)
		dateVal = lambda fmtPlaceholder: date[fmtIdx(datefmt, fmtPlaceholder)]
		datetimedict.update({'day': dateVal('%d'), 'month': dateVal('%m'), 'year': dateVal('%y')})

	if time is not None:
		time = time.split(':', 2)
		timeVal = lambda fmtPlaceholder: time[fmtIdx(timefmt, fmtPlaceholder)]
		datetimedict.update({'hour': timeVal('%H'), 'min': timeVal('%M'), 'sec': timeVal('%S')})

	return calc(datetimedict, consts)


def view(classroom:attendance.Classroom,
		 subject_name=None,
		 date=None,
		 detailed=False):
	recorders = classroom.getrecorders(subject_name,
									   date,
									   caseInsensitive=config['view_caseinsensitive'],
									   key=lambda recorder:Timestamp(datetime=recorder.created_datetime))
	recorders_output = [formatter(recorder, detailed=detailed) for recorder in recorders]
	formatted_output = "\n\n".join(recorders_output)
	print("\n" + formatted_output + "\n\n")
	return


def help(cmd=None):
	clearScreen()
	if not cmd:
		print(f"""
			--Help Menu--
			[R|RC]Record
			[V|VD|VC|VCD]View
			[E|EC]Edit
			[I|ID]Classroom Information
			[C]Config Information
			[H]Help
			[X]Exit

			Subcommands:
			C | Custom
			D | Detailed

			Examples:
			Syntax: R1
			Effect:  Would Initiate A Record Of The Subject [{subject_list[0]}] On Today's Date.

			Syntax: V1
			Effect: Would Initiate A View Action Of All The Subject [{subject_list[0]}] Records.

			Syntax: V1 <Date Format: {attendance.dateformat} Ex: {currdate()}>
			Effect: Would Initiate A View Action On The Subject [{subject_list[0]}] Record On The Specified Date.

			Syntax: E1 <Date Format: {attendance.dateformat} Ex: {currdate()}>
			Effect: Would Initiate An Edit Action On The Subject [{subject_list[0]}] On The Specified Date.

			Syntax: VC <Date Format: {attendance.dateformat} Ex: {currdate()}> <Subjectname>
			Effect: Initiate View Action With The Given Date or Subjectname or Both.
			        It's case-insensitivity can be changed in the config file.

			Syntax: ID
			Effect: Shows The Classroom Informations In Detail.
		""".strip('\n').replace('\t', ''))
		return


def classroomInfo(classroom:attendance.Classroom,
				  detailed=False,
				  clearscreen=True):
	clearScreen() if clearscreen else None
	recorders = [str(recorder) for recorder in classroom.getrecorders()]

	ClassroomInformations = f"""
-- Classroom Information --

Classroom Name: {classroom.name}

{f"Classroom Students: {list(classroom.students.values())}" if detailed else ''}
Classroom Student Count: {len(classroom.students.values())}

{f"Classroom Recorders: {recorders}" if detailed else ''}
Classroom Recorder Count: {len(recorders)}


Classroom Attendance Parameters: {classroom.attendance_parameters}

{"[I D] For more information." if not detailed else ''}
""".strip('\n')
	print(ClassroomInformations)
	return


def configInfo(clearscreen=True):
	clearScreen() if clearscreen else None
	configInformations = f"""
-- Configurations --

Configuration File: {ConfigFile}

Configurations:
  Database File: {config['database_filename']}
  Subject List : {config['subject_list']}
  View Case Insensitive : {config['view_caseinsensitive']}
  {f'''Classroom Constructor:
    {f"Class Name: {config['classroom_constructor']['class_name']}"}
    {f"Student Name List File: {config['classroom_constructor']['students_file']}"}
    {f"Attendance Parameters: {config['classroom_constructor']['attendance_parameters']}"}
''' if config.get('classroom_constructor') is not None else 'Classroom Constructor: Not Defined'}
""".strip('\n')

	print(configInformations)
	return


def datefmt(date: str):
	if date is not None:
		try:
			int(date)
			date = "-".join([date[0:2], date[2:4], date[4:6]])
		except:
			seperators = [' ', '/', '\\', '.']
			for seperator in seperators:
				date = date.replace(seperator, '-')
		return date


def verifyDate(candidate):
	try:
		candidate = datefmt(candidate)
		candidateObj = time.strptime(candidate, attendance.dateformat)
		return True
	except ValueError:
		return False


def verifyDates(candidates):
	result = {}
	for candidate in candidates:
		try:
			candidate = datefmt(candidate)
			candidateObj = time.strptime(candidate, attendance.dateformat)
			result[candidate] = True
		except ValueError:
			result[candidate] = False

	return result


def mainClass(classroom:attendance.Classroom):
	while True:
		clearScreen()
		print(f'{"Attendance Main Menu":-^{mainMenuLen}}')
		print(f'{f"[Classroom {classroom.name}]":^{mainMenuLen}}\n')
		for i, subject in enumerate(subject_list):
			print(f"[{i+1}]{subject}")
		print('\n[H]Help and [X]Exit')
		inp = input('Choice:')
		try:
			choice, param = inp.split(' ', 1)
			choice = choice.upper()
		except ValueError:
			choice = inp.upper()
			param = ''
		try:
			if choice.startswith('R'):
				if choice[1:].startswith('C'):
					print("\n-- Custom Record --")
					subject = input("Subject Name:")
					date = input("Date:")
					print(f"\n Taking Custom Attendance For {subject}")
					record(classroom, subject_name=subject, date=date)
				else:
					print(f"Taking attendance for {subject_list[int(choice[1:])-1]}\n")
					record(classroom, subject_list[int(choice[1:])-1])
				input("\nPress enter to return.")

			elif choice.startswith('V'):
				detailed = True if 'D' in choice else False

				if len(choice) == 1 or (len(choice) == 2 and choice[1:].startswith('D')):
					param = None if param in ['', ' '] else param
					view(classroom, date=datefmt(param), detailed=detailed)
					input("Press enter to return.")
					continue
				subjectChooser = choice[1:] if choice[1] not in ['D', 'C'] else choice[2:]

				if 'C' in choice:
					subjectname, date = param, None
					try:
						subjectname, date = param.split(' ', 1)
					except ValueError:
						if verifyDate(param):
							date = param
					view(classroom, subject_name=subjectname, date=datefmt(date), detailed=detailed)

				else:
					param = None if param in ['', ' '] else param
					view(classroom, subject_list[int(subjectChooser)-1], datefmt(param), detailed=detailed)
				input("Press enter to return.")

			elif choice.startswith('E'):
				try:
					recorder = classroom.getrecorders(subject_name=subject_list[int(choice[1:])-1], date=datefmt(param))[0]
					recorder = edit(classroom, recorder)
					print("\nSuccessfully Updated Record.\n")
					print(formatter(recorder))
				except ValueError:
					if 'C' in choice:
						subjectname, date = param, None
						try:
							subjectname, date = param.split(' ', 1)
						except ValueError:
							if verifyDate(param):
								date = param
						recorder = classroom.getrecorders(subject_name=subjectname, date=datefmt(date))[0]
						recorder = edit(classroom, recorder)
						print("\nSuccessfully Updated Record.\n")
						print(formatter(recorder))
				except IndexError:
					print("No Recorder Found.")
				input("Press enter to return.")

			elif choice.startswith('I'):
				detailedKeywords = ['D', 'DET', 'DETAIL','DETAILED']
				detailed = True if choice[1:].upper() in detailedKeywords else False
				detailed = True if param.upper() in detailedKeywords else detailed
				classroomInfo(classroom, detailed=detailed)
				input("Press enter to return.")

			elif choice in ['C', 'CI', 'CONFIG']:
				configInfo()
				input("Press enter to return.")

			elif choice in ['H', 'HELP']:
				help(param)
				input("Press enter to return.")

			elif choice in ['X', 'EXIT', '0']:
				break
			else:
				pass
		except UnboundLocalError:
			print("Please Input Required Parameters.")
		except ValueError:
			pass
	return classroom


if __name__ == '__main__':
	import sys
	try:
		if sys.argv[1].lower() == 'test':
			ConfigFile='./test/config.json'
	except IndexError:
		pass
	finally:
		del sys

	loadConfig(ConfigFile)
	mainClass(classroom)
