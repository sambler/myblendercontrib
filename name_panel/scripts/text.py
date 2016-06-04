
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the Free
#  Software Foundation; either version 2 of the License, or (at your option)
#  any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT
#  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
#
#  You should have received a copy of the GNU General Public License along with
#  this program; if not, write to the Free Software Foundation, Inc.,
#  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

cheatsheet = r'''
Special Characters

  \        Escape special characters or start a sequence.

  .        Matches any character. ('.*' matches everything in a name.)

  ^        Matches beginning of string.

  $        Matches end of string.

  [3a-c]   Matches any characters '3', 'a', 'b' or 'c'.

  [^3a-c]  Matches any characters except '3', 'a', 'b' or 'c'.

  a|b      matches either a or b.


Quantifiers

  *        0 or more. (append ? for fewest)

  +        1 or more. (append ? for fewest)

  ?        0 or 1. (append ? for fewest)

  {m}      Exactly m occurrences.

  {m, n}   From m to n, m defaults to 0, n defaults to infinity.

  {m, n}?  From m to n, as few as possible.


Special Sequences

  \A       Start of string.

  \b       Matches empty string at word boundary. (between \w and \W)

  \B       Matches empty string not at word boundary.

  \d       A digit.

  \D       A non-digit.

  \s       Whitespace.

  \S       Non-whitespace.

  \w       Alphanumeric, Same as: [0-9a-zA-Z_]

  \W       Non-alphanumeric.

  \Z       End of name.


Groups

  ()             Creates a capture group and indicates precedence.

  \1             Recall first captured group, change accordingly.

  (?P<name>...)  Creates a group with the id of 'name'.

  \g<id>         Matches a previously defined group.

  (?(id)yes|no)  Match 'yes' if group 'id' matched, else 'no'.


Examples

(1) String: 'Name.001'

    Find: \W[0-9]*$

    Result: 'Name'

    This expression will strip any numbers at the tail end of a name up to and
    including any non-alphanumeric character.

    The individual characters used are;

    \W    Non-alphanumeric. (any character other then [0-9a-zA-Z_])

    [0-9] Character class from range 0 through 9.

    *     Anything preceding this symbol will be matched until no other matches
          are found.

    $     Indicates that we want to start from the end of the string.


(2) String: 'Name.001'

    Find: ([A-z]*\.)

    Replace: Changed_\1

    Result: 'Changed_Name.001'

    This expression will create a capture group of any characters and a . (dot)
    replace those characters with 'Changed_' infront of that captured group.

      The individual characters used are;

      (     Start a capture group.

      [A-z] Character class range A-z (upper and lowercase).

      *     Anything preceding this symbol will be matched until no other
            matches are found.

      \.    Used here to escape the character . (dot) which has special
            meaning in regular expressions.

      )     End a capture group.

      \1    Recall first captured group.





  Regular expressions are much like a tiny programming language, this cheatsheet
  will help get you started.

  For a more complete documentation of python related regular expressions;

    https://docs.python.org/3.5/library/re.html
'''
