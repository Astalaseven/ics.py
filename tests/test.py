from __future__ import unicode_literals, absolute_import
import os
from six import PY2, PY3
from six.moves import filter, map, range

import unittest
from ics.parse import (
    ParseError,
    ContentLine,
    Container,
    unfold_lines,
    string_to_container,
    lines_to_container,
)
from .fixture import (
    cal1,
    cal2,
    cal3,
    cal4,
    cal5,
    cal6,
    cal7,
    cal8,
    cal9,
    unfolded_cal1,
    unfolded_cal2,
    unfolded_cal6,
)
from ics.event import Event
from ics.eventlist import EventList
from ics.icalendar import Calendar


class TestContentLine(unittest.TestCase):

    dataset = {
        'haha:': ContentLine('haha'),
        ':hoho': ContentLine('', {}, 'hoho'),
        'haha:hoho': ContentLine('haha', {}, 'hoho'),
        'haha:hoho:hihi': ContentLine('haha', {}, 'hoho:hihi'),
        'haha;hoho=1:hoho': ContentLine('haha', {'hoho': ['1']}, 'hoho'),
        'RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU':
        ContentLine(
            'RRULE',
            {},
            'FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU'
        ),
        'SUMMARY:dfqsdfjqkshflqsjdfhqs fqsfhlqs dfkqsldfkqsdfqsfqsfqsfs':
        ContentLine(
            'SUMMARY',
            {},
            'dfqsdfjqkshflqsjdfhqs fqsfhlqs dfkqsldfkqsdfqsfqsfqsfs'
        ),
        'DTSTART;TZID=Europe/Brussels:20131029T103000':
        ContentLine(
            'DTSTART',
            {'TZID': ['Europe/Brussels']},
            '20131029T103000'
        ),
    }

    dataset2 = {
        'haha;p2=v2;p1=v1:':
        ContentLine(
            'haha',
            {'p1': ['v1'], 'p2': ['v2']},
            ''
        ),
        'haha;hihi=p3,p4,p5;hoho=p1,p2:blabla:blublu':
        ContentLine(
            'haha',
            {'hoho': ['p1', 'p2'], 'hihi': ['p3', 'p4', 'p5']},
            'blabla:blublu'
        ),
    }

    def test_errors(self):
        self.assertRaises(ParseError, ContentLine.parse, 'haha;p1=v1')
        self.assertRaises(ParseError, ContentLine.parse, 'haha;p1:')

    def test_str(self):
        for test in self.dataset:
            expected = test
            got = str(self.dataset[test])
            self.assertEqual(expected, got, "To string")

    def test_parse(self):
        self.dataset2.update(self.dataset)
        for test in self.dataset2:
            expected = self.dataset2[test]
            got = ContentLine.parse(test)
            self.assertEqual(expected, got, "Parse")


class TestUnfoldLines(unittest.TestCase):

    def test_no_folded_lines(self):
        self.assertEqual(list(unfold_lines(cal2.split('\n'))), unfolded_cal2)

    def test_simple_folded_lines(self):
        self.assertEqual(list(unfold_lines(cal1.split('\n'))), unfolded_cal1)

    def test_last_line_folded(self):
        self.assertEqual(list(unfold_lines(cal6.split('\n'))), unfolded_cal6)

    def test_simple(self):
        dataset = {
            'a': ('a',),
            'ab': ('ab',),
            'a\nb': ('a', 'b',),
            'a\n b': ('ab',),
            'a \n b': ('a b',),
            'a\n b\nc': ('ab', 'c',),
            'a\nb\n c': ('a', 'bc',),
            'a\nb\nc': ('a', 'b', 'c',),
            'a\n b\n c': ('abc',),
            'a \n b \n c': ('a b c',),
        }
        for line in dataset:
            expected = dataset[line]
            got = tuple(unfold_lines(line.split('\n')))
            self.assertEqual(expected, got)

    def test_empty(self):
        self.assertEqual(list(unfold_lines([])), [])

    def test_one_line(self):
        self.assertEqual(list(unfold_lines(cal6.split('\n'))), unfolded_cal6)

    def test_two_lines(self):
        self.assertEqual(list(unfold_lines(cal3.split('\n'))),
                         ['BEGIN:VCALENDAR', 'END:VCALENDAR'])

    def test_no_empty_lines(self):
        self.assertEqual(list(unfold_lines(cal7.split('\n'))),
                         ['BEGIN:VCALENDAR', 'END:VCALENDAR'])

    def test_no_whitespace_lines(self):
        self.assertEqual(list(unfold_lines(cal8.split('\n'))),
                         ['BEGIN:VCALENDAR', 'END:VCALENDAR'])

    def test_first_line_empty(self):
        self.assertEqual(list(unfold_lines(cal9.split('\n'))),
                         ['BEGIN:VCALENDAR', 'END:VCALENDAR'])


class TestParse(unittest.TestCase):

    def test_parse(self):
        content = string_to_container(cal5)
        self.assertEqual(1, len(content))

        cal = content.pop()
        self.assertEqual('VCALENDAR', cal.name)
        self.assertTrue(isinstance(cal, Container))
        self.assertEqual('VERSION', cal[0].name)
        self.assertEqual('2.0', cal[0].value)
        self.assertEqual(cal5.strip(), str(cal).strip())

    def test_one_line(self):
        ics = 'DTSTART;TZID=Europe/Brussels:20131029T103000'
        reader = lines_to_container([ics])
        self.assertEqual(next(iter(reader)), TestContentLine.dataset[ics])

    def test_many_lines(self):
        i = 0
        for line in string_to_container(cal1)[0]:
            self.assertNotEqual('', line.name)
            if isinstance(line, ContentLine):
                self.assertNotEqual('', line.value)
            if line.name == 'DESCRIPTION':
                self.assertEqual('Lorem ipsum dolor sit amet, \
                    consectetur adipiscing elit. \
                    Sed vitae facilisis enim. \
                    Morbi blandit et lectus venenatis tristique. \
                    Donec sit amet egestas lacus. \
                    Donec ullamcorper, mi vitae congue dictum, \
                    quam dolor luctus augue, id cursus purus justo vel lorem. \
                    Ut feugiat enim ipsum, quis porta nibh ultricies congue. \
                    Pellentesque nisl mi, molestie id sem vel, \
                    vehicula nullam.', line.value)
            i += 1


class TestEvent(unittest.TestCase):

    def test_event(self):
        e = Event(begin=0, end=20)
        self.assertEqual(e.begin.timestamp, 0)
        self.assertEqual(e.end.timestamp, 20)
        self.assertTrue(e.has_end())
        self.assertFalse(e.all_day)

        f = Event(begin=10, end=30)
        self.assertTrue(e < f)
        self.assertTrue(e <= f)
        self.assertTrue(f > e)
        self.assertTrue(f >= e)

    def test_or(self):
        g = Event(begin=0, end=10) | Event(begin=10, end=20)
        self.assertEqual(g, (None, None))

        g = Event(begin=0, end=20) | Event(begin=10, end=30)
        self.assertEqual(tuple(map(lambda x: x.timestamp, g)), (10, 20))

        g = Event(begin=0, end=20) | Event(begin=5, end=15)
        self.assertEqual(tuple(map(lambda x: x.timestamp, g)), (5, 15))

        g = Event() | Event()
        self.assertEqual(g, (None, None))


class TestEventList(unittest.TestCase):

    from time import time

    def test_evlist(self):
        l = EventList()
        t = self.time()

        self.assertEqual(len(l), 0)
        e = Event(begin=t, end=t + 1)
        l.append(e)
        self.assertEqual(len(l), 1)
        self.assertEqual(l[0], e)
        self.assertEqual(l.today(), [e])
        l.append(Event(begin=t, end=t + 86400))
        self.assertEqual(l.today(strict=True), [e])


class TestCalendar(unittest.TestCase):

    def test_imports(self):
        c = Calendar(cal1)
        self.assertEqual(1, len(c.events))

    def test_events(self):
        e = Event(begin=0, end=30)
        c = Calendar()
        c.events.append(e)
        d = Calendar(events=c.events)
        self.assertEqual(1, len(d.events))
        self.assertEqual(e, d.events[0])

    def test_selfload(self):
        c = Calendar(cal1)
        d = Calendar(str(c))
        self.assertEqual(c, d)
        for i in range(len(c.events)):
            e, f = c.events[i], d.events[i]
            self.assertEqual(e, f)
            self.assertEqual(e.begin, f.begin)
            self.assertEqual(e.end, f.end)
            self.assertEqual(e.name, f.name)


class TestFunctional(unittest.TestCase):

    def test_gehol(self):
        # convert ics to utf8: recode l9..utf8 *.ics
        cal = os.path.join(os.path.dirname(__file__), "gehol", "BA1.ics")
        with open(cal) as ics:
            ics = ics.read()
            if PY2:
                ics = ics.decode('utf-8')

            ics = string_to_container(ics)[0]
            self.assertTrue(ics)


if __name__ == '__main__':
    unittest.main()
