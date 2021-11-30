import platform
from os import system as shexec
import json
import time
from utils import Pause

import attendance


ConfigFile = './config.json'
mainMenuLen = 30

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


def loadConfig(ConfigFile: str, databaseFileOverrider=None):
	with open(ConfigFile, 'r') as file:
		config = json.load(file)
	config = config

	# Set Database Filename
	if databaseFileOverrider is not None:
		config['database_filename'] = databaseFileOverrider

	# Convert Subject List Into List
	config['subject_list'] = config['subject_list'].split(', ')

	# Create A Classroom Object
	try:
		classroom = attendance.Classroom.loadfromfile(config['database_filename'])
	except:
		print('Classroom file does not exist.\n'
			  'Creating Classroom With Classroom Constructor Parameters...')
		classroom = classroomConstructor(config['classroom_constructor'], config['database_filename'])
		print('Loaded Classroom.')
		Pause(waitMultiplier=10, waitOnly=True)
	return config, classroom


class Input:
	def __init__(self,
				 InputString: str = '',
				 CommandForceUppercase: bool = False):
		self.string = InputString
		self.Elements = self.Parser(CommandForceUppercase)
		self.Elements['subject_name'] = self.subject_name

	def __str__(self):
		return f"{self.__class__.__name__} Object. String: {self.string}, Elements: {self.Elements}"

	def __repr__(self):
		return f"{self.__class__.__name__}({self.string})"

	@property
	def subject_name(self):
		return " ".join(self.Elements['subject_names']) if len(self.Elements['subject_names']) > 0 else None

	def Parser(self,
			   CommandForceUppercase: bool = False):
		Elements = {}
		words = self.string.split(' ')

		while not len(words) >= 3:
			words.append('')


		command = words[0]
		parameters = [word for word in words[1:] if len(word) > 0]
		DateVerifyRes = verifyDates(parameters)
		DateVerified = [date for date, verified in verifyDates(parameters).items() if verified]
		SubjectNames = [date for date, verified in verifyDates(parameters).items() if not verified and len(date) > 0]

		if CommandForceUppercase:
			command = command.upper()

		# Reassigning Variables
		Elements['words'] = [word for word in words[1:] if len(word) > 0]
		Elements['command'] = command
		Elements['parameters'] = parameters
		Elements['dates'] = DateVerified
		Elements['date'] = list(DateVerified+[None])[0]
		Elements['subject_names'] = SubjectNames
		#Elements['subject_name'] = self.subject_name
		#Elements['subject_name'] = " ".join(SubjectNames) if len(SubjectNames) > 0 else None
		return Elements

	@staticmethod
	def Get(prompt: str = '',
			CommandForceUppercase: bool = False):
		InputString = input(prompt)
		InputObj = Input(InputString,
						 CommandForceUppercase=CommandForceUppercase)
		return InputObj


def testInputClass(inputVals: list[str],
				   exitAfter: bool = False):
	for inputVal in inputVals:
		e = Input(inputVal)
		print(f"----\nInput: {inputVal}\n\nInput Object: {e}\nInput.Elements: {e.Elements}\n")
	if exitAfter:
		exit()


clear_cmd = "cls" if platform.system() == "Windows" else "clear"
def clearScreen():
	shexec(clear_cmd)


def currDate():
	return time.strftime(attendance.DATE_FORMAT)


def saveData(school: attendance.School = None,
			 classroom: attendance.Classroom = None,
			 filename: str = 'data.json'):
	if school is not None:
		school.save(filename)
	if classroom is not None:
		classroom.save(filename)


def record(config: dict,
		   classroom: attendance.Classroom,
		   Input: Input,
		   SubjectFromList: bool = False):
	if SubjectFromList:
		subject_name = config['subject_list'][int(Input.Elements['command'][1:])-1]
	else:
		subject_name = Input.Elements['subject_name']
	recorder = classroom.create_recorder(subject_name = subject_name,
										 date=currDate() or Input.Elements['date'])
	recorder.record()
	saveData(classroom=classroom, filename=config['database_filename'])
	return classroom


def edit(config: dict,
		 classroom: attendance.Classroom,
		 recorder: attendance.Recorder):
	print(f"""
Updating {recorder.subject_name} Recorder
Press Enter to skip an entry.
Enter [Stop] or [S] to end entering parameters.
""")
	data = recorder.record(InterfaceOnly=True, InterfaceStoppers=['stop', 's'])
	data = {id:param for id, param in data.items() if param != ''}
	recorder.update(data)
	saveData(classroom=classroom, filename=config['database_filename'])
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
	dateFmt = attendance.DATE_FORMAT.split('-')
	timefmt = attendance.TIME_FORMAT.split(':')

	fmtIdx = lambda format, val: format.index(val)

	timestamp = 0
	consts = {'sec': 1, 'min': 60, 'hour': 3600, 'day': 86400, 'month': 2629743, 'year': 31556926}

	datetimedict = {}

	calc = lambda datetime, consts: sum([int(datetime[key])*int(consts[key]) for key in datetime.keys()])

	if datetime is not None:
		date, time = datetime.split(' ')

	if date is not None:
		date = date.split('-', 2)
		dateVal = lambda fmtPlaceholder: date[fmtIdx(dateFmt, fmtPlaceholder)]
		datetimedict.update({'day': dateVal('%d'), 'month': dateVal('%m'), 'year': dateVal('%y')})

	if time is not None:
		time = time.split(':', 2)
		timeVal = lambda fmtPlaceholder: time[fmtIdx(timefmt, fmtPlaceholder)]
		datetimedict.update({'hour': timeVal('%H'), 'min': timeVal('%M'), 'sec': timeVal('%S')})

	return calc(datetimedict, consts)


def view(config: dict,
		 classroom:attendance.Classroom,
		 Input: Input,
		 detailed: bool = False,
		 SubjectFromList: bool = False):

	if SubjectFromList:
		try:
			subject_name = config['subject_list'][int(Input.Elements['command'][1:])-1]
		except ValueError:
			subject_name = config['subject_list'][int(Input.Elements['command'][2:])-1]
	else:
		subject_name = Input.Elements['subject_name']

	recorders = classroom.getrecorders(subject_name = subject_name,
									   date = Input.Elements['date'],
									   caseInsensitive=config['case-insensitive'],
									   key = lambda recorder:Timestamp(datetime=recorder.created_datetime))
	recorders_output = [formatter(recorder, detailed=detailed) for recorder in recorders]
	formatted_output = "\n\n".join(recorders_output)
	print("\n" + formatted_output + "\n\n")
	return


def export(classroom: attendance.Classroom):
	data = classroom.getdata()
	dataStr = json.dumps(data)
	print("-- Export Classroom --")
	print(f"Classroom Name: {data['name']}\nClassroom Data length: {len(dataStr)}")
	filename = input("Export To (Extension Will Be Appended): ") + '.json'
	confirmation = True if input("Confirm Export?\nChoice(Y/N): ").upper() in ['Y', 'YE', 'YES'] else False
	if confirmation:
		classroom.save(filename)
		print("File Exported.")
	else:
		print("Export Action Invalidated.")


def statistics(config: dict,
			   classroom: attendance.Classroom,
			   Input: Input,
			   blacklistedParameters: list[str] = ['No Class'],
			   ReverseSortOrder: bool = True,
			   SubjectFromList: bool = False):

	st = time.time()

	if SubjectFromList:
		subject_name = config['subject_list'][int(Input.Elements['command'][1:])-1]
	else:
		subject_name = Input.Elements['subject_name']

	blacklistedParameters = [p.lower() for p in blacklistedParameters]
	recorders = classroom.getrecorders(subject_name=subject_name,
									   key=lambda recorder:Timestamp(datetime=recorder.created_datetime),
									   caseInsensitive=config['case-insensitive'])
	attendances = [recorder.human_readable for recorder in recorders]
	students = [name for name in classroom.students.values()]
	parameters = [name for name in classroom.attendance_parameters.values() if name.lower() not in blacklistedParameters]

	statistics = {}
	sortedBy = {}

	for record in attendances:
		for name, parameter in record.items():
			if parameter.lower() in blacklistedParameters:
				continue
			statistics[name] = statistics.get(name, {p: 0 for p in parameters})
			statistics[name][parameter] += 1

	#import pprint
	#pprint.pprint(statistics)

	SortableStatistics = [{'name':name, 'attendance_record': attendance} for name, attendance in statistics.items()]
	for parameter in parameters:
		sortedBy[parameter] = sorted(SortableStatistics,
									 key=lambda x: x['attendance_record'][parameter],
									 reverse=ReverseSortOrder)

	#pprint.pprint(sortedBy)
	#print("Time Elapsed:", round(time.time()-st, 5))

	return statistics, sortedBy


def viewStats(config: dict,
			  classroom: attendance.Classroom,
			  Input: Input,
			  blacklistedParameters: list[str] = ['No Class'],
			  SubjectFromList: bool = False):

	attendanceKeys = list(classroom.attendance_parameters.keys())
	sortParameterKey = 1


	for param in Input.Elements['parameters']:
		if param in attendanceKeys:
			sortParameterKey = param
			Input.Elements['words'].remove(param)
			Input.Elements['subject_names'].remove(param+'--')
			Input.Elements['subject_name'] = Input.subject_name

	sortParameter = classroom.attendance_parameters[str(sortParameterKey)]

	recorderCount = len(classroom.attendance_recorders)

	if recorderCount <= 0:
		return print("No recorders in database, Cannot create statistics.")

	rawstat, sortedstats = statistics(config=config,
									  classroom=classroom,
									  Input=Input,
									  blacklistedParameters=config['statistics_blacklisted_attendance_parameters'],
									  ReverseSortOrder=config['reverse_sorted_statistics'],
									  SubjectFromList=SubjectFromList)
	stat = sortedstats[sortParameter]

	maxlen_student = len(max(classroom.students.values(), key=len)) + 4

	rside = f"{recorderCount:>{len(str(recorderCount))}}/{recorderCount} {round((recorderCount/recorderCount) * 100, 2)}%"
	formatting_len = maxlen_student + len(' | ') + len(rside)

	formatted_strings = [f"{'':_<{formatting_len}}",
						 f"{f'Statistics Sorted By [{sortParameter}]':-^{formatting_len}}"]

	for rank, student in enumerate(stat):
		count = student['attendance_record'][sortParameter]
		percentage = round((count/recorderCount) * 100, 2)
		rside = f"{count:>{len(str(recorderCount))}}/{recorderCount} {percentage}%"
		formatted_strings += [f"""{f'{rank+1}. {student["name"]}':<{maxlen_student}} | {rside}"""]

	formatted_strings += [f"{'':_<{formatting_len}}"]

	formatted_string = "\n".join(formatted_strings)
	print(formatted_string + "\n")
	return


def help(config: dict,
		 detailed = False):
	clearScreen()
	subject_list = config['subject_list']

	helpstr = f"""
--Help Menu--
[R|RC]Record
[V|VD|VC|VCD]View
[E|EC]Edit
[EX]Export
[S|SC]Statistics
[I|ID]Classroom Information
[C]Config Information
[H|HD]Help
[X]Exit

Subcommands:
C | Custom
D | Detailed
	""".strip("\n")
	if detailed:
		helpstr += f"""

Examples:
Syntax: R1
Effect: Would Initiate A Record Of The Subject [{subject_list[0]}] On Today's Date.

Syntax: RC <Subject Name> <Date Format: {attendance.DATE_FORMAT} Ex: {currDate()}>
Effect: Would Initiate A Record Of The Given Subject On The Given Date. 

Syntax: V1
Effect: Would Initiate A View Action Of All The Subject [{subject_list[0]}] Records.

Syntax: V1 <Date Format: {attendance.DATE_FORMAT} Ex: {currDate()}>
Effect: Would Initiate A View Action On The Subject [{subject_list[0]}] Record On The Specified Date.

Syntax: E1 <Date Format: {attendance.DATE_FORMAT} Ex: {currDate()}>
Effect: Would Initiate An Edit Action On The Subject [{subject_list[0]}] On The Specified Date.

Syntax: VC <Date Format: {attendance.DATE_FORMAT} Ex: {currDate()}> <Subjectname>
Effect: Initiate View Action With The Given Date or Subjectname or Both.
        It's case-insensitivity can be changed in the config file.

Syntax: EX
Effect: Given Prompt Asking For Filename And Saves It If Confirmed.

Syntax: S
Effect: Shows A Ranking Statistics Of The Students Across The Recorders.

Syntax: S1
Effect: Shows A Ranking Statistics Of The First Listed Subject In subject_list. (Percentage Compared Across All Recorders)

Syntax: SC <Optional: Subject Name> <Optional: Parameter>
Effect: Shows A Ranking Statistics Of The Given Subject On The Given Parameter. (Percentage Compared Across All Recorders)

Syntax: ID
Effect: Shows The Classroom Informations In Detail.
		""".rstrip('\n')
	helpstr += "\n[HD] For Examples."

	print(helpstr)
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

{"[ID] For detailed information." if not detailed else ''}
""".strip('\n')
	print(ClassroomInformations)
	return


def configInfo(config: dict,
			   clearscreen = True):
	clearScreen() if clearscreen else None
	configInformations = f"""
-- Configurations --

Configuration File: {ConfigFile}

Configurations:
  Database File: {config['database_filename']}
  Subject List : {config['subject_list']}
  Global Search Case Insensitive : {config['case-insensitive']}
  Reverse Sorted Statistics : {config['reverse_sorted_statistics']}
  Statistiscs Blacklisted Attendance Parameters : {config['statistics_blacklisted_attendance_parameters']}
  {f'''Classroom Constructor:
    {f"Class Name: {config['classroom_constructor']['class_name']}"}
    {f"Student Name List File: {config['classroom_constructor']['students_file']}"}
    {f"Attendance Parameters: {config['classroom_constructor']['attendance_parameters']}"}
''' if config.get('classroom_constructor') is not None else 'Classroom Constructor: Not Defined'}
""".strip('\n')
	print(configInformations)
	return


def dateFmt(date: str):
	if date is not None:
		try:
			int(date)
			date = "-".join([date[0:2], date[2:4], date[4:6]])
		except:
			seperators = [' ', '/', '\\', '.']
			for seperator in seperators:
				date = date.replace(seperator, '-')
		return date


def verifyDate(candidate: str):
	try:
		candidate = dateFmt(candidate)
		candidateObj = time.strptime(candidate, attendance.DATE_FORMAT)
		return True
	except ValueError:
		return False


def verifyDates(candidates: list[str]):
	result = {}
	for candidate in candidates:
		try:
			candidate = dateFmt(candidate)
			candidateObj = time.strptime(candidate, attendance.DATE_FORMAT)
			result[candidate] = True
		except ValueError:
			result[candidate] = False
	return result


def mainClass(config: dict,
			  classroom: attendance.Classroom):

	subject_list = config['subject_list']

	getCmd = lambda InpObj: InpObj.Elements['command']


	while True:
		clearScreen()
		print(f'{"Attendance Main Menu":-^{mainMenuLen}}')
		print(f'{f"[Classroom {classroom.name}]":^{mainMenuLen}}\n')
		for i, subject in enumerate(subject_list):
			print(f"[{i+1}]{subject}")
		print('\n[H]Help and [X]Exit')
		inp = Input.Get('Choice:', CommandForceUppercase=True)

		cmd = getCmd(inp)

		try:

			if cmd in ['EX', 'EXPORT']:
				export(classroom)
				input("Press enter to return.")

			elif cmd.startswith('R'):
				if 'C' in cmd:
					if inp.Elements['date'] is None:
						inp.Elements['date'] = currDate()
					print(f"\n Taking Custom Attendance For {inp.Elements['subject_name']} On {inp.Elements['date']}")
					record(config=config,
						   classroom=classroom,
						   Input=inp)
				else:
					print(f"Taking attendance for {subject_list[int(cmd[1:])-1]}\n")
					record(config=config,
						   classroom=classroom,
						   Input=inp,
						   SubjectFromList=True)
				input("\nPress enter to return.")

			elif cmd.startswith('V'):
				detailed = True if 'D' in cmd else False
				SubjectFromlist = True

				if len(cmd) == 1 or (len(cmd) == 2 and detailed):
					SubjectFromlist = False

				if 'C' in cmd:
					SubjectFromlist = False

				view(config=config,
					 classroom=classroom,
					 Input=inp,
					 detailed=detailed,
					 SubjectFromList=SubjectFromlist)
				input("\nPress enter to return.")

			elif cmd.startswith('E'):
				try:
					recorder = classroom.getrecorders(subject_name=subject_list[int(cmd[1:])-1],
													  date=inp.Elements['date'])[0]
					recorder = edit(config=config,
									classroom=classroom,
									recorder=recorder)
					print("\nSuccessfully Updated Record.\n")
					print(formatter(recorder))
				except ValueError:
					if 'C' in cmd:
						recorder = classroom.getrecorders(subject_name=inp.Elements['subject_name'],
														  date=inp.Elements['date'])[0]
						recorder = edit(config=config,
										classroom=classroom,
										recorder=recorder)
				except IndexError:
					print("No Recorder Found.")
				input("Press enter to return.")

			elif cmd.startswith('S'):
				SubjectFromlist = True

				if len(cmd) == 1 or 'C' in cmd:
					SubjectFromlist = False

				viewStats(config=config,
						  classroom=classroom,
						  Input=inp,
						  SubjectFromList=SubjectFromlist)
				input("Press enter to return.")

			elif cmd.startswith('I'):
				detailed = True if 'D' in cmd else False

				classroomInfo(classroom=classroom,
							  detailed=detailed)
				input("Press enter to return.")

			elif cmd in ['C', 'CONF', 'CINFO', 'CONFIG']:
				configInfo(config=config)
				input("Press enter to return.")

			elif cmd.startswith('H'):
				detailed = True if 'D' in cmd else False
				help(config=config, detailed=detailed)
				input("Press enter to return.")

			elif cmd in ['X', 'EXIT', '0']:
				break
			else:
				pass
		except UnboundLocalError:
			print("Please Input Required Parameters.")
		except ValueError:
			pass
	return classroom


#testInputClass(['vd 1 16 213414', 'ab sk a9f ai', 'a1 204021', 'afsf8 324f32 d1r 9sfhs 3tg5'], True)


if __name__ == '__main__':
	import sys
	databaseFile = None

	try:
		if sys.argv[1].lower() == 'test':
			ConfigFile='./test/config.json'
		for arg in sys.argv[1:]:
			if arg.endswith('.json'):
				databaseFile=arg
	except IndexError:
		pass
	finally:
		del sys

	try:
		config, classroom = loadConfig(ConfigFile, databaseFileOverrider=databaseFile)
	except FileNotFoundError:
		config, classroom = loadConfig(ConfigFile='config_example.json')

	mainClass(config, classroom)
