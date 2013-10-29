from parser import ContentLine, Container
from datetime import datetime, timedelta

class Property(ContentLine):
	Name = ''

	def __init__(self, value='', params={}, name=''):
		name = name if name else self.Name
		super(Property, self).__init__(name, params, self.parseValue(value))

	def parseValue(self, value):
		return value

class ICSDate(Property):
	format = '%Y-%m-%d %H:%M:%S'

	def valueAsString(self):
		return self.value.strftime(self.format)

	def parseValue(self, value):
		if not value:
			return datetime.now()
		elif (isinstance(value, datetime)):
			return value
		return datetime.strptime(self.format, value)

class StartDate(ICSDate): Name = 'DTSTART'

class EndDate(ICSDate): Name = 'DTEND'

class Location(Property): Name = 'LOCATION'

##############

class Section(Container):
	Mandatory = ()
	Name = 'VSECTION'

	def __init__(self, *items, **options):
		super(Section, self).__init__(self.Name)
		for name, property_type in self.Mandatory:
			if name in options:
				self.append(property_type(options[name]))
			else:
				self.append(property_type())
		for item in items:
			self.append(item)

	def __index_for_mandatory(self, name):
		for i in range(len(self.Mandatory)):
			if self.Mandatory[i][0] == name:
				return i
		return None

	def __getattr__(self, attr):
		i = self.__index_for_mandatory(attr)
		return self.__dict__[attr] if i is None else self[i]

class Calendar(Section):
	Mandatory = ()
	Name = 'VCALENDAR'

class Event(Section):
	Mandatory = (
		('start', StartDate),
		('end', EndDate),
	)
	Name = 'VEVENT'

Properties_class = [StartDate, EndDate, Location, Calendar]
Properties = {klass.Name: klass for klass in Properties_class}

Sections_class = [Calendar]
Sections = {klass.Name: klass for klass in Sections_class}
