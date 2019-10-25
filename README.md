# Deoxyribose
The DNA-themed programming language all the kids are talking about

## Introducing Deoxyribose

Deoxyribose is a stack-based esoteric programming language based on the syntax
and function of DNA.

A valid deoxyribose program is made up entirely of the letters A, C, G, and T,
which form three-digit **codons** in accordance with the
[DNA codon table](https://en.wikipedia.org/wiki/DNA_codon_table).
These codons correspond to stack or flow-control operations. All other
characters are ignored, making the language suitable for polyglots and other
such fun things.

Interestingly, the correspondence between codons and operations is
**degenerate**, so there's more than one way to write each operator, just like
in the real genetic code.

Execution of Deoxyribose takes place on a closed circle of DNA (like the
bacterial genome).
Any amount of information can be placed before the first start codon, and if no
stop codon is found, execution will loop around to the very beginning.
Clever use of the frameshifts this can lead to, combined with the degeneracy of
the codon–amino acid correspondence, can allow some very fun and exciting
things.

The name of the language was selected due to being the "most-DNA-y" word that
doesn't contain an A, C, G, or T, meaning it can be included in a comment or
shebang (`#! /usr/bin/env deoxyribose` is a valid comment).

## Amino acids (operators)

The operators are defined by their correspondence to particular amino acids, as
follows.

### Special codons
* **Start** (`ATG`): Start program execution
* **Stop** (`TAG`, `TAA`, and `TGA`): *End* program execution & return 0

### Charged amino acids — Single-stack operations
* **His**: *Push* next codon (expressed in quaternary notation, see below) to
  the top of the main stack
* **Lys**: *Pop* top of main stack to standard output as a number
* **Arg**: *Pop* top of main stack to standard output as a Unicode character
* **Glu**: *Dupe* (duplicate) the top element of the main stack
* **Asp**: *Drop* the top element of the main stack

### Non-polar amino acids — Two-stack/variable operations
* **Leu**: *Plus* (add) the top elements of the main and auxiliary stacks,
  remove these elements, and place the result on top of the main stack
* **Ile**: *Minus* (subtract) the top element of the auxiliary stack from the
  top element of the main stack, remove these elements, and place the result on
  top of the main stack
* **Val**: *Mul* (multiply) the top elements of the main and auxiliary stacks,
  remove these elements, and place the result on top of the main stack
* **Pro**: *Divide* the top element of the main stack by the top element
  of the auxiliary stack, remove these elements,
  and place the result on top of the main stack
* **Phe**: *Join* (concatenate) the main and auxiliary stacks by placing the
  auxiliary stack on top of the main stack, leaving the auxiliary stack empty
* **Gly**: *Move* the top element of the main stack to the top of the auxiliary
  stack
* **Ala**: *Modulo* — calculate the remainder when the top element of the main
  stack is divided by the top element of the auxiliary stack, remove both of
  these elements, and place the result on top of the main stack
* **Trp**: *Keep* (store) the top element of the main stack in the variable
  named by the next codon; using with an empty stack clears the variable
* **Met**:  *Reed* (read) the variable named by the next codon, and move its
  value to the top of the main stack; this clears the variable

### Polar amino acids — Flow control
* **Cys**: *Jump* – Jump to the *next* occurrence of the next codon
* **Asn**: *Loop* – Jump backwards to the *previous* occurrence of the next
  codon
* **Ser**: *Jump if <=0* – If the top element of the main stack is less than or
  equal to zero, jump to the *next* occurrence of the next codon
* **Thr**: *Loop if <=0* – If the top element of the main stack is less than or
  equal to zero, jump to the *previous* occurrence of the next codon
* **Tyr**: *Jump if null* – If the main stack is empty, jump to the *next*
  occurrence of the next codon
* **Gln**: *Loop if null* – If the main stack is empty, jump to the *previous*
  occurrence of the next codon

Note that the length of these jumps need not always be a multiple of three. This
can cause frameshifts, which are half the fun.

## Integer literals

Integer literals are expressed as a three-digit number in base-4, such that
`A` = 0, `C` = 1, `G` = 2, and `T` = 3. This limits integer literals to the
range `AAA` (0) to `TTT` (63).

Once stored inside the stack, values are not subject to these same limits, and
are treated just like ordinary Python numbers. Larger values, floats, and
negative numbers can therefore be constructed using mathematical operations.

Unicode characters can be stored as their character reference and converted back
by arginine. There is no built-in string (or array) datatype, nor any real
distinction between ints and floats, only numbers ordered on the stack.

## Variables

Deoxyribose programs primarily store values in two stacks,
usually referred to as the main and auxiliary stacks.
Operations are applied to the values on top of one or both of these stacks,
and a number of operations are dedicated to shunting values between them.

In addition,
as of Deoxyribose 3.0,
it is possible to declare up to 64 variables
with single-codon names.
Each variable can hold a single integer,
which must be read back into the stack in order to be operated on.
This significantly simplifies many algorithms,
but makes everything a bit less fun.
Every use of a variable requires at least four codons,
and the variable operations correspond to the two least degenerate amino acids,
so they should be used sparingly in golfy code.

## Examples

Note that the examples below include spaces to separate segments of the code for
readability; these are unnecessary, ignored by the interpreter, and excluded
from the given byte counts.

The multi-line explanations given below each example will not run as expected
unless all A, C, G, and T characters (case-insensitive) are removed from the
comments; all other comment characters are fine.

These examples generally implement a naïve and accessible approach to a problem,
in order to demonstrate the power and concept of programming in Deoxyribose.
These solutions may be suboptimal in terms of performance and byte count.
Golfing them down is left as an exercise to the reader (but the reader is
encouraged to submit shorter solutions as pull requests).

### Hello, world!

`ATG CATGAC CACTTTCACGCCGGTTTA ... CATTTTCATAGCGGTTTG AGATATATTAATTTG`
(Truncated because it's long and boring, actually prints `Hd!`)

Accepts no input; prints `Hello, world!` to STDOUT.

```
ATG ==>                     End

CAT Push
GAC 33 (!)

CAC Push
TTT 63
CAC Push
GCC 37
GGT Move
TTA Plus (= 100, d)

...

CAT Push
TTT 63
CAT Push
AGC 9
GGT Move
TTG Plus (= 72, H)

AGA Pop
TAT Jump if null
ATT *
AAT Loop                    *
TTG
```

### Infinite Fibonacci sequence

`ATG CCTGAA GGT GAATTA TGGAAA GGC ATGAAA GAAAAA AATGGT` (45 B)

Accepts no input; prints an infinite series of newline-separated integers to
STDOUT. The printed sequence starts at 2, but it would be trivial to add the
expected `1\n1\n` at the expense of a few more bytes.

```
ATG ==>

CCT Divide (yields 1)
GAA Dupe

GGT Move
 *
GAA Dupe
TTA Plus

TGG Keep
AAA b

GGC Move

ATG Reed
AAA b

GAA Dupe
AAA Pop

AAT Loop
GGT <- *
```

### Cat

`ATG GGT TATTGT AATATGT TTT AGA TATTCT AATTTTCT TA` (41 B)

Accepts any number of characters or Unicode codepoints as arguments; prints its
input to the screen.
If the input contains spaces, these will be stripped unless the string is
wrapped in quotes.
Input containing numbers is fine, but entirely numeric input will be converted
into the corresponding Unicode character (e.g. input of `100` prints `d`).

```
  ATG GGT TATTGT AATATGT TTT AGA TATTCT AATTTTCT TA
      ^                  *   %                   +
0 ==> Mov IfN->* Loop<^                          End
+1                       Joi Uni IfN->+ Loop<%
```

### Print integers from 1 to N

`ATG GGT CATAAC GAAGGTCCT GAAAAA CATAAC GGTTTATTTGAAGGTGGT GAAATT AGTTAG
TAG GAT AATCCT` (75 B)

Accepts an integer *N* as input; prints all integers from 1 to *N* to STDOUT,
separated by newlines.

```
ATG ==>

GGT Move

CAT Push
AAC 1

GAA Dupe
GGT Move
CCT Divide
 +
GAA Dupe
AAA Pop

CAT Push
AAC 1

GGT Move
TTA Plus
TTT Join
GAA Dupe
GGT Move
GGT Move

GAA Dupe
ATT Minus

AGT Jump if <= 0
TAG -> *

TAG End
 *
GAT Drop

AAT Loop
CCT <- +
```

### Primality test

`ATG GAA CATAAG GAGGGTGGC GCT CATAAC GGT AGTGAC GAT GAATTTGGTTTA AATAAG GAAGAC
GATTTTGATGGTATT AGTTAG CATAAA AAA TAG CATAAC AA` (107 B)

Accepts one integer greater than 1 as input; prints 1 if prime, 0 if composite.

```
    0            +1
ATG ==>

GAA Dupe         END

CAT Push
AAG 2
 +
GAG Dupe
GGT Move
GGC Move

GCT Modulo

CAT Push
AAC 1

GGT Move

AGT Jump if <= 0
GAC -> *

GAT Drop

GAA Dupe
TTT Join
GGT Move
TTA Plus

AAT Loop
AAG <- +

GAA Dupe
GAC Drop
 *
GAT Drop
TTT Join
GAT Drop
GGT Move
ATT Minus

AGT Jump if <= 0
TAG -> %

CAT Push
AAA 0

AAA Pop

TAG END
 %
CAT Push
AAC 1

AA  Pop
```

### Truth machine

`ATGGAGAAGAGTATAAAT` (18 B)

Accepts one value as input. If this value is less than or equal to 0, it is
printed once before the program terminates. If the value is greater than 0, it
is printed infinitely.

```
  ATGGAGAAGAGTATAAAT
     ^            *
0 ==>DupPop<=0->*Loop>^
+1 Keep_bUniMulEND
```

* Execution starts at the initial ATG.
* The top element of the main stack is duplicated & printed, then
    * If the value is less than or equal to zero, jump to the ATA formed by the
      Asn and the start codon (remember, the code is circular), then run
      through a series of no-ops, including printing some non-printable
      characters.
    * If the value is greater than 0, loop back to the start.

If you don't like the ugly sequence of no-ops, adding `ATG` to the end to make
the loop target explicit results in a clean termination immediately after the
jump, for three more bytes.

### A polyglot

```fortran
program polyglot

    real :: big_number = 1764.0, arnold
    integer :: ounces_in_a_ton = 42

    if (.true.) then
        print *, ounces_in_a_ton, "is a cunning number"
    else
        arnold = sqrt(big_number)
    end if

    contains

    subroutine count_elements(array, num)

        real, dimension (:) :: array
        integer :: num

        num = size(array)

    end subroutine count_elements

end program polyglot
```

When interpreted as Fortran,
this rather stupid program prints
`42 is a cunning number`.
However, a secret code has been hidden within,
which only a deoxyribose interpreter can unveil.
Deciphering it is an exercise for the reader.

## Note

This is very much a work in progress, and some aspects of the design will
probably be changed in backwards-incompatible ways in future versions. I would
welcome suggestions.

## Licensing

The specification and documentation for this project are dual-licensed under a
[CC-BY](https://creativecommons.org/licenses/by/3.0) licence and the MIT
Licence, and the interpreter etc. are under the MIT Licence.
See the `LICENSE` file for more information.

This allows you to do whatever you want with the software,
free of charge,
including making modifications and distributing it commercially,
provided you retain the contents of the (very short) `LICENSE` file
in an appropriate place in all copies you distribute.
This file includes an attribution to the authors of this repository.

All potential contributors are expected to license their contributions under
the same licence,
and *may* add their names to the copyright notice in a pull request.

Although no patents are, at present, claimed on this software,
for the avoidance of doubt,
the "without limitation" line in the license text is considered by the authors
to be an explicit licence of any relevant patents.
