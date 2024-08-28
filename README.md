# Xapian Spelling Suggestions – Proof of Concept

_Xapian's spelling suggestion feature handles some common misspellings in German_


The reference implementation of the ZIM specification – libzim[^1] –
is written in C++ and uses Xapian[^2] for providing search
functionality. While the implementation is being case insensitive and
lenient in terms accentuation of search terms, misspellings of search
queries are not tolerated. Beyond handling of typos, especially for
dictionary content where a user is searching for ZIM entries
explaining the correct spelling of a word in the first place, this is
a substantial limitation.

The test case in this project illustrates for German as an example,
that Xapian's builtin functionality of providing spelling suggestions
would be sufficient to handle common misspellings as conducted by
people learning German, either as their first or as a second language.


[^1]: https://github.com/openzim/libzim
[^2]: https://xapian.org/
