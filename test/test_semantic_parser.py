# Copyright 2019 Alex Badics <admin@stickman.hu>
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

from hun_law.utils import IndentedLine
from hun_law.structure import Reference, InTextSemanticData
from hun_law.parsers.structure_parser import ActParser
from hun_law.parsers.semantic_parser import ActSemanticDataParser

import pytest


def absref(act=None, article=None, paragraph=None, point=None, subpoint=None):
    return Reference(act, article, paragraph, point, subpoint)


def ref(article=None, paragraph=None, point=None, subpoint=None):
    return Reference(None, article, paragraph, point, subpoint)


@pytest.fixture(scope="module")
def parser():
    return ActSemanticDataParser()


CASES_WITHOUT_POSITIONS = [
    (
        """
            17. §          Hatályát veszti
                           a)   a Polgári Törvénykönyvről szóló 1959. évi IV. törvény 261. § (4) bekezdése,
                           b)   a Polgári Törvénykönyv hatálybalépéséről és végrehajtásáról szóló 1960. évi 11. törvényerejű
                                rendelet 83/A. §-a,
                           c)   az ingatlan-nyilvántartásról szóló 1997. évi CXLI. törvény 16/A. §-a és 91. § (2) bekezdése.
        """,
        {
            ref("17", None, "a"): (
                absref("1959. évi IV. törvény"),
                absref("1959. évi IV. törvény", "261", "4"),
            ),
            # TODO: Act-like decree ref in b)
            ref("17", None, "b"): (
                ref("83/A"),
            ),
            ref("17", None, "c"): (
                absref("1997. évi CXLI. törvény"),
                absref("1997. évi CXLI. törvény", "16/A"),
                absref("1997. évi CXLI. törvény", "91", "2"),
            ),
        },
    ),
    (
        """
        40. § (1)  A kisadózó vállalkozások tételes adójáról és a kisvállalati adóról szóló 2012. évi CXLVII. törvény (a továbbiakban: Katv.) 2. § 19–20. pontja helyébe a következő rendelkezés lép:

        41. §   Hatályát veszti
                1. az illetékekről szóló 1990. évi XCIII. törvény 17. § (1) bekezdés c) pontjában a „vagy egészségügyi hozzájárulás” szövegrész;
                2. a számvitelről szóló 2000. évi C. törvény
                    a) 79. § (4) bekezdésében az „az egészségügyi hozzájárulás,” szövegrész;
                    b) 103. § (2) bekezdés c) pontjában az „egészségügyi hozzájárulás,” szövegrész;
                3. a különösen sok dologról szóló 2004. évi CXXIII. törvény
                    a) 8/A. §–8/B. §-a,
                    b) 16/A. §–16/B. §-a,
                    c) 17/A. § (1) és (3) bekezdése;
                4. a Katv. 2. § 21. pontja;
        """,
        {
            ref("40", "1"): (
                absref("2012. évi CXLVII. törvény"),
                absref("2012. évi CXLVII. törvény", "2", None, ("19", "20")),
            ),
            ref("41", None, "1"): (
                absref("1990. évi XCIII. törvény"),
                absref("1990. évi XCIII. törvény", "17", "1", "c"),
            ),
            ref("41", None, "2"): (
                absref("2000. évi C. törvény"),
            ),
            ref("41", None, "2", "a"): (
                absref("2000. évi C. törvény", "79", "4"),
            ),
            ref("41", None, "2", "b"): (
                absref("2000. évi C. törvény", "103", "2", "c"),
            ),
            ref("41", None, "3"): (
                absref("2004. évi CXXIII. törvény"),
            ),
            ref("41", None, "3", "a"): (
                absref("2004. évi CXXIII. törvény", ("8/A", "8/B")),
            ),
            ref("41", None, "3", "b"): (
                absref("2004. évi CXXIII. törvény", ("16/A", "16/B")),
            ),
            ref("41", None, "3", "c"): (
                absref("2004. évi CXXIII. törvény", "17/A", "1"),
                absref("2004. évi CXXIII. törvény", "17/A", "3"),
            ),
            ref("41", None, "4"): (
                absref("2012. évi CXLVII. törvény"),
                absref("2012. évi CXLVII. törvény", "2", None, "21"),
            ),
        },

    ),
]


def quick_parse_structure(act_text):
    lines = []
    for l in act_text.split('\n'):
        parts = []
        skip_spaces = True
        for indent, char in enumerate(l):
            if char == ' ' and skip_spaces:
                continue
            skip_spaces = False
            parts.append(IndentedLine.Part(indent * 5, char))
        lines.append(IndentedLine.from_parts(parts))
    return ActParser.parse("2345 évi 1. törvény", "About testing", lines)


@pytest.mark.parametrize("act_text,itsds", CASES_WITHOUT_POSITIONS)
def test_parse_results_without_position(parser, act_text, itsds):
    act = quick_parse_structure(act_text)
    semantic_data = parser.parse(act)
    extracted_itsds = {k: tuple(vv.data for vv in v) for k, v in semantic_data.iter_semantic_data_items()}
    assert extracted_itsds == itsds


def test_parse_positions_are_okay(parser):
    act = quick_parse_structure(
        """
        1. §    A tesztelésről szóló 2345. évi I. törvény
                a) 8. §
                    aa) (5) bekezdése,
                    ab) (6) bekezdés a) pontja,
                b) 10. §-a, és
                c) egy totál másik dolog 1. § c) pontja, még utána ezzel szöveggel
                jól van feldolgozva.
        """
    )
    semantic_data = parser.parse(act)
    parsed_data = dict(semantic_data.iter_semantic_data_items())
    print(parsed_data)
    correct_data = {
        ref("1"): (InTextSemanticData(21, 41, Reference("2345. évi I. törvény")), ),
        ref("1", None, "a"): (InTextSemanticData(0, 4, Reference("2345. évi I. törvény", "8")), ),
        ref("1", None, "a", "aa"): (InTextSemanticData(0, 13, Reference("2345. évi I. törvény", "8", "5")), ),
        ref("1", None, "a", "ab"): (InTextSemanticData(0, 22, Reference("2345. évi I. törvény", "8", "6", "a")), ),
        ref("1", None, "b"): (InTextSemanticData(0, 7, Reference("2345. évi I. törvény", "10")),),
        ref("1", None, "c"): (InTextSemanticData(22, 36, Reference(None, "1", None, "c")),),
    }
    assert parsed_data == correct_data
