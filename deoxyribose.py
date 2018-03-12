#!/usr/bin/env python3

"""
DEOXYRIBOSE INTERPRETER
George Watson, 2018
https://georgewatson.me
Released under an MIT licence
"""

# pylint: disable=unused-argument

import sys
import re


def leu(pointer, main_stack, aux_stack):
    """
    Leu
    Add the top elements of each stack.
    Place the result in the main stack.
    If either stack is empty, treat it as zero.
    """
    # If either list is empty, treat it as zero
    if main_stack:
        a = int(main_stack.pop())
    else:
        a = 0
    if aux_stack:
        b = int(aux_stack.pop())
    else:
        b = 0
    main_stack.append(a + b)
    return(pointer, main_stack, aux_stack)


def ile(pointer, main_stack, aux_stack):
    """
    Ile
    Subtract the top of the aux stack from the top of the main stack.
    Place the result in the main stack.
    If either stack is empty, treat it as zero.
    """
    # If either list is empty, treat it as zero
    if main_stack:
        a = int(main_stack.pop())
    else:
        a = 0
    if aux_stack:
        b = int(aux_stack.pop())
    else:
        b = 0
    main_stack.append(a - b)
    return(pointer, main_stack, aux_stack)


def met(pointer, main_stack, aux_stack):
    """
    Met
    Swap the top elements of the two stacks.
    Gracefully handles empty stacks.
    """
    # If either list is empty, just move one way
    # If both are empty, do nothing
    if main_stack:
        a = main_stack.pop()
    else:
        a = []
    if aux_stack:
        b = aux_stack.pop()
    else:
        b = []
    aux_stack.append(a)
    main_stack.append(b)
    return(pointer, main_stack, aux_stack)


def val(pointer, main_stack, aux_stack):
    """
    Val
    Multiply the top elements of the two stacks.
    Place the result in the main stack.
    If either stack is empty, treat it as one.
    """
    # If either list is empty, treat it as one
    if main_stack:
        a = int(main_stack.pop())
    else:
        a = 1
    if aux_stack:
        b = int(aux_stack.pop())
    else:
        b = 1
    main_stack.append(a * b)
    return(pointer, main_stack, aux_stack)


def ser(pointer, main_stack, aux_stack):
    """
    Ser
    If the top element of the main stack is <= 0, jump to next Thr.
    """
    if main_stack[-1] <= 0:
        results = []
        for term in ["act", "acc", "aca", "acg"]:
            result, success = look_ahead(pointer, term)
            if success:
                results.append(result - pointer)
        if results:
            pointer += min(results) + 1
    return(pointer, main_stack, aux_stack)


def pro(pointer, main_stack, aux_stack):
    """
    Pro
    Floor-divide the top of the main stack by the top of the aux stack.
    Place the result in the main stack.
    If either stack is empty, treat it as one.
    """
    # If either list is empty, treat it as one
    if main_stack:
        a = int(main_stack.pop())
    else:
        a = 1
    if aux_stack:
        b = int(aux_stack.pop())
    else:
        b = 1
    main_stack.append(a // b)
    return(pointer, main_stack, aux_stack)


def ala(pointer, main_stack, aux_stack):
    """
    Ala
    Calculate main top modulo aux top.
    Place the result in the main stack.
    If either stack is empty, treat it as zero.
    """
    # If either list is empty, treat it as zero
    if main_stack:
        a = int(main_stack.pop())
    else:
        a = 0
    if aux_stack:
        b = int(aux_stack.pop())
    else:
        b = 0
    main_stack.append(a % b)
    return(pointer, main_stack, aux_stack)


def tyr(pointer, main_stack, aux_stack):
    """
    Tyr
    If main stack is empty, jump to next Gln.
    """
    if not main_stack:
        results = []
        for term in ["caa", "cag"]:
            result, success = look_ahead(pointer, term)
            if success:
                results.append(result - pointer)
        if results:
            pointer += min(results) + 1
    return(pointer, main_stack, aux_stack)


def stop(pointer, main_stack, aux_stack):
    """
    Stop
    Terminate execution.
    """
    sys.exit(0)


def his(pointer, main_stack, aux_stack):
    """
    His
    Treat next block as an integer literal in quaternary notation.
    Push the value to the main stack.
    """
    block = ""
    for _ in range(BLOCK_SIZE):
        codon, pointer = read_next_codon(pointer)
        block += codon
    main_stack.append(block_to_int(block))
    return(pointer, main_stack, aux_stack)


def asn(pointer, main_stack, aux_stack):
    """
    Asn
    Jump to previous Cys.
    """
    results = []
    for term in ["tgt", "tgc"]:
        result, success = look_back(pointer, term)
        if success:
            results.append(pointer - result)
    if results:
        pointer -= min(results) - 1
    return(pointer, main_stack, aux_stack)


def lys(pointer, main_stack, aux_stack):
    """
    Lys
    If the main stack is non-empty, pop the top element as an integer.
    """
    # If the stack is empty, do nothing
    if main_stack:
        print(main_stack.pop())
    return(pointer, main_stack, aux_stack)


def arg(pointer, main_stack, aux_stack):
    """
    Arg
    If the main stack is non-empty, pop the top element as a Unicode character.
    """
    if main_stack:
        sys.stdout.write(str(chr(int(main_stack.pop()))))
    return(pointer, main_stack, aux_stack)


def asp(pointer, main_stack, aux_stack):
    """
    Asp
    If the main stack is non-empty, move the top element to the aux stack.
    """
    if main_stack:
        aux_stack.append(main_stack.pop())
    return(pointer, main_stack, aux_stack)


def glu(pointer, main_stack, aux_stack):
    """
    Glu
    If the main stack is non-empty, duplicate the top element.
    """
    if main_stack:
        main_stack.append(main_stack[-1])
    return(pointer, main_stack, aux_stack)


def phe(pointer, main_stack, aux_stack):
    """
    Phe
    Put aux stack on top of main stack, preserving its order
    """
    main_stack += aux_stack
    aux_stack = []
    return(pointer, main_stack, aux_stack)


def block_to_int(block):
    """
    Convert a quaternary block to an integer, and return the result.
    """
    block = block.lower()
    i = 0
    value = 0
    for i in range(len(block)):
        char = block[-i-1]
        if char == 'a':
            value += 0
        elif char == 'c':
            value += 1 * (4**i)
        elif char == 'g':
            value += 2 * (4**i)
        elif char == 't':
            value += 3 * (4**i)
        else:
            sys.stderr.write("Mutation: Block ", block,
                             " contains invalid character ", char)

    return value


def read_next_codon(pointer):
    """
    Read the next 3-digit codon
    """
    codon = ""
    for _ in range(3):
        codon += CHROMOSOME[pointer % len(CHROMOSOME)].lower()
        pointer += 1
    return(codon, pointer)


def look_ahead(pointer, search_term):
    """
    Search forwards for a given string of length 3, and return the position of
    the last character.
    Also return a boolean representing success.
    """
    # Only loop back round to where we came from, then give up
    for _ in range(len(CHROMOSOME)):
        if (CHROMOSOME[pointer % len(CHROMOSOME)] == search_term[2] and
                CHROMOSOME[(pointer-1) % len(CHROMOSOME)] == search_term[1] and
                CHROMOSOME[(pointer-2) % len(CHROMOSOME)] == search_term[0]):
            return(pointer, True)
        else:
            pointer += 1
    return(pointer, False)


def look_back(pointer, search_term):
    """
    Search backwards for a given string of length 3, and return the position of
    the last character.
    Also return a boolean representing success.
    """
    # Only loop back round to where we came from, then give up
    for _ in range(len(CHROMOSOME)):
        if (CHROMOSOME[pointer % len(CHROMOSOME)] == search_term[2] and
                CHROMOSOME[(pointer-1) % len(CHROMOSOME)] == search_term[1] and
                CHROMOSOME[(pointer-2) % len(CHROMOSOME)] == search_term[0]):
            return(pointer, True)
        else:
            pointer -= 1
    return(pointer, False)


GENETIC_CODE = {
    "tta": leu,
    "ttg": leu,
    "ctt": leu,
    "ctc": leu,
    "cta": leu,
    "ctg": leu,

    "att": ile,
    "atc": ile,
    "ata": ile,

    "atg": met,

    "gtt": val,
    "gtc": val,
    "gta": val,
    "gtg": val,

    "tct": ser,
    "tcc": ser,
    "tca": ser,
    "tcg": ser,
    "agt": ser,
    "agc": ser,

    "cct": pro,
    "ccc": pro,
    "cca": pro,
    "ccg": pro,

    "gct": ala,
    "gcc": ala,
    "gca": ala,
    "gcg": ala,

    "tat": tyr,
    "tac": tyr,

    "taa": stop,  # ochre

    "tag": stop,  # amber

    "cat": his,
    "cac": his,

    "aat": asn,
    "aac": asn,

    "aaa": lys,
    "aag": lys,

    "tga": stop,  # opal

    "cgt": arg,
    "cgc": arg,
    "cga": arg,
    "cgg": arg,
    "aga": arg,
    "agg": arg,

    "gat": asp,
    "gac": asp,

    "gaa": glu,
    "gag": glu,

    "ttt": phe,
    "ttc": phe
}


def main():
    """
    The main body of the interpreter
    """
    # pylint: disable=global-statement
    global BLOCK_SIZE

    codon = ""
    main_stack = []
    aux_stack = []
    in_gene = False

    # Push additional command line arguments to the stack
    for element in sys.argv[2:]:
        try:
            # Is the argument an integer?
            main_stack.append(int(element))
        except ValueError:
            # If not, treat it as a string & split it into characters, each of
            # which provides one integer.
            for char in element:
                main_stack.append(ord(char))

    # Start at the beginning
    pointer = 0

    # Loop indefinitely (or until a stop codon)
    while True:
        # Are we in a gene currently?
        if in_gene:
            # If so, read the next codon
            codon, pointer = read_next_codon(pointer)

            # Do we know what this codon does?
            if codon in GENETIC_CODE:
                # If so, run the amino acid function
                pointer, main_stack, aux_stack = GENETIC_CODE[codon](
                    pointer, main_stack, aux_stack)

            # We're done with this codon now
            codon = ""

        else:
            # If not, look for a start codon
            pointer, in_gene = look_ahead(pointer, "atg")

            # If we find one, the next codon should be the block size
            pointer += 1
            codon, pointer = read_next_codon(pointer)
            BLOCK_SIZE = block_to_int(codon)

            # Note that if we don't find a start codon, the program never
            # terminates. This is intentional.


BLOCK_SIZE = 1

# Get code, keeping only A, C, G, and T characters
if len(sys.argv) > 1:
    CHROMOSOME = re.sub('[^acgt]', '', sys.argv[1].lower())

    # Run interpreter
    main()
else:
    # If no program was specified as an argument, accept from standard input
    while True:
        USER_INPUT = input()
        CHROMOSOME = re.sub('[^acgt]', '', USER_INPUT.lower())

        # Run interpreter
        main()
