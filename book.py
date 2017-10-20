import math
import os

BOOK_PAGE = """

    |<---------------->|
  ^ ####################
  | ####################
  | ####################
  | ####################
  | ####################
  | ####################
  | ####################
"""

SHEET_SIZE_LINE = ''

HORIZONTAL_MARGIN_LINE = ''

VERTICAL_MARGIN_LINE = ''

FOLDING_TABLE_DISCLAIMER = """
{pattern_name:=<080}
The folding marks are measured from the bottom of the page.
The blank pages are meant to be folded all the way, from top to bottom.
The measures are given in cm.
===============================================================================
"""

FOLDING_TABLE_HEADER = """
===============================================================================
{page: <04}\t{lower_mark: <05}\t{upper_mark: <05}
===============================================================================\n"""

FOLDING_TABLE_FOOTER = """
===============================================================================
Generated by the OverWorked Moodule.
Licensed under GPL v3.
Enjoy your time folding !"""

FOLDING_TABLE_BLANK_LINE = """
{page: <04d}\t{lower: <05.1f}\t{upper: <05.1f}\tThis page is WHITE = folded all the way!\n"""

FOLDING_TABLE_FOLDED_LINE = """
{page: <04d}\t{lower: <05.1f}\t{upper: <05.1f}\n"""

FOLDING_TABLE_BLACK_LINE = """
{page: <04d}\t{lower: <05.1f}\t{upper: <05.1f}\tThis page is BLACK = not folded !\n"""

NOT_ENOUGH_PAGES_WARNING = """
! The book has only {sheet_count} sheets of paper while the pattern requires {band_count} !"""

class Book(object):
    """Models the whole book.
    It is chosen to match the aspect ratio of the pattern, which is considered fixed.
    To adjust the aspect ratio of the folded pattern, you can play with :
        - the book size (sheet size, number of pages)
        - the margins around the folded pattern (optimal values are calculated)
        - the opening of the book (3 cases : 90, 180 and 360)"""
   
    def __init__(self):
        self._first_page = 1            # no unit, the total page count, equals last page number
        self._last_page = 100
        self._sheet_height = 0.2        # taking the margin into account
        self._sheet_depth = 0.1
        self._horizontal_margin = 0     # no unit, it is the number of sheets left both before and after the pattern
        self._vertical_margin = 0.0     # in meters, the blank space left both above and under the pattern
        self._opening = 180             # in degrees, the angle of opening calculated to preserve the aspect ratio
        self._pattern = None

    def __str__(self):
        str_format = """{book_name:=<050}"""
        str_format = str_format.format(book_name='= Book ' + self._pattern.name() + ' ')
        return str_format

    def sheet_count(self):  # the actual number of pages used in the pattern
        total_sheet_count = int(math.ceil(float(self._last_page - self._first_page + 1) / 2.0))
        pattern_sheet_count = total_sheet_count - 2 * self._horizontal_margin
        pattern_sheet_count = max(pattern_sheet_count, 0)
        return (self._horizontal_margin, pattern_sheet_count, self._horizontal_margin, total_sheet_count)

    def sheet_height(self):
        pattern_height = self._sheet_height - 2.0 * self._vertical_margin
        pattern_height = round(max(0.0, pattern_height), 3)
        return (self._vertical_margin, pattern_height, self._vertical_margin, self._sheet_height)

    def sheet_spacing(self):
        max_spacing = 2.0 * 3.1416 * self._sheet_depth
        max_spacing = max_spacing / self.sheet_count()[3]
        return (0.25 * max_spacing, 0.5 * max_spacing, max_spacing)

    def aspect_ratio(self):
        """Gives the range of possible ratios for the folded pattern.
        The ratio can be adjusted by opening the book more or less.
        The calculation is made with fixed margins."""
        pattern_sheet_count = self.sheet_count()[1]
        pattern_height = self.sheet_height()[1]
        pattern_ratio = float(pattern_sheet_count) / pattern_height
        min_ratio = self.sheet_spacing()[0] * pattern_ratio
        max_ratio = self.sheet_spacing()[2] * pattern_ratio
        opt_ratio = self.sheet_spacing()[1] * pattern_ratio
	return (min_ratio, opt_ratio, max_ratio)

    def horizontal_ranges(self):
        pattern_start_page = self._first_page + 2 * self._horizontal_margin
        pattern_end_page = pattern_start_page + 2 * self.sheet_count()[1]
        return (self._first_page, pattern_start_page, pattern_end_page, self._last_page)

    def vertical_ranges(self):
        return (0.0, self._vertical_margin, self._sheet_height - self._vertical_margin, self._sheet_height)

    def name(self):
        book_name = ''
        if self._pattern is not None:
            book_name = self._pattern.name()
        return book_name

    def set_size(self, first_page_number, last_page_number, sheet_height, sheet_depth):
        self._first_page = first_page_number
        self._last_page = last_page_number
        self._sheet_height = sheet_height
        self._sheet_depth = sheet_depth

    def set_pattern(self, pattern):
        self._pattern = pattern
        self._calculate_margins()
        if self._pattern.width(raw=False) > self.sheet_count()[3]:
            print NOT_ENOUGH_PAGES_WARNING.format(
                    sheet_count=self.sheet_count()[3],
                    band_count=self._pattern.width(raw=False)) 

    def _calculate_margins(self):
        self._calculate_horizontal_margin()
        self._calculate_book_opening()
        self._calculate_vertical_margin()

    def _calculate_horizontal_margin(self):
        self._horizontal_margin = 0
        if self._pattern is not None:
            self._horizontal_margin = self.sheet_count()[3] - self._pattern.width(raw=False)
            self._horizontal_margin = max(0, self._horizontal_margin) // 2

    def _calculate_book_opening(self):
        self._book_opening = 180
        if self._pattern is not None:
            pattern_width_360 = self.sheet_spacing()[2] * float(self.sheet_count()[1])
            pattern_height_360 = pattern_width_360 / self._pattern.aspect_ratio(raw=True)
            pattern_to_sheet_ratio = pattern_height_360 / self.sheet_height()[3]
            if pattern_to_sheet_ratio < 1.0:
                self._book_opening = 360
            elif pattern_to_sheet_ratio < 2.0:
                self._book_opening = 180
            else:
                self._book_opening = 90

    def _calculate_vertical_margin(self):
        self._vertical_margin = 0.0
        if self._pattern is not None:
            pattern_width_360 = self.sheet_spacing()[2] * float(self.sheet_count()[1])
            pattern_height_360 = pattern_width_360 / self._pattern.aspect_ratio(raw=True)
            self._vertical_margin = 0.5 * self.sheet_height()[3]
            if self._book_opening == 360:
                self._vertical_margin -= 0.5 * pattern_height_360
            elif self._book_opening == 180:
                self._vertical_margin -= 0.25 * pattern_height_360
            else:
                self._vertical_margin -= 0.125 * pattern_height_360
            self._vertical_margin = max(0.0, self._vertical_margin)
            self._vertical_margin = round(self._vertical_margin, 3)

    def save_folding_table(self, pattern_path=None):
        saving_path = os.path.join('patterns/', self.name())
        if pattern_path is not None:
            if type(pattern_path) is str and pattern_path:
                saving_path = pattern_path
        saving_path, ext = os.path.splitext(saving_path)
        ext = ext.replace('.', '')
        if not ext:
            ext = 'txt'
        saving_path += '_pattern.' + ext.lower()

        with open(saving_path, 'w') as pattern_file:
       
            if self._pattern is not None:
                folding_table = FOLDING_TABLE_DISCLAIMER.format(
                    pattern_name='= ' + self._pattern.name() + ' ')

                folding_table += FOLDING_TABLE_HEADER.format(
                        page='Page',
                        lower_mark='Lower',
                        upper_mark='upper')
        
                for i, band in enumerate(self._pattern._bands):
                    folding_table += self._band_to_folding_marks_line_str(i, band)

                folding_table += FOLDING_TABLE_FOOTER

            pattern_file.write(folding_table)
            pattern_file.close()
            print 'Your pattern has been saved to {file_path}.'.format(file_path=saving_path)

    def fold(self):
        pass

    def _pixel_to_sheet_coordinate(self, pixel_y):
        pixel_ratio = self._pattern.vertical_coordinate_ratio(pixel_y, from_top=False, raw=False)
        coordinate = self._vertical_margin + (pixel_ratio * self.sheet_height()[1])
        return coordinate

    def _band_to_folding_marks_line_str(self, index, band):
        folding_marks_line = ''
        is_blank_page = (band[0] == band[1])
        current_page = self._first_page + 2 * self._horizontal_margin + 2 * index
        lower_mark = 100.0 * self._pixel_to_sheet_coordinate(band[1])
        upper_mark = 100.0 * self._pixel_to_sheet_coordinate(band[0])
        if is_blank_page:
            lower_mark = 0.0
            upper_mark = 100.0 * self._sheet_height
            folding_marks_line = FOLDING_TABLE_BLANK_LINE.format(
                                    page=current_page,
                                    lower=lower_mark,
                                    upper=upper_mark)
        else:
            folding_marks_line = FOLDING_TABLE_FOLDED_LINE.format(
                                    page=current_page,
                                    lower=lower_mark,
                                    upper=upper_mark)
        return folding_marks_line
