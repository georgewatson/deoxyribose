# Deoxyribose
The DNA-themed programming language all the kids are talking about

# Introducing Deoxyribose

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
the codon–amino acid correspondence, can allow some very fun and exciting things.

## Amino acids (operators)

The operators are defined by their correspondence to particular amino acids, as
follows.

**Special codons:**
* `ATG`: Start program execution. Everything before this codon is ignored, and
  it is expected that the next codon will define the "block size" (see below);
  this codon also codes for methionine
* `TAG`, `TAA`, and `TGA`: Stop; exit the program and return 0.

**Charged amino acids — Single-stack operations:**
* **His**: Push next block (expressed in quaternary notation, see below) to the
  top of the main stack
* **Lys**: Pop top of main stack to standard output as an integer
* **Arg**: Pop top of main stack to standard output as a Unicode character
* **Glu**: Duplicate top element of main stack

**Non-polar amino acids — Two-stack operations:**
* **Leu**: Add the top elements of the main and auxiliary stack, remove these
  elements, and place the result on top of the main stack
* **Ile**: Subtract the top element of the auxiliary stack from the top element
  of the main stack, remove these elements, and place the result on top of the
  main stack
* **Val**: Multiply the top elements of the main and auxiliary stack, remove these
  elements, and place the result on top of the main stack
* **Pro**: Floor-divide the top element of the main stack by the top element
  of the auxiliary stack, remove these elements, and place the result on top of the
  main stack
* **Ala**: Calculate the top element of the main stack modulo the top element
  of the auxiliary stack, remove these elements, and place the result on top of the
  main stack
* **Met**: Swap the top elements of the main and auxiliary stacks
* **Phe**: Put the auxiliary stack on top of the main stack, clearing the
  auxiliary stack
* **Asp**: Move the top element of the main stack to the top of the auxiliary
  stack (*Aspartic acid is actually a charged amino acid, and shouldn't really be
  in this section*)

**Polar amino acids — Flow control**
* **Ser**: If the top elements of the stacks are equal, jump to the next **Thr**
* **Tyr**: If the main stack is empty, jump to the next **Gln**
* **Asn**: Jump backwards to the previous **Cys**

Note that the length of these jumps need not always be a multiple of three. This
can cause frameshifts, which are half the fun.

## Integer literals

"But," I hear you cry, "How am I supposed to represent numbers using only the
letters A, C, G, and T?"

"Simple," I reply. "You just express natural numbers in base-4 such that A = 0,
C = 1, G = 2, and T = 3."

This is also where the block size comes in. The block size is a 3-digit base-4
number, expressed as described above, that specifies how many codons are in a
block. For example, a block size of `AAC` allows numbers up to `4**3 - 1` (63) to be
represented as integer literals, `AAG` up to `4**6 - 1` (4095), and `TTT` up
to `4**189 - 1` (~6E113). But choosing a larger block size means typing more
every time you want a number, so choose the balance carefully.

Once stored inside the stack, values are not subject to these same limits, and
are treated just like ordinary Python integers. Negative integers can therefore
be constructed by subtracting a natural number from zero.

Unicode characters can be stored as their character reference, and converted
back by arginine. There is no built-in string datatype, only chars ordered on
the stack.

## Examples

### Hello, world!
`ATGACGAAGAAACATAAAGACCACAACGCA...CATAACAGATGTAGATATAATCAATAG`
(117 B)

```
ATG Start
AAG Block size = 2

CAT His     Push next block
AAA 000     Start of block  0 +
GAC 201     End of block    33  = 33 (ASCII !)

CAC His     Push next block
AAC 001     Start of block  64 +
GCA 210     End of block    36  = 100 (ASCII d)

...

CAT His     Push next block
AAC 001     Start of block  64 +
AGA 020     End of block    8   = 72 (ASCII H)

TGT Cys     Destination of Asn
AGA Arg     Pop top block as char
TAT Tyr     If stack is empty, jump forward to Gln
AAT Asn     Else, jump back to Cys
CAA Gln     Destination of Tyr

TAG Stop
```

### Infinite Fibonacci sequence
`ATGAACCATAACGAAGATTGTGAATTAGATATGGAAAAAAAT`
(42 B)

```
ATG Start
AAC Block size = 1

CAT His     Push next block
AAC 001     Numeric literal 1
GAA Glu     Duplicate top element of main stack

GAT Asp     Move main top to aux

TGT Cys     Destination of Asn
GAA Glu     Duplicate top element of main stack
TTA Leu     Add top elements of stacks
GAT Asp     Move main top to aux
ATG Met     Swap top elements
GAA Glu     Duplicate top element of main stack
AAA Lys     Pop top element of main stack as int
AAT Asn     Jump back to Cys
```

### Cat
`ATGAACTGTGATTATAATCAATTTTGTAGATATAATCAATAG`
(42 B)

```
ATG Start
AAC Block size = 1

TGT Cys     Destination of Asn
GAT Asp     Move top element of main stack to aux stack
TAT Tyr     If the stack is empty, jump to next Gln
AAT Asn     Jump back to Cys
CAA Gln     Destination for Tyr

TTT Phe     Put aux stack on top of main stack

TGT
AGA Arg     Pop main stack as char
TAT
AAT
CAA

TAG Stop
```

### Integers from 1 to N
`ATGAAC GATCATAAC TGT GAAAAACATAACGATTTA AGTAATACT GAAAAA TAG`
(54 B)

```
ATG Start
AAC Block size = 1

GAT Asp     Move top element of main to aux

CAT His     Push next block
AAC 001     Numeric literal 1

TGT Cys     Destination of Asn

GAA Glu     Duplicate top element of main stack
AAA Lys     Pop top element of main stack as int
CAT His     Push next block
AAC 001     Numeric literal 1
GAT Asp     Move top element of main to aux
TTA Leu     Add top elements

AGT Ser     If top elements are equal, jump to next Thr
AAT Asn     Jump back to Cys
ACT Thr     Destination of Ser

GAA Glu     Duplicate top element of main stack
AAA Lys     Pop top element of main stack as int

TAG Stop
```

## Notes etc.

This is very much a work in progress, and there are some very poor aspects of the
design that will likely be changed in backwards-incompatible ways in future
versions. I would welcome suggestions.

The specification and documentation for this project are under a
[CC-BY](https://creativecommons.org/licenses/by/3.0) licence, and the
interpreter etc. are under an MIT licence. I'd love to see them developed and
improved upon, but it would be nice to see my name on there somewhere.
