# ATTENDANCE RECORDER

## Main.py
Attendance Recorder's configuration file should be saved as config.json in the same directory as the main.py

The Configuration file structure should be the same as below.

```json
{
    "database_filename": "./data.json",
    "subject_list": "Science, Literature, Math",
    "case-insensitive": true,
    "reverse_sorted_statistics": true,
    "statistics_blacklisted_attendance_parameters": ["No Class"],
    "classroom_constructor": {
        "class_name": "Example Class",
        "students_file": "./students.txt",
        "attendance_parameters": {
            "0": "Alpha",
            "1": "Present",
            "2": "Permit",
            "3": "Sick"
        }
    }
}
```
- Classroom_constructor can be omitted **if** the database_filename points to a valid database file of classroom type.

- Main.py can only process file of instance classroom as of now.

- Subject list are separated with a comma followed with a space [, ].

- Case-insensitive is used for app-wide recorder searching.

- Reverse sorted statistics is used for the SortedBy statistics. Reverse means the highest would be on top.

- Statistics blacklisted attendance parameters. any parameters inserted here would be removed if existed in data when processing the statistics.

## Attendance.py
	
Attendance Has 3 Classes: 
	- School
	- Classroom 
	- Recorder

### Recorder

`Recorder.__init__(self, subject_name: str, classroom: Classroom, date: str)` takes 3 required arguments. the subject name, the classroom it's going to inherit students and parameters from, and to be displayed date.

Recorder object created its self.created_datetime, self.modified_datetime, and self.attendance_record when the __init__ method is called.
Recorder object also gives you access to students, parameters, parameter_stats (returns an empty dict if nothing was found on the attendance record or the parameter is not compatible with the record), and human-readable.
- `Recorder.students` returns the Classroom.students. (type: dictionary)
- `Recorder.parameters` returns the Classroom.parameters. (type: dictionary)
- `Recorder.parameter_stats` returns the count of each parameter in Classroom.parameters inside of attendance_record. (type: dictionary)
- `Recorder.human_readable` returns attendance_records that has been converted with Classroom.students and classroom.parameters. (type: dictionary)

 **Functions**

1. `Recorder.record(self, attendance_record: dict = None, InterfaceOnly = False, InterfaceStoppers: list = ['stop'])` 
A basic attendance_recording interface. record the attendance and assign it into recorder.attendance_record if nothing goes wrong, then returns the recorder object.
- attendance_record would be passed to recorder.load_record
- if InterfaceOnly is set to true, the record would only record the attendance. When the passed parameter is in Interface Stoppers, the interface loop would automatically stop and returns the recording dictionary
- InterfaceStoppers Will he used as a stop parameter when InterfaceOnly is enabled.

2. `Recorder.load_record(self, attendance_record)`
Loads the attendance_record and assigning it into Recorder.attendance_record if it passes some basic tests.

3. `Recorder.update(self, updater: dict)`
	updates the current Recorder.attendance_record with the updater dict.

4. `Recorder.getdata()`
returns the recorder data in dictionary. Valid to be passed into Recorder.load() as the data parameter.

5. `Recorder.load(data, classroom: Classroom)`
Recorder.load is a staticmethod.
returns a recorder object constructed from the data and inherits from the classroom.


