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
from abc import ABC, abstractmethod
from typing import Type, Tuple, ClassVar, Optional, Mapping, Union, Iterable

import attr

from hun_law.utils import int_to_text_hun, int_to_text_roman, IndentedLine

# Main act on which all the code was based:
# 61/2009. (XII. 14.) IRM rendelet a jogszabályszerkesztésről

# Structuring levels (36. § (2)), and their Akoma Ntoso counterpart (at least IMO):
# a) az alpont,                         | subpoint
# b) a pont,                            | point
# c) a bekezdés,                        | paragraph
# d) a szakasz, [a.ka. paragrafus]      | article *
# e) az alcím,                          | subtitle
# f) a fejezet,                         | chapter
# g) a rész és                          | part
# h) a könyv.                           | book
#
# Additional levels for non-conformant laws, such as 2013. V (PTK):
#    cím                                | title
#
# * even though we call this level "sections" in hungarian (was "paragrafus")
# similar levels are called "section" in UK and US, but "Article" in EU Acts.

# Numbering is non-intuitive:
# Book 1
#   Part 1
#     Title 1
#       Article 1
#         Paragraph 1
#         Paragraph 2
#     Title 2
#       Article 2
#         Paragraph 1
#           Point a)
#           Point b)
#       Article 3
#         Point a)
#   Part 2
#     Title 3
#       Article 4
#       Article 5
#     Title 4
#       Article 6
# Book 2
#   Part 1
#     Title 1
#       Article 1
# ....

# Sometimes numbering are different, especially for older Acts.
# Also, sometimes a Part has Articles outside Titles (at the beginning)
# See 2013. V, 3:159. §

# For this reason, (and because they are so useless) we only handle structure levels,
# as mere 'titles', and don't use them in the code as actual structural things.

# All classes are immutable by design


@attr.s(slots=True, frozen=True)
class StructuralElement(ABC):
    identifier: str = attr.ib()
    title: str = attr.ib()

    @property
    @abstractmethod
    def formatted_identifier(self):
        pass


@attr.s(slots=True, frozen=True)
class Book(StructuralElement):
    # 38. §, Könyv
    # Example:
    # NYOLCADIK KÖNYV
    @property
    def formatted_identifier(self):
        return "{} KÖNYV".format(int_to_text_hun(int(self.identifier)).upper())


@attr.s(slots=True, frozen=True)
class Part(StructuralElement):
    # 39. § Rész
    # Example:
    # MÁSODIK RÉSZ
    # KÜLÖNÖS RÉSZ

    # 39. § (5)
    SPECIAL_PARTS = ('ÁLTALÁNOS RÉSZ', 'KÜLÖNÖS RÉSZ', 'ZÁRÓ RÉSZ', None)

    @property
    def formatted_identifier(self):
        # TODO: special parts
        return "{} RÉSZ".format(int_to_text_hun(int(self.identifier)).upper())


@attr.s(slots=True, frozen=True)
class Title(StructuralElement):
    # "CÍM"
    # Nonconformant structural type, present only in PTK
    # Example:
    # XXI. CÍM
    @property
    def formatted_identifier(self):
        # TODO: special parts
        return "{}. CÍM".format(int_to_text_roman(int(self.identifier)).upper())


@attr.s(slots=True, frozen=True)
class Chapter(StructuralElement):
    # 40. §,  fejezet
    # Example:
    # II. FEJEZET
    # IV. Fejezet
    # XXIII. fejezet  <=  not conformant, but present in e.g. PTK
    @property
    def formatted_identifier(self):
        # TODO: special parts
        return "{}. FEJEZET".format(int_to_text_roman(int(self.identifier)).upper())


@attr.s(slots=True, frozen=True)
class Subtitle(StructuralElement):
    # 41. §, Alcím
    # Guaranteed to be uppercase
    # Example:
    # 17. Az alcím
    #
    # For older acts, there is no number, only a text.

    @property
    def formatted_identifier(self):
        if not self.identifier:
            return ""
        # TODO: special parts
        return "{}.".format(self.identifier)


STRUCTURE_ELEMENT_TYPES = (
    Book,
    Part,
    Title,
    Chapter,
    Subtitle,
)


@attr.s(slots=True, frozen=True)
class InTextReference:
    # Start and end pos are python range, i.e. end_pos is after the last character
    start_pos: int = attr.ib()
    end_pos: int = attr.ib()
    reference: "Reference" = attr.ib()


@attr.s(slots=True, frozen=True)
class OutgoingReference:
    from_reference: "Reference" = attr.ib()
    # Start and end pos are python range, i.e. end_pos is after the last character
    start_pos: int = attr.ib()
    end_pos: int = attr.ib()
    to_reference: "Reference" = attr.ib()


@attr.s(slots=True, frozen=True)
class QuotedBlock:
    lines: Tuple[IndentedLine, ...] = attr.ib()
    identifier: ClassVar = None


SubArticleChildType = Union['Article', 'SubArticleElement', 'QuotedBlock']
@attr.s(slots=True, frozen=True)
class SubArticleElement(ABC):
    ALLOWED_CHILDREN_TYPE: ClassVar[Tuple[Type[SubArticleChildType], ...]] = ()

    identifier: Optional[str] = attr.ib(default=None)
    text: Optional[str] = attr.ib(default=None)
    intro: Optional[str] = attr.ib(default=None)
    children: Optional[Tuple[SubArticleChildType, ...]] = attr.ib(default=None)
    wrap_up: Optional[str] = attr.ib(default=None)

    children_type: Optional[Type[SubArticleChildType]] = attr.ib(init=False)
    children_map: Optional[Mapping[Optional[str], SubArticleChildType]] = attr.ib(init=False)

    @children_type.default
    def _children_type_default(self) -> Optional[Type[SubArticleChildType]]:
        if self.children is None:
            return None
        return type(self.children[0])

    @children_map.default
    def _children_map_default(self) -> Optional[Mapping[Optional[str], SubArticleChildType]]:
        if self.children is None:
            return None
        return {c.identifier: c for c in self.children}

    @text.validator
    def _content_validator_if_text(self, _attribute, text: Optional[str]):
        if text is not None:
            if self.intro is not None or self.wrap_up is not None or self.children is not None:
                raise ValueError("SAE can contain either text or intro/wrap-up/children")

    @children.validator
    def _content_validator_if_children(self, _attribute, children: Optional[Tuple['SubArticleElement', ...]]):
        if children is None:
            return
        if self.children_type not in self.ALLOWED_CHILDREN_TYPE:
            raise TypeError("Children of {} can only be {} (got {})".format(type(self), self.ALLOWED_CHILDREN_TYPE, self.children_type))
        for c in children:
            # We really do want type equality here, not "isintance".
            # pylint: disable=unidiomatic-typecheck
            if type(c) != self.children_type:
                raise TypeError(
                    "All children  has to be of the  same type ({} is not {})"
                    .format(type(c), self.children_type)
                )

    def child(self, child_id: str) -> SubArticleChildType:
        if self.children_map is None:
            raise KeyError("There are no children of this element")
        return self.children_map[child_id]

    @classmethod
    @abstractmethod
    def header_prefix(cls, identifier: Optional[str]) -> str:
        pass

    @classmethod
    @abstractmethod
    def next_identifier(cls, identifier: str) -> str:
        pass

    @property
    @abstractmethod
    def relative_reference(self) -> 'Reference':
        pass


@attr.s(slots=True, frozen=True)
class AlphabeticSubpoint(SubArticleElement):
    @classmethod
    def header_prefix(cls, identifier: Optional[str]) -> str:
        return "{}) ".format(identifier)

    @classmethod
    def next_identifier(cls, identifier: str) -> str:
        if len(identifier) == 1:
            return chr(ord(identifier) + 1)
        if len(identifier) == 2:
            return identifier[0] + chr(ord(identifier[1]) + 1)
        raise ValueError("Invalid identifier for subpoint '{}'".format(identifier))

    @property
    def relative_reference(self) -> 'Reference':
        return Reference(subpoint=self.identifier)


@attr.s(slots=True, frozen=True)
class NumericSubpoint(SubArticleElement):
    @classmethod
    def header_prefix(cls, identifier: Optional[str]) -> str:
        return "{}. ".format(identifier)

    @classmethod
    def next_identifier(cls, identifier: str) -> str:
        if identifier.isdigit():
            return str(int(identifier) + 1)
        number = identifier[:-1]
        postfix = identifier[-1]
        return number + chr(ord(postfix) + 1)

    @property
    def relative_reference(self) -> 'Reference':
        return Reference(subpoint=self.identifier)


@attr.s(slots=True, frozen=True)
class NumericPoint(SubArticleElement):
    ALLOWED_CHILDREN_TYPE = (AlphabeticSubpoint, )

    @classmethod
    def header_prefix(cls, identifier: Optional[str]) -> str:
        return "{}. ".format(identifier)

    def subpoint(self, sp_id: str) -> AlphabeticSubpoint:
        result = self.child(sp_id)
        assert isinstance(result, AlphabeticSubpoint)
        return result

    @classmethod
    def next_identifier(cls, identifier: str) -> str:
        if identifier.isdigit():
            return str(int(identifier) + 1)
        number = identifier[:-1]
        postfix = identifier[-1]
        return number + chr(ord(postfix) + 1)

    @property
    def relative_reference(self) -> 'Reference':
        return Reference(point=self.identifier)


@attr.s(slots=True, frozen=True)
class AlphabeticPoint(SubArticleElement):
    ALLOWED_CHILDREN_TYPE = (AlphabeticSubpoint, NumericSubpoint, )

    @classmethod
    def header_prefix(cls, identifier: Optional[str]) -> str:
        return "{}) ".format(identifier)

    def subpoint(self, sp_id: str) -> Union[AlphabeticSubpoint, NumericSubpoint]:
        result = self.child(sp_id)
        assert isinstance(result, (AlphabeticSubpoint, NumericSubpoint))
        return result

    @classmethod
    def next_identifier(cls, identifier: str) -> str:
        if identifier == 'ny':
            return 'o'
        if identifier == 'sz':
            return 't'
        return chr(ord(identifier) + 1)

    @property
    def relative_reference(self) -> 'Reference':
        return Reference(point=self.identifier)


@attr.s(slots=True, frozen=True)
class BlockAmendment(SubArticleElement):
    ALLOWED_CHILDREN_TYPE: ClassVar[Tuple[Type[SubArticleChildType], ...]] = ()  # Will be defined later in this file, since it uses classes defined later.

    @classmethod
    def header_prefix(cls, identifier: Optional[str]) -> str:
        raise TypeError("Block Amendments do not have header")

    @classmethod
    def next_identifier(cls, identifier: str) -> str:
        raise TypeError("Block Amendments do not have identifiers")

    @property
    def relative_reference(self) -> 'Reference':
        raise TypeError("Block Amendments cannot be referred to.")


@attr.s(slots=True, frozen=True)
class Paragraph(SubArticleElement):
    ALLOWED_CHILDREN_TYPE = (AlphabeticPoint, NumericPoint, QuotedBlock, BlockAmendment)

    @classmethod
    def header_prefix(cls, identifier: Optional[str]) -> str:
        if identifier is None:
            # Happens in special cases when no header was found, e.g.
            # Came from an article with a single paragraph.
            return ''
        return "({}) ".format(identifier)

    def point(self, point_id: str) -> Union[AlphabeticPoint, NumericPoint]:
        result = self.child(point_id)
        if not isinstance(result, (AlphabeticPoint, NumericPoint)):
            raise KeyError("Selected child is not a Point")
        return result

    def quoted_block(self, block_num) -> QuotedBlock:
        if self.children is None:
            raise KeyError("There are no children")
        result = self.children[block_num]
        if not isinstance(result, QuotedBlock):
            raise KeyError("Selected child is not a QuotedBlock")
        return result

    def block_amendment(self) -> BlockAmendment:
        if self.children is None or len(self.children) == 0:
            raise KeyError("There are no children")
        result = self.children[0]
        if not isinstance(result, BlockAmendment):
            raise KeyError("Selected child is not a BlockAmendment")
        assert len(self.children) == 1, "There should be exactly one block amendment per paragraph"
        return result

    @classmethod
    def next_identifier(cls, identifier: str) -> str:
        if identifier.isdigit():
            return str(int(identifier) + 1)
        number = identifier[:-1]
        postfix = identifier[-1]
        return number + chr(ord(postfix) + 1)

    @property
    def relative_reference(self) -> 'Reference':
        return Reference(paragraph=self.identifier)


@attr.s(slots=True, frozen=True)
class Article:
    identifier: str = attr.ib()
    children: Tuple[Paragraph, ...] = attr.ib()
    title: Optional[str] = attr.ib(default=None)

    paragraph_map: Mapping[Optional[str], Paragraph] = attr.ib(init=False)

    @children.validator
    def _children_validator(self, _attribute, children: Tuple[Paragraph, ...]):
        # Attrs validators as decorators are what they are, it cannot be a function.
        # pylint: disable=no-self-use
        for c in children:
            if c.identifier is None:
                if len(children) != 1:
                    raise ValueError("Unnamed paragraphs cannot have siblings.")

    @paragraph_map.default
    def _paragraph_map_default(self) -> Mapping[Optional[str], Paragraph]:
        return {c.identifier: c for c in self.children}

    @property
    def paragraphs(self) -> Tuple[Paragraph, ...]:
        # Children are always paragraphs (see constructor)
        return self.children

    def paragraph(self, paragraph_id: Optional[str] = None):
        if paragraph_id is not None:
            return self.paragraph_map[paragraph_id]
        return self.paragraph_map[None]

    @classmethod
    def next_identifier(cls, identifier: str) -> str:
        if "/" in identifier:
            prefix, letter = identifier.split('/')
            return "{}/{}".format(prefix, chr(ord(letter) + 1))
        if ":" in identifier:
            book, num = identifier.split(":")
            # "1:234/A" like cases are already handled above
            return "{}:{}".format(book, int(num) + 1)
        return str(int(identifier) + 1)

    @property
    def relative_reference(self) -> 'Reference':
        return Reference(article=self.identifier)


BlockAmendment.ALLOWED_CHILDREN_TYPE = (Article, Paragraph, AlphabeticPoint, NumericPoint, AlphabeticSubpoint, NumericSubpoint)


@attr.s(slots=True, frozen=True)
class Act:
    identifier: str = attr.ib()
    subject: str = attr.ib()
    preamble: str = attr.ib()
    children: Tuple[Union['StructuralElement', 'Article'], ...] = attr.ib()

    act_id_abbreviations: Optional[Tuple['ActIdAbbreviation']] = attr.ib(default=None)
    outgoing_references: Optional[Tuple['OutgoingReference', ...]] = attr.ib(default=None)

    articles: Tuple[Article, ...] = attr.ib(init=False)
    articles_map: Mapping[str, Article] = attr.ib(init=False)

    @articles.default
    def _articles_default(self) -> Tuple[Article, ...]:
        return tuple(c for c in self.children if isinstance(c, Article))

    @articles_map.default
    def _articles_map_default(self):
        return {c.identifier: c for c in self.articles}

    def article(self, article_id: str) -> Article:
        assert self.articles_map[str(article_id)].identifier == str(article_id)
        return self.articles_map[str(article_id)]

    def outgoing_references_from(self, reference: 'Reference') -> Iterable['OutgoingReference']:
        if self.outgoing_references is None:
            return ()
        return (r for r in self.outgoing_references if r.from_reference == reference)


ReferencePartType = Union[None, str, Tuple[str, str]]
@attr.s(slots=True, frozen=True)
class Reference:
    act: Optional[str] = attr.ib(default=None)
    article: ReferencePartType = attr.ib(default=None)
    paragraph: ReferencePartType = attr.ib(default=None)
    point: ReferencePartType = attr.ib(default=None)
    subpoint: ReferencePartType = attr.ib(default=None)

    def is_relative(self) -> bool:
        return self.act is None

    def is_range(self) -> bool:
        return (
            isinstance(self.article, tuple) or
            isinstance(self.paragraph, tuple) or
            isinstance(self.point, tuple) or
            isinstance(self.subpoint, tuple)
        )

    def relative_to(self, other: 'Reference') -> 'Reference':
        params = []
        my_part = False
        for key in ("act", "article", "paragraph", "point", "subpoint"):
            if getattr(self, key) is not None:
                my_part = True
            params.append(getattr(self if my_part else other, key))
        return Reference(*params)

    @property
    def relative_id_string(self) -> str:
        result = "ref"
        for key, id_key in (("article", "a"), ("paragraph", "p"), ("point", "pt"), ("subpoint", "sp")):
            val = getattr(self, key)
            if val is not None:
                if isinstance(val, tuple):
                    val = val[0]
                result = "{}_{}{}".format(result, id_key, val)
        return result

    def first_in_range(self) -> 'Reference':
        result = self
        if isinstance(result.article, tuple):
            result = attr.evolve(result, article=result.article[0])
        if isinstance(result.paragraph, tuple):
            result = attr.evolve(result, paragraph=result.paragraph[0])
        if isinstance(result.point, tuple):
            result = attr.evolve(result, point=result.point[0])
        if isinstance(result.subpoint, tuple):
            result = attr.evolve(result, subpoint=result.subpoint[0])
        return result

    def last_component_with_type(self) -> Tuple[ReferencePartType, Optional[Type]]:
        # Thanks pylint, but this is the simplest form of this function.
        # pylint: disable=too-many-return-statements
        if self.subpoint is not None:
            first_subpoint_id = self.subpoint[0] if isinstance(self.subpoint, tuple) else self.subpoint
            if first_subpoint_id[0].isdigit():
                # Both 1, 12, and 3a are NumericSubpoints.
                return self.subpoint, NumericSubpoint
            return self.subpoint, AlphabeticSubpoint
        if self.point is not None:
            first_point_id = self.point[0] if isinstance(self.point, tuple) else self.point
            if first_point_id[0].isdigit():
                # Both 1, 12, and 3a are NumericPoints.
                return self.point, NumericPoint
            return self.point, AlphabeticPoint
        if self.paragraph is not None:
            return self.paragraph, Paragraph
        if self.article is not None:
            return self.article, Article
        if self.act is not None:
            return self.act, Act
        return None, None


@attr.s(slots=True, frozen=True)
class ActIdAbbreviation:
    abbreviation: str = attr.ib()
    act: str = attr.ib()


@attr.s(slots=True, frozen=True)
class BlockAmendmentMetadata:
    amended_reference: Optional[Reference] = attr.ib(kw_only=True, default=None)
    inserted_reference: Optional[Reference] = attr.ib(kw_only=True, default=None)

    def __attrs_post_init__(self):
        if self.amended_reference is None and self.inserted_reference is None:
            raise ValueError("A BlockAmendmentMetadata object has to contain at least an amendment or an insertion")
