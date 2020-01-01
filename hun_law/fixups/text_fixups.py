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


# The whole module is a bunch of fixups to existing Acts, that aren't
# well-formed enough to be parsed by the parser out-of-the-box

from .common import add_fixup, replace_line_content, add_empty_line_after, ptke_article_header_fixer, delete_line
from .replacement_fixups import replacement_fixups

# Title IV not found otherwise
add_fixup("2013. évi V. törvény", add_empty_line_after("A SZERZŐDÉS ÁLTALÁNOS SZABÁLYAI"))

# Article titles starting before the article sign.
# See ptke_article_header_fixer source for details
add_fixup("2013. évi CLXXVII. törvény", ptke_article_header_fixer)

# Botched merge between two range insertion amendments
add_fixup("2011. évi CLXIX. törvény", replace_line_content(
    "(2) Az Mktv. 36. §-a a következő (4)–(6) bekezdéssel egészül ki:",
    "(2) Az Mktv. 36. §-a a következő (4)–(9) bekezdéssel egészül ki:"
))
add_fixup("2011. évi CLXIX. törvény", replace_line_content(
    "adatot át kell adni az NMHH részére, amely azokat tárolja és kezeli.”",
    "adatot át kell adni az NMHH részére, amely azokat tárolja és kezeli."
))
add_fixup("2011. évi CLXIX. törvény", delete_line(
    "„(3) Az Mktv. 36. §-a a következő (7)–(9) bekezdéssel egészül ki:"
))
add_fixup("2011. évi CLXIX. törvény", replace_line_content(
    "„(7) 2012. január 1-je előtt a kiskorúak védelme érdekében",
    "(7) 2012. január 1-je előtt a kiskorúak védelme érdekében",
))

add_fixup("2013. évi LXXVIII. törvény", delete_line(
    "212/A. §"
))
add_fixup("2013. évi LXXVIII. törvény", replace_line_content(
    "(1) Aki gyermekének szülője, továbbá az elkövetéskor vagy korábban vele közös háztartásban vagy egy lakásban",
    "212/A. § (1) Aki gyermekének szülője, továbbá az elkövetéskor vagy korábban vele közös háztartásban vagy egy lakásban"
))

for act_id, replacements in replacement_fixups.items():
    for replace_args in replacements:
        # TODO: correct typing for this call. Replacements will probably need to
        # be an attrs class instead of the current dict hack.
        add_fixup(act_id, replace_line_content(**replace_args))  # type: ignore
