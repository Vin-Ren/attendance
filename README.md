


# ATTENDANCE RECORDER

This python module is created to record attendances specifically in school, that's why the classes are structured like a school.

## [Main.py](./main.py)
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
-  Case-insensitive is used for app-wide recorder searching.
- Reverse sorted statistics is used for the SortedBy statistics. Reverse means the highest would be on top.
- Statistics blacklisted attendance parameters. any parameters inserted here would be removed if existed in data when processing the statistics.

## [Attendance.py](./attendance.py)
    
Attendance Has 3 Classes: 
- School
- Classroom 
- Recorder

### [Recorder](./attendance.py#L193-L334)

`Recorder.__init__(self, subject_name: str, classroom: Classroom, date: str)` takes 3 required arguments. the subject name, the classroom it's going to inherit students and parameters from, and to be displayed date.

Recorder object created its self.created_datetime, self.modified_datetime, and self.attendance_record when the __init__ method is called.
Recorder object also gives you access to students, parameters, parameter_stats (returns an empty dict if nothing was found on the attendance record or the parameter is not compatible with the record), and human-readable.
- `Recorder.students` returns the Classroom.students. (type: dictionary)
- `Recorder.parameters` returns the Classroom.parameters. (type: dictionary)
- `Recorder.parameter_stats` returns the count of each parameter in Classroom.parameters inside of attendance_record. (type: dictionary)
- `Recorder.human_readable` returns attendance_records that has been converted with Classroom.students and classroom.parameters. (type: dictionary)

 **Functions**

**1. `Recorder.record(self, attendance_record: dict = None, InterfaceOnly = False, InterfaceStoppers: list = ['stop'])` **
A basic attendance_recording interface. record the attendance and assign it into recorder.attendance_record if nothing goes wrong, then returns the recorder object.
- attendance_record would be passed to recorder.load_record.
- If InterfaceOnly is set to true, the record would only record the attendance. When the passed parameter is in Interface Stoppers, the interface loop would automatically stop and returns the recording dictionary.
- InterfaceStoppers Will be used as a stop parameter when InterfaceOnly is enabled.

**2. `Recorder.load_record(self, attendance_record)`**
Loads the attendance_record and assigning it into Recorder.attendance_record if it passes some basic tests.

**3. `Recorder.update(self, updater: dict)`**
updates the current Recorder.attendance_record with the updater dict.

**4. `Recorder.getdata()`**
returns the recorder data in dictionary. Valid to be passed into Recorder.load() as the data parameter.

**5. `Recorder.load(data, classroom: Classroom)`**
Recorder.load is a staticmethod.
returns a recorder object constructed from the data and inherits from the classroom.


### [Classroom](./attendance.py#L89-L190)
Classroom is basically a collection for the recorders as well as the classroom's info to create new recorders.

- `Classroom.recorder_count` returns the count of recorders in the classroom instance.

**Functions**
**1. `Classroom.__init__(self, name: str, students: dict, attendance_parameters: dict)`**
Upon initialization, the Classroom class takes name, students, and attendance parameters as well as create a new attendance record list and put the values to the object's variables.

**2. `Classroom.create_recorder(self, subject_name, date)`**
Creates a new recorder object with the given subject name and date and the classroom itself.

**3. `Classroom.getrecorders(self, subject_name: str = None, date: str = None, caseInsensitive: bool = False, key: callable = None, reverse: bool = False)`**
This function takes 5 optional arguments. 3 to filter, 2 to sort. 
> **Filter arguments**: subject_name, date, caseInsensitive. 
> **Sort arguments**: key, reverse.

if subject_name is passed, it would check the caseInsensitive argument, and filter accordingly.
If date is passed, it would filter the recorders that have the **same** date as the passed date.
If key is passed, it will sort the recorders with the passed key and reverse argument.

**4. `Classroom.getdata(self)`**
This function gets the Classroom instance's data and gets the data from each recorder in the classroom instance then returns it all in an dictionary format. This is the valid input format for `Classroom.load(data)`.

**5. `Classroom.get_recorders_data(self)`**
A function to iterate through all recorders and return all recorder's data in a list.

**6. `Classroom.save(self, filename: str)`**
Takes the filename to save the classroom data from `Classroom.getdata`.

**7. `Classroom.load(data)`**
A static method taking the data from `Classroom.getdata` and reconstructs the classroom object with all its recorders reconstructed as well.

**8. `Classroom.loadfromfile(filename)`**
A static method taking a filename to load the data saved to it by `Classroom.save` method.



### [School](./attendance.py#L9-L86)
School is basically a collection of classrooms and an easier way to manage multiple classroom instances.

- `School.classroom_names` returns a list of all classroom names.
- `School.recorder_count` returns the count of recorders in all classrooms.

**Functions**
**1. `School.__init__(self, name: str, classroom_list: list = [])`**
Initialize the school with given name and classroom list if passed.

**2. `School.create_classroom(self, name: str, students: dict, attendance_parameters: dict)`**
Creates a classroom and puts it into the school instance's classroom list. Note that each classroom should have a unique name.


**3. `School.getclass(self, classname: str)`**
Returns the classroom with matching name, returns None if not found.

**4. `School.getdata(self)`**
Returns the school instance's data in a json format.

**5. `School.save(self, filename)`**
Saves the school instance to the specified filename.

**6. `School.load(data)`**
A static method taking data from `School.save` method to reconstruct the same school instance and returns it.

**7. `School.loadfromfile(filename)`**
A static method that takes filename to load the data saved by `School.save` method.
