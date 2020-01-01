# Copyright 2018 Alex Badics <admin@stickman.hu>
#
# This file is part of Hun-Law.
#
# Hun-Law is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Hun-Law is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Hun-Law.  If not, see <https://www.gnu.org/licenses/>.

import re
from typing import List, Dict, Optional, Type, Tuple, Iterable, Union, Callable
import attr

from hun_law.utils import EMPTY_LINE, IndentedLine
from . import Extractor
from .pdf import PdfOfLines


def is_magyar_kozlony(pdf_file: PdfOfLines) -> bool:
    # TODO: Lets hope justified text detector works, and it's not something like
    # 'M A G Y A R K O Z L O N Y
    if 'MAGYAR KÖZLÖNY' in pdf_file.pages[0].lines[0].content:
        return True
    return False


@attr.s(slots=True, frozen=True, auto_attribs=True)
class PageWithHeader:
    header: Tuple[IndentedLine, ...]
    lines: Tuple[IndentedLine, ...]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class KozlonyPagesWithHeaderAndFooter:
    pages: Tuple[PageWithHeader, ...]


@Extractor(PdfOfLines)
def MagyarKozlonyHeaderExtractor(pdf_file: PdfOfLines) -> Iterable[KozlonyPagesWithHeaderAndFooter]:
    if not is_magyar_kozlony(pdf_file):
        return
    # TODO: assert the header.

    # The first page is special:

    # MAGYAR KÖZLÖNY 71 . szám
    #
    # A MAGYAR KÖZTÁRSASÁG HIVATALOS LAPJA
    # 2011. június 28., kedd
    #

    result_pages = [PageWithHeader(tuple(pdf_file.pages[0].lines[:5]), tuple(pdf_file.pages[0].lines[5:]))]
    for page in pdf_file.pages:
        # Others are
        # 15202 M A G Y A R   K Ö Z L Ö N Y  •  2011. évi 71 . szám
        #
        result_pages.append(PageWithHeader(tuple(page.lines[:2]), tuple(page.lines[2:])))
    yield KozlonyPagesWithHeaderAndFooter(tuple(result_pages))


@attr.s(slots=True, frozen=True, auto_attribs=True)
class MagyarKozlonyLawsSection:
    lines: Tuple[IndentedLine, ...]


SectionType = Union[MagyarKozlonyLawsSection]

SECTION_TYPES: Dict[str, Optional[Type[SectionType]]] = {
    'Tartalomjegyzék': None,
    'II. Törvények': MagyarKozlonyLawsSection,
    'III. Kormányrendeletek': None,
    'IV. A Magyar Nemzeti Bank elnökének rendeletei,': None,  # TODO: This could be formatted in otehr ways
    'V. A Kormány tagjainak rendeletei': None,
    'VI.Az Alkotmánybíróság határozatai, teljes ülési': None,  # TODO: This is most probably word-wrapped in oither ways
    'VII. A Kúria határozatai': None,
    # TODO: VIII.
    'IX. Határozatok Tára': None,
    # TODO: X?
}


@Extractor(KozlonyPagesWithHeaderAndFooter)
def MagyarKozlonySectionExtractor(kozlony: KozlonyPagesWithHeaderAndFooter) -> Iterable[SectionType]:
    current_section_type = None
    content_of_current_section: List[IndentedLine] = []

    for page in kozlony.pages:

        if not page.lines:
            continue
        for section_type in SECTION_TYPES:
            # This is not something like 'page.lines[0] in SECTION_TYPES' to allow for more
            # complex conditions, like regex section types later.
            if page.lines[0].content != section_type:
                continue
            if current_section_type == section_type:
                content_of_current_section.extend(page.lines[1:])
                break
            if current_section_type is not None:
                if SECTION_TYPES[current_section_type] is not None:
                    yield SECTION_TYPES[current_section_type](tuple(content_of_current_section))
            current_section_type = section_type
            content_of_current_section = list(page.lines[1:])
            break
        else:
            if current_section_type is None:
                raise ValueError("Unknown starting section: '{}'".format(page.lines[0]))
            content_of_current_section.extend(page.lines)
        # This is where we do away with the "Page" abstraction, and further processing
        # can only use EMPTY_LINE to have some separation info.
        content_of_current_section.append(EMPTY_LINE)
    assert current_section_type is not None
    the_type = SECTION_TYPES[current_section_type]
    if the_type is not None:
        yield the_type(tuple(content_of_current_section))


@attr.s(slots=True, frozen=True, auto_attribs=True)
class MagyarKozlonyLawRawText:
    identifier: str
    subject: str
    body: Tuple[IndentedLine, ...]


LawExtractorStateFn = Callable[[IndentedLine], None]


class LawExtractorStateMachine:
    HEADER_STARTING_RE = re.compile('^[12][09][0-9][0-9]. évi [IVXLC]+. törvény')
    ACT_FOOTER_RE = re.compile('köztársasági elnök az Országgyűlés (al)?elnöke')

    def __init__(self) -> None:
        self.identifier = ''
        self.subject = ''
        self.body: List[IndentedLine] = []
        self.state: LawExtractorStateFn = self.WAITING_FOR_HEADER_NEWLINE
        self.pending_result: Optional[MagyarKozlonyLawRawText] = None

    def feed_line(self, line: IndentedLine) -> Optional[MagyarKozlonyLawRawText]:
        self.pending_result = None
        self.state(line)
        return self.pending_result

    def WAITING_FOR_HEADER_NEWLINE(self, line: IndentedLine) -> None:
        if line != EMPTY_LINE:
            return
        self.state = self.WAITING_FOR_HEADER

    def WAITING_FOR_HEADER(self, line: IndentedLine) -> None:
        if not self.HEADER_STARTING_RE.match(line.content):
            self.state = self.WAITING_FOR_HEADER_NEWLINE
            return
        self.identifier = line.content
        self.state = self.HEADER

    def HEADER(self, line: IndentedLine) -> None:
        if self.subject != '':
            self.subject = self.subject + ' ' + line.content
        else:
            self.subject = line.content

        # TODO: this is also a huge hack, because we depend on there always being a footer about
        # when the law or amendment was enacted and by whom.
        if self.subject[-1] == '*':
            self.subject = self.subject[:-1]
            self.state = self.BODY_BEFORE_ASTERISK_FOOTER

    def BODY_BEFORE_ASTERISK_FOOTER(self, line: IndentedLine) -> None:
        # State to swallow the following footer:
        # "* A törvényt az Országgyûlés a 2010. november 22-i ülésnapján fogadta el."

        self.body.append(line)
        if len(self.body) >= 4:
            # TODO: this whole asterisk footer whatever is ugly. The footer should be detected
            # in extractors before this one, based on other cues.
            # Also let's just hope there are no two small laws on a single page
            if self.body[-3] == EMPTY_LINE and self.body[-1] == EMPTY_LINE and self.body[-2].content[0] == '*':
                self.body = self.body[:-3] + [EMPTY_LINE]
                self.state = self.BODY_AFTER_ASTERISK_FOOTER
                return

        # There might not be an asterisk footer at all before the end of the act,
        # so check for that too in this state.
        # But let's pretend the append never happened, first.
        self.body.pop()
        self.BODY_AFTER_ASTERISK_FOOTER(line)

    def BODY_AFTER_ASTERISK_FOOTER(self, line: IndentedLine) -> None:
        self.body.append(line)

        if len(self.body) < 4:
            # body not long enough to contain ACT_FOOTER_RE
            return

        # Example for the actual format of the act footer
        # [EMPTY]
        # Dr. Schmitt Pál s. k.,     Dr. Kövér László s. k.,
        # köztársasági elnök     az Országgyűlés elnöke
        if self.body[-3] == EMPTY_LINE and self.ACT_FOOTER_RE.match(self.body[-1].content):
            # TODO: Extract footer
            self.pending_result = MagyarKozlonyLawRawText(
                self.identifier,
                self.subject,
                tuple(self.body[:-3])
            )
            self.identifier = ''
            self.subject = ''
            self.body = []
            self.state = self.WAITING_FOR_HEADER_NEWLINE


@Extractor(MagyarKozlonyLawsSection)
def MagyarKozlonyLawExtractor(laws_section: MagyarKozlonyLawsSection) -> Iterable[MagyarKozlonyLawRawText]:
    state_machine = LawExtractorStateMachine()
    for line in laws_section.lines:
        result = state_machine.feed_line(line)
        if result is not None:
            yield result
