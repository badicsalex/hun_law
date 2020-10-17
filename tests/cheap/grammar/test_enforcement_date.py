# Copyright 2018-2019 Alex Badics <admin@stickman.hu>
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

from typing import Tuple

import pytest

from hun_law.parsers.grammatical_analyzer import GrammaticalAnalyzer
from hun_law.structure import EnforcementDate, DaysAfterPublication, DayInMonthAfterPublication
from hun_law.utils import Date

from tests.cheap.utils import ref

CASES: Tuple[Tuple[str, Tuple[EnforcementDate, ...]], ...] = (
    (
        "E törvény 2013. július 1-jén lép hatályba.",
        (
            EnforcementDate(position=None, date=Date(2013, 7, 1)),
        )
    ),
    (
        "Ez a törvény a kihirdetését követő napon lép hatályba.",
        (
            EnforcementDate(position=None, date=DaysAfterPublication()),
        )
    ),
    (
        "Ez a törvény kihirdetését követő napon lép hatályba.",
        (
            EnforcementDate(position=None, date=DaysAfterPublication()),
        )
    ),
    (
        "Ez a törvény – a (2) bekezdésben meghatározott kivétellel – a kihirdetését követő napon lép hatályba.",
        (
            EnforcementDate(position=None, date=DaysAfterPublication()),
        )
    ),
    (
        "Ez a törvény – a (2)–(14) bekezdésben meghatározott kivétellel – a kihirdetését követő napon lép hatályba.",
        (
            EnforcementDate(position=None, date=DaysAfterPublication()),
        )

    ),
    (
        "Ez a törvény a kihirdetését követő nyolcadik napon lép hatályba.",
        (
            EnforcementDate(position=None, date=DaysAfterPublication(8)),
        )
    ),
    (
        "Ez a törvény a kihirdetését követő tizenötödik napon lép hatályba.",
        (
            EnforcementDate(position=None, date=DaysAfterPublication(15)),
        )
    ),
    (
        "Ez a törvény a kihirdetését követő harmincadik napon lép hatályba.",
        (
            EnforcementDate(position=None, date=DaysAfterPublication(30)),
        )
    ),
    (
        "Ez a törvény – a (2)–(8) bekezdésben foglalt kivétellel – a kihirdetést követő 8. napon lép hatályba.",
        (
            EnforcementDate(position=None, date=DaysAfterPublication(days=8)),
        )
    ),
    (
        "Ez a törvény – a (2) bekezdésben foglaltak kivételével − a kihirdetését követő 30. napon lép hatályba.",
        (
            EnforcementDate(position=None, date=DaysAfterPublication(days=30)),
        )
    ),
    (
        "Az 50–51. § és az 53. § (1)–(5) bekezdése e törvény kihirdetését követő 31. napon lép hatályba.",
        (
            EnforcementDate(position=ref(None, ('50', '51')), date=DaysAfterPublication(31)),
            EnforcementDate(position=ref(None, '53', ('1', '5')), date=DaysAfterPublication(31)),
        )
    ),
    (
        "A 180. § (1) bekezdés a) pontja 2013. január 2-án lép hatályba.",
        (
            EnforcementDate(position=ref(None, '180', '1', 'a'), date=Date(2013, 1, 2)),
        )
    ),
    (
        "A 112. § (4), (10), (32), (44), (48) és (51) bekezdése, (54) bekezdésének 30. pontja 2014. július 1-jén lép hatályba.",
        (
            EnforcementDate(position=ref(None, '112', '4'), date=Date(2014, 7, 1)),
            EnforcementDate(position=ref(None, '112', '10'), date=Date(2014, 7, 1)),
            EnforcementDate(position=ref(None, '112', '32'), date=Date(2014, 7, 1)),
            EnforcementDate(position=ref(None, '112', '44'), date=Date(2014, 7, 1)),
            EnforcementDate(position=ref(None, '112', '48'), date=Date(2014, 7, 1)),
            EnforcementDate(position=ref(None, '112', '51'), date=Date(2014, 7, 1)),
            EnforcementDate(position=ref(None, '112', '54', '30'), date=Date(2014, 7, 1)),
        )
    ),
    (
        "A 10. § c) és d) pontja 2017. június 30. napján lép hatályba.",
        (
            EnforcementDate(position=ref(None, '10', None, ('c', 'd')), date=Date(2017, 6, 30)),
        )
    ),
    (
        "A 36. §, a 197. § (3) bekezdése, a 200. § (4) bekezdése, a 205. §, a 218–219. §, a 221. §, a 225–227. §, "
        "a 229. §, a 231. §, a 233. § (1) bekezdés a) és c) pontja, (2) bekezdés d) és f) pontja, a 256. §, a 314. "
        "§ és a 318. § 2013. február 1-jén lép hatályba.",
        (
            EnforcementDate(position=ref(None, '36'), date=Date(2013, 2, 1)),
            EnforcementDate(position=ref(None, '197', '3'), date=Date(2013, 2, 1)),
            EnforcementDate(position=ref(None, '200', '4'), date=Date(2013, 2, 1)),
            EnforcementDate(position=ref(None, '205'), date=Date(2013, 2, 1)),
            EnforcementDate(position=ref(None, ('218', '219')), date=Date(2013, 2, 1)),
            EnforcementDate(position=ref(None, '221'), date=Date(2013, 2, 1)),
            EnforcementDate(position=ref(None, ('225', '227')), date=Date(2013, 2, 1)),
            EnforcementDate(position=ref(None, '229'), date=Date(2013, 2, 1)),
            EnforcementDate(position=ref(None, '231'), date=Date(2013, 2, 1)),
            EnforcementDate(position=ref(None, '233', '1', 'a'), date=Date(2013, 2, 1)),
            EnforcementDate(position=ref(None, '233', '1', 'c'), date=Date(2013, 2, 1)),
            EnforcementDate(position=ref(None, '233', '2', 'd'), date=Date(2013, 2, 1)),
            EnforcementDate(position=ref(None, '233', '2', 'f'), date=Date(2013, 2, 1)),
            EnforcementDate(position=ref(None, '256'), date=Date(2013, 2, 1)),
            EnforcementDate(position=ref(None, '314'), date=Date(2013, 2, 1)),
            EnforcementDate(position=ref(None, '318'), date=Date(2013, 2, 1)),
        )
    ),
    (
        "Az 1–35. §, a 37–151. §, a 153–176. §, a 177. § (3) bekezdése, 178–179. §, a 180. § (1) bekezdés b)–d) "
        "pontja, a 180. § (2) bekezdése, a 181–196. §, a 197. § (1)–(2) és (4)–(5) bekezdése, a 198–199. §, a 200. "
        "§ (1)–(3) és (5)–(6) bekezdése, a 201–204. §, a 206–208. §, a 212. §, a 214–217. §, a 220. §, a 222–224. "
        "§, a 228. §, a 230. §, a 232. §, a 233. § (1) bekezdés b) pontja és (2) bekezdés a)–c) és e) pontja, a "
        "235–255. §, a 257–260. §, a 261. § (2)–(5) bekezdése és (6) bekezdés b)–d) pontja, a 262–290. §, a 291. § "
        "(1), (2), és (4)–(10) bekezdése, a 292–313. § és a 315–317. § 2013. július 1-jén lép hatályba.",
        (
            EnforcementDate(position=ref(None, ('1', '35')), date=Date(2013, 7, 1)),
            EnforcementDate(position=ref(None, ('37', '151')), date=Date(2013, 7, 1)),
            EnforcementDate(position=ref(None, ('153', '176')), date=Date(2013, 7, 1)),
            EnforcementDate(position=ref(None, '177', '3'), date=Date(2013, 7, 1)),
            EnforcementDate(position=ref(None, ('178', '179')), date=Date(2013, 7, 1)),
            EnforcementDate(position=ref(None, '180', '1', ('b', 'd')), date=Date(2013, 7, 1)),
            EnforcementDate(position=ref(None, '180', '2'), date=Date(2013, 7, 1)),
            EnforcementDate(position=ref(None, ('181', '196')), date=Date(2013, 7, 1)),
            EnforcementDate(position=ref(None, '197', ('1', '2')), date=Date(2013, 7, 1)),
            EnforcementDate(position=ref(None, '197', ('4', '5')), date=Date(2013, 7, 1)),
            EnforcementDate(position=ref(None, ('198', '199')), date=Date(2013, 7, 1)),
            EnforcementDate(position=ref(None, '200', ('1', '3')), date=Date(2013, 7, 1)),
            EnforcementDate(position=ref(None, '200', ('5', '6')), date=Date(2013, 7, 1)),
            EnforcementDate(position=ref(None, ('201', '204')), date=Date(2013, 7, 1)),
            EnforcementDate(position=ref(None, ('206', '208')), date=Date(2013, 7, 1)),
            EnforcementDate(position=ref(None, '212',), date=Date(2013, 7, 1)),
            EnforcementDate(position=ref(None, ('214', '217')), date=Date(2013, 7, 1)),
            EnforcementDate(position=ref(None, '220'), date=Date(2013, 7, 1)),
            EnforcementDate(position=ref(None, ('222', '224')), date=Date(2013, 7, 1)),
            EnforcementDate(position=ref(None, '228'), date=Date(2013, 7, 1)),
            EnforcementDate(position=ref(None, '230'), date=Date(2013, 7, 1)),
            EnforcementDate(position=ref(None, '232'), date=Date(2013, 7, 1)),
            EnforcementDate(position=ref(None, '233', '1', 'b'), date=Date(2013, 7, 1)),
            EnforcementDate(position=ref(None, '233', '2', ('a', 'c')), date=Date(2013, 7, 1)),
            EnforcementDate(position=ref(None, '233', '2', 'e'), date=Date(2013, 7, 1)),
            EnforcementDate(position=ref(None, ('235', '255')), date=Date(2013, 7, 1)),
            EnforcementDate(position=ref(None, ('257', '260')), date=Date(2013, 7, 1)),
            EnforcementDate(position=ref(None, '261', ('2', '5')), date=Date(2013, 7, 1)),
            EnforcementDate(position=ref(None, '261', '6', ('b', 'd')), date=Date(2013, 7, 1)),
            EnforcementDate(position=ref(None, ('262', '290')), date=Date(2013, 7, 1)),
            EnforcementDate(position=ref(None, '291', ('1', '2')), date=Date(2013, 7, 1)),
            EnforcementDate(position=ref(None, '291', ('4', '10')), date=Date(2013, 7, 1)),
            EnforcementDate(position=ref(None, ('292', '313')), date=Date(2013, 7, 1)),
            EnforcementDate(position=ref(None, ('315', '317')), date=Date(2013, 7, 1)),
        ),
    ),
    (
        "A 35. §, a 41–46. §, a 48. §, az 50. § a–i) pontja, az 50. § l–m) pontja, az 51. §, a 74. § (1) bekezdése, a 75–77. §, a 78. § a) és b) pontja, a 79–86. §, a 87. §, a 99–109. §, a 110. § a) pontja és a 146–148. § a kihirdetést követő 16. napon lép hatályba.",
        (
            EnforcementDate(position=ref(None, '35'), date=DaysAfterPublication(days=16)),
            EnforcementDate(position=ref(None, ('41', '46')), date=DaysAfterPublication(days=16)),
            EnforcementDate(position=ref(None, '48'), date=DaysAfterPublication(days=16)),
            EnforcementDate(position=ref(None, '50', None, ('a', 'i')), date=DaysAfterPublication(days=16)),
            EnforcementDate(position=ref(None, '50', None, ('l', 'm')), date=DaysAfterPublication(days=16)),
            EnforcementDate(position=ref(None, '51'), date=DaysAfterPublication(days=16)),
            EnforcementDate(position=ref(None, '74', '1'), date=DaysAfterPublication(days=16)),
            EnforcementDate(position=ref(None, ('75', '77')), date=DaysAfterPublication(days=16)),
            EnforcementDate(position=ref(None, '78', None, ('a', 'b')), date=DaysAfterPublication(days=16)),
            EnforcementDate(position=ref(None, ('79', '86')), date=DaysAfterPublication(days=16)),
            EnforcementDate(position=ref(None, '87'), date=DaysAfterPublication(days=16)),
            EnforcementDate(position=ref(None, ('99', '109')), date=DaysAfterPublication(days=16)),
            EnforcementDate(position=ref(None, '110', None, 'a'), date=DaysAfterPublication(days=16)),
            EnforcementDate(position=ref(None, ('146', '148')), date=DaysAfterPublication(days=16)),
        )
    ),
    (
        "Az 55–66. §, a 70. § és a 72. § a) pontja, a 73. § a) és b) pontja 2019. szeptember 1-jén lép hatályba.",
        (
            EnforcementDate(position=ref(None, ('55', '66')), date=Date(year=2019, month=9, day=1)),
            EnforcementDate(position=ref(None, '70'), date=Date(year=2019, month=9, day=1)),
            EnforcementDate(position=ref(None, '72', None, 'a'), date=Date(year=2019, month=9, day=1)),
            EnforcementDate(position=ref(None, '73', None, ('a', 'b')), date=Date(year=2019, month=9, day=1)),
        )
    ),
    (
        "A 33. §, a 47. §, az 50. § j–k) és n) pontja, a 74. § (2) bekezdése, a 78. § c) pontja, a 97. § és a 110. § b) pontja 2020. január 1-jén lép hatályba.",
        (
            EnforcementDate(position=ref(None, '33'), date=Date(year=2020, month=1, day=1)),
            EnforcementDate(position=ref(None, '47'), date=Date(year=2020, month=1, day=1)),
            EnforcementDate(position=ref(None, '50', None, ('j', 'k')), date=Date(year=2020, month=1, day=1)),
            EnforcementDate(position=ref(None, '50', None, 'n'), date=Date(year=2020, month=1, day=1)),
            EnforcementDate(position=ref(None, '74', '2', None), date=Date(year=2020, month=1, day=1)),
            EnforcementDate(position=ref(None, '78', None, 'c'), date=Date(year=2020, month=1, day=1)),
            EnforcementDate(position=ref(None, '97', None, None), date=Date(year=2020, month=1, day=1)),
            EnforcementDate(position=ref(None, '110', None, 'b'), date=Date(year=2020, month=1, day=1)),
        )
    ),
    (
        "Ez a törvény a kihirdetését követő hónap első napján lép hatályba.",
        (
            EnforcementDate(position=None, date=DayInMonthAfterPublication(day=1)),
        )
    ),
    (
        "Ez a törvény a kihirdetését követő hónap 15. napján lép hatályba.",
        (
            EnforcementDate(position=None, date=DayInMonthAfterPublication(day=15)),
        )
    ),
    (
        "Ez a törvény a kihirdetését követő második hónap első napján lép hatályba.",
        (
            EnforcementDate(position=None, date=DayInMonthAfterPublication(day=1, months=2)),
        )
    ),
    (
        "A 39–41. § a kihirdetést követő második hónap ötödik napján lép hatályba.",
        (
            EnforcementDate(position=ref(None, ('39', '41')), date=DayInMonthAfterPublication(day=5, months=2)),
        )
    ),
    (
        "Ez a törvény – a (2) bekezdésben meghatározott kivétellel – a kihirdetését követő napon lép hatályba, és 2019. december 31-én hatályát veszti.",
        (
            EnforcementDate(position=None, date=DaysAfterPublication(), repeal_date=Date(2019, 12, 31)),
        )
    ),
    (
        "Ez a törvény – a (2)–(5) bekezdésben foglalt kivétellel – a kihirdetését követő napon lép hatályba, és ez a törvény 2019. február 10-én a hatályát veszti.",
        (
            EnforcementDate(position=None, date=DaysAfterPublication(), repeal_date=Date(2019, 2, 10)),
        )
    ),
    (
        "Ez a törvény – a (2)–(9) bekezdésben meghatározott kivétellel – 2014. január 1-jén lép hatályba, és 2015. december 31-én hatályát veszti.",
        (
            EnforcementDate(position=None, date=Date(2014, 1, 1), repeal_date=Date(2015, 12, 31)),
        )
    ),
    (
        "Ez a törvény – a (2) bekezdésben meghatározott kivétellel – 2018. november 1-jén lép hatályba, és 2022. december 31-én hatályát veszti.",
        (
            EnforcementDate(position=None, date=Date(2018, 11, 1), repeal_date=Date(2022, 12, 31)),
        )
    ),
    (
        "A 4. § (2) bekezdése; a 9. § (2) bekezdése; a 12. § (2) bekezdése; a 21. §; a 28. § (7) bekezdése; a 29. § (1) bekezdése; a 31. § (2)–(3) bekezdése; a 32. § (2) bekezdése; a 34. § (2) bekezdése; a 40. § (3)–(4) bekezdése; a 42. § (1) bekezdése; a 47. § (2) bekezdése; a 63. § (2) bekezdése; a 65. § (1) bekezdése; a 69. § (4)–(5) bekezdése; a 76. § (7)–(8) bekezdése; a 81. § (1) bekezdése; a 84. § (1)–(2) bekezdése; a 87. §; a 96. § 2021. január 1-jén lép hatályba.",
        (
            EnforcementDate(position=ref(None, '4', '2'), date=Date(2021, 1, 1)),
            EnforcementDate(position=ref(None, '9', '2'), date=Date(2021, 1, 1)),
            EnforcementDate(position=ref(None, '12', '2'), date=Date(2021, 1, 1)),
            EnforcementDate(position=ref(None, '21'), date=Date(2021, 1, 1)),
            EnforcementDate(position=ref(None, '28', '7'), date=Date(2021, 1, 1)),
            EnforcementDate(position=ref(None, '29', '1'), date=Date(2021, 1, 1)),
            EnforcementDate(position=ref(None, '31', ('2', '3')), date=Date(2021, 1, 1)),
            EnforcementDate(position=ref(None, '32', '2'), date=Date(2021, 1, 1)),
            EnforcementDate(position=ref(None, '34', '2'), date=Date(2021, 1, 1)),
            EnforcementDate(position=ref(None, '40', ('3', '4')), date=Date(2021, 1, 1)),
            EnforcementDate(position=ref(None, '42', '1'), date=Date(2021, 1, 1)),
            EnforcementDate(position=ref(None, '47', '2'), date=Date(2021, 1, 1)),
            EnforcementDate(position=ref(None, '63', '2'), date=Date(2021, 1, 1)),
            EnforcementDate(position=ref(None, '65', '1'), date=Date(2021, 1, 1)),
            EnforcementDate(position=ref(None, '69', ('4', '5')), date=Date(2021, 1, 1)),
            EnforcementDate(position=ref(None, '76', ('7', '8')), date=Date(2021, 1, 1)),
            EnforcementDate(position=ref(None, '81', '1'), date=Date(2021, 1, 1)),
            EnforcementDate(position=ref(None, '84', ('1', '2')), date=Date(2021, 1, 1)),
            EnforcementDate(position=ref(None, '87'), date=Date(2021, 1, 1)),
            EnforcementDate(position=ref(None, '96'), date=Date(2021, 1, 1)),
        )
    ),
)

# TODO: Special
#    (
#        "A 234. § a Schengeni Információs Rendszer második generációjának(SIS II) létrehozásáról, működtetéséről "
#        "és használatáról szóló, 2006. december 20-i, 1987/2006/EK európai parlamenti és tanácsi rendelet 55. cikk "
#        "(2) bekezdésében meghatározott eljárás keretében, a SIS II alkalmazhatóságáról szóló tanácsi határozatban "
#        "foglalt napon lép hatályba.",
#        (
#            EnforcementDate(
#                position=ref(None, '234'),
#                date=SpecialEnforcementDate(
#                    "a Schengeni Információs Rendszer második generációjának(SIS II) létrehozásáról, működtetéséről "
#                    "és használatáról szóló, 2006. december 20-i, 1987/2006/EK európai parlamenti és tanácsi rendelet 55. cikk "
#                    "(2) bekezdésében meghatározott eljárás keretében, a SIS II alkalmazhatóságáról szóló tanácsi határozatban "
#                    "foglalt napon",
#                )
#            ),
#        ),
#    ),
#    (
#        "A 319. § az országgyűlési képviselők következő általános választását követően megalakuló Országgyűlés"
#        "alakuló ülésének napján lép hatályba.",
#        (
#            EnforcementDate(
#                position=ref(None, '234'),
#                date=SpecialEnforcementDate(
#                    "az országgyűlési képviselők következő általános választását követően megalakuló Országgyűlés alakuló ülésének napján"
#                )
#            ),
#        ),
#    ),
#
#    "Az 52–54 §, a 67–69. §, a 71. §, a 72. § b) és c) pontja, a 73. § c) pontja, a 88–89. §, a 111–113. §, a 116–119. §, "
#    "a 133–134. §, a 137–138. § és az 1. melléklet 2020. január 17-én lép hatályba."
#
# TODO: Simples
#    Ez a törvény – a (2)–(7) bekezdésben foglalt kivételekkel – 2013. január 1-jén lép hatályba.
#    44. §     (1)  Ez a törvény – a (2)–(3) bekezdésben foglalt kivétellel – a kihirdetését követő harmadik napon lép
#               hatályba.
#          (2)  Az 50–51. § és az 53. § (1)–(5) bekezdése e törvény kihirdetését követő 31. napon lép hatályba.
#
#    (1)  Ez a törvény – a (2) bekezdésben meghatározott kivételekkel – a kihirdetését követő napon lép hatályba.
#
#    (3)  A 4–6. § és a 48. § (1) bekezdése 2013. július 1-jén lép hatályba.
#
#    Ez a törvény a (2) és (3) bekezdésben meghatározott kivétellel a kihirdetését követő napon lép hatályba.
#
#    A 2. § és a 3. § a Megállapodás 6. Cikk (1) bekezdésében meghatározott időpontban lép hatályba.
#
#
#    TODO: appendix reference:
#    Az 1. § (1) bekezdése, a 2. §, az 5. §, a 9. §, a 14. §, a 15. §, a 17. §, a 114. §
#    és az 1. melléklet az e törvény kihirdetését követő 90. napon lép hatályba.
#
#    Az 1−68. §, a 70−75. §, a 78. § (1) és (2) bekezdése, a 80. § és az 1–14. melléklet
#    2013. július 1-jén lép hatályba.
#
#    TODO: stuctural reference:
#    A 3. és 6. alcím, valamint a (7) bekezdés 2013. június 30-án lép hatályba.
#    A VI. Fejezet 2014. október 1-jén lép hatályba.
#
#    TODO: multiple dates:
#    А 16. § (2) bekezdésének c), e), h)–j) pontja 2013. április 1-jén, d) pontja 2014. január 1-jén lép hatályba.
#


@pytest.mark.parametrize("s,correct_metadata", CASES)
def test_enforcement_date_parsing(s: str, correct_metadata: Tuple[EnforcementDate, ...]) -> None:
    parsed = GrammaticalAnalyzer().analyze(s, print_result=True)
    parsed_metadata = parsed.semantic_data
    assert correct_metadata == parsed_metadata
