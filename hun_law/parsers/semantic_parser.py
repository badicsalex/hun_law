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

import re
from typing import List, Iterable

import attr

from hun_law.structure import \
    Act, Article, Paragraph, QuotedBlock, BlockAmendment, StructuralElement, \
    Reference, OutgoingReference, InTextReference,\
    BlockAmendmentMetadata, \
    ActIdAbbreviation, SubArticleChildType
from .structure_parser import BlockAmendmentStructureParser, SubArticleParsingError
from .grammatical_analyzer import GrammaticalAnalyzer


@attr.s(slots=True)
class SemanticParseState:
    analyzer: GrammaticalAnalyzer = attr.ib(factory=GrammaticalAnalyzer)
    act_id_abbreviations: List[ActIdAbbreviation] = attr.ib(factory=list)
    outgoing_references: List[OutgoingReference] = attr.ib(factory=list)


class ActSemanticsParser:
    INTERESTING_SUBSTRINGS = (")", "§", "törvén")

    @classmethod
    def parse(cls, act: Act) -> Act:
        # TODO: Rewrite this to be more functional instead of passing
        # a mutable state
        state = SemanticParseState()
        for article in act.articles:
            for paragraph in article.paragraphs:
                cls.recursive_parse(paragraph, article.relative_reference, "", "", state)
        return attr.evolve(
            act,
            act_id_abbreviations=tuple(state.act_id_abbreviations),
            outgoing_references=tuple(state.outgoing_references)
        )

    @classmethod
    def recursive_parse(
            cls,
            element: SubArticleChildType,
            parent_reference: Reference,
            prefix: str, postfix: str,
            state: SemanticParseState
    ) -> None:
        # TODO: pylint is right here, should refactor.
        #pylint: disable=too-many-arguments
        if isinstance(element, (QuotedBlock, BlockAmendment, Article, StructuralElement)):
            return
        element_reference = element.relative_reference.relative_to(parent_reference)
        if element.text is not None:
            cls.parse_text(element.text, prefix, postfix, element_reference, state)
            return

        # First parse the intro of this element, because although we will
        # parse the same text when in context of the children, we throw away
        # the intro part of the result there.

        # TODO: Not using the children and postfix here is a huge hack. This code is reached for
        # Points and SubPoints, so most of the time these are partial sentences,
        # e.g
        # From now on
        #     a) things will change
        #     b) everything will be better.
        #
        # In this case, we hope that the string "From now on" can be parsed without
        # the second part of the sentence.
        assert element.intro is not None
        cls.parse_text(element.intro, prefix, '', element_reference, state)

        # TODO: Parse the wrap up of "this element"

        if element.intro is not None:
            prefix = prefix + element.intro + " "

        if element.wrap_up is not None:
            postfix = " " + element.wrap_up + postfix

        assert element.children is not None
        for child in element.children:
            cls.recursive_parse(child, element_reference, prefix, postfix, state)

    @classmethod
    def parse_text(cls, middle: str, prefix: str, postfix: str, element_reference: Reference, state: SemanticParseState) -> None:
        # TODO: pylint is right here, should refactor.
        #pylint: disable=too-many-arguments
        text = prefix + middle + postfix
        if len(text) > 10000:
            return
        if not any(s in text for s in cls.INTERESTING_SUBSTRINGS):
            return

        analysis_result = state.analyzer.analyze(text)

        state.act_id_abbreviations.extend(analysis_result.act_id_abbreviations)

        state.outgoing_references.extend(cls.convert_parsed_references(
            analysis_result.all_references,
            element_reference,
            len(prefix), len(text) - len(postfix),
            state
        ))
        # TODO: parse block amendments, and return interesting results
        return

    @classmethod
    def convert_parsed_references(
            cls,
            parsed_references: Iterable[InTextReference],
            element_reference: Reference,
            prefixlen: int,
            textlen: int,
            state: SemanticParseState
    ) -> Iterable[OutgoingReference]:
        # TODO: pylint is right here, should refactor.
        #pylint: disable=too-many-arguments
        result = []
        abbreviations_map = {a.abbreviation: a.act for a in state.act_id_abbreviations}
        for in_text_reference in parsed_references:
            # The end of the parsed reference is inside the target string
            # Checking for the end and not the beginning is important, because
            # we also want partial references to work here.
            if in_text_reference.end_pos <= prefixlen or in_text_reference.end_pos > textlen:
                continue

            result.append(
                OutgoingReference(
                    from_reference=element_reference,
                    start_pos=max(in_text_reference.start_pos - prefixlen, 0),
                    end_pos=(in_text_reference.end_pos - prefixlen),
                    to_reference=in_text_reference.reference.resolve_abbreviations(abbreviations_map)
                )
            )
        result.sort()
        return result


class ActBlockAmendmentParser:
    @classmethod
    def parse(cls, act: Act) -> Act:
        new_children = []
        for child in act.children:
            if isinstance(child, Article):
                child = cls.parse_article(child)
            new_children.append(child)
        return attr.evolve(act, children=tuple(new_children))

    @classmethod
    def parse_article(cls, article: Article) -> Article:
        new_children = []
        for paragraph in article.paragraphs:
            new_children.append(cls.parse_paragraph(paragraph))
        return attr.evolve(article, children=tuple(new_children))

    @classmethod
    def parse_paragraph(cls, paragraph: Paragraph) -> Paragraph:
        if paragraph.children_type != QuotedBlock:
            return paragraph
        assert paragraph.children is not None
        assert paragraph.intro is not None
        if len(paragraph.intro) > 10000:
            return paragraph
        # TODO: We don't currently parse structural amendments properly in the
        # structural step.
        # Block amendements have a two-part intro, which we unfortunately merge:
        #    Az Eurt.tv. 9. § (5) bekezdés c) pontja helyébe a következő rendelkezés lép:
        #   (Nem minősül függetlennek az igazgatótanács tagja különösen akkor, ha)
        #   „c) a társaság olyan részvényese, aki közvetve vagy közvetlenül a leadható szavazatok...
        #
        # Also, its sometimes bracketed with [] instead of ()

        matches = re.match(r"^(.*:) ?(\(.*\)|\[.*\])$", paragraph.intro)
        context_intro = None
        context_outro = None
        if matches is None:
            actual_intro = paragraph.intro
        else:
            actual_intro = matches.group(1)
            context_intro = matches.group(2)[1:-1]
            if paragraph.wrap_up is not None:
                context_outro = paragraph.wrap_up[1:-1]

        # TODO: Maybe cache?
        analysis_result = GrammaticalAnalyzer().analyze(actual_intro).special_expression
        if not isinstance(analysis_result, BlockAmendmentMetadata):
            return paragraph

        assert len(paragraph.children) == 1

        try:
            block_amendment = BlockAmendmentStructureParser.parse(
                analysis_result,
                context_intro, context_outro,
                paragraph.quoted_block(0).lines
            )
        except SubArticleParsingError:
            # TODO: There are many unhandled cases right now, but don't stop
            # parsing just because this. Leave the whole thing as a QuotedLines
            # for now
            return paragraph
        return attr.evolve(paragraph, intro=actual_intro, wrap_up="", children=(block_amendment,))
