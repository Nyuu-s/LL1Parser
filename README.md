☕ An LL1 Parser and Parsing table generator ☕

Reads a grammar file, creates a parsing table, then parse an input file.
The starting rule name must be specified.

Altough the grammar parser technically handles the "Any Order" construct, it is recommend to use it for very simple usecase as it can lead to unhandled ambigious grammars.

No AST nor parse tree are built during parsing, it's essentially a syntax checker as of right now ✅

Grammar file special syntax:
-Rule names are followed by the = symbol.
-(Recommended) seperate each symbol with spaces
-Terminals are between double quotes: "something"
-Non Terminals are not between quotes and can contains eaither - or _ 
-Groups are made with parenthesis ( )
-Optional rules are made with [ ]
-Repetition rules are made with { }* or { }+ where * is for 0 or more reptition and + is for 1 or more.
-Any order is made with || taking their immediate neigbours from left and right and you can combine them (e.g: A || B or A || B || C...  are valid) IF YOU WANT MORE THAN 1 SYMBOL TO BE PART OF THE ANYORDER GROUP THEM !
-Choices are made with | they represent a single choice from many, they're taking their immediate neigbours from left and right and you can combine them  (e.g: A | B or A | B | C are valid ) IF YOU WANT MORE THAN 1 SYMBOL TO BE PART OF A CHOICE GROUP THEM !

Some lore:

This project was the 1st version of the LegacySearchEngine project.
Initially trying to parse the COBOL language, I unfortuatly made 2 mistakes:
- Chosing python as main language.
- Chosing the LL1 parsing technique for the COBOL grammar.

The COBOL grammar has some constructs that was too painful and annoying to workaround. Like the fact that a given rule may have serval formats (in a way that isn't just a simple choice, formats may have the same first symbols making the grammar ambigious). 

This alone would be managable with some left refactoring of some sort. But combined with the "Any order" construct that lets non terminal come in any order in a rule its making some rules very tricky to tackle down correctly. (e.g file-control-entry, it has multiple formats depending on - but not only - what kind of ORGANISATION there is to allow some rules or not, but the ORGANISATION symbol may appear in any order inside that rule... not a particular predictive behaviour for a predictive parser 🤔 )
