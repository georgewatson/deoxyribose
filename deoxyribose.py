#!/usr/bin/env python3

"""
DEOXYRIBOSE INTERPRETER
George Watson, 2018-2019
https://georgewatson.me
Released under an MIT licence
"""

# pylint: disable=invalid-name

import sys
import re


def stop(_, main_stack, aux_stack, variables):
    """
    Stop
    Terminate execution.
    """
    if VERBOSE:
        print("Stop", main_stack, aux_stack, variables)
    sys.exit(0)


# Charged amino acids: Single-stack operations


def his(pointer, main_stack, aux_stack, variables):
    """
    His
    Treat next codon as an integer literal in quaternary notation.
    Push the value to the main stack.
    """
    codon, pointer = read_next_codon(pointer)
    if VERBOSE:
        print("His", main_stack, aux_stack, codon)
    main_stack.append(codon_to_int(codon))
    return pointer, main_stack, aux_stack, variables


def lys(pointer, main_stack, aux_stack, variables):
    """
    Lys
    If the main stack is non-empty, pop the top element as a number.
    """
    if VERBOSE:
        print("Lys", main_stack, aux_stack)
    # If the stack is empty, do nothing
    if main_stack:
        print(main_stack.pop())
    return pointer, main_stack, aux_stack, variables


def arg(pointer, main_stack, aux_stack, variables):
    """
    Arg
    If the main stack is non-empty, pop the top element.
    If it is positive, round it towards zero and print it as a Unicode
    character.
    """
    if VERBOSE:
        print("Arg", main_stack, aux_stack)
    if main_stack:
        char = int(main_stack.pop())
        if char >= 0:
            try:
                sys.stdout.write(str(chr(char)))
            # If the value is too large, don't print it
            except (ValueError, OverflowError, UnicodeEncodeError):
                pass
    return pointer, main_stack, aux_stack, variables


def glu(pointer, main_stack, aux_stack, variables):
    """
    Glu
    If the main stack is non-empty, duplicate the top element.
    """
    if VERBOSE:
        print("Glu", main_stack, aux_stack)
    if main_stack:
        main_stack.append(main_stack[-1])
    return pointer, main_stack, aux_stack, variables


def asp(pointer, main_stack, aux_stack, variables):
    """
    Asp
    If the main stack is non-empty, drop the top element.
    """
    if VERBOSE:
        print("Asp", main_stack, aux_stack)
    if main_stack:
        main_stack = main_stack[:-1]
    return pointer, main_stack, aux_stack, variables


# Non-polar amino acids: Two-stack operations


def leu(pointer, main_stack, aux_stack, variables):
    """
    Leu
    Add the top elements of each stack.
    Place the result in the main stack.
    If either stack is empty, treat it as zero.
    """
    if VERBOSE:
        print("Leu", main_stack, aux_stack)
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
    return pointer, main_stack, aux_stack, variables


def ile(pointer, main_stack, aux_stack, variables):
    """
    Ile
    Subtract the top of the aux stack from the top of the main stack.
    Place the result in the main stack.
    If either stack is empty, treat it as zero.
    """
    if VERBOSE:
        print("Ile", main_stack, aux_stack)
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
    return pointer, main_stack, aux_stack, variables


def val(pointer, main_stack, aux_stack, variables):
    """
    Val
    Multiply the top elements of the two stacks.
    Place the result in the main stack.
    If either stack is empty, treat it as one.
    """
    if VERBOSE:
        print("Ile", main_stack, aux_stack)
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
    return pointer, main_stack, aux_stack, variables


def pro(pointer, main_stack, aux_stack, variables):
    """
    Pro
    Divide the top of the main stack by the top of the aux stack.
    Result is a float.
    Place the result in the main stack.
    If either stack is empty, treat it as one.
    """
    if VERBOSE:
        print("Pro", main_stack, aux_stack)
    # If either list is empty, treat it as one
    if main_stack:
        a = int(main_stack.pop())
    else:
        a = 1
    if aux_stack:
        b = int(aux_stack.pop())
    else:
        b = 1
    try:
        main_stack.append(a / b)
    # Fall back to integer division if the result doesn't fit in a float
    except OverflowError:
        main_stack.append(a // b)
    except ZeroDivisionError:
        main_stack.append(a)
    return pointer, main_stack, aux_stack, variables


def met(pointer, main_stack, aux_stack, variables):
    """
    Met
    Move the value of the variable named by the next codon to the top of the
    main stack.
    If the variable does not exist, do nothing.
    """
    variable_name, pointer = read_next_codon(pointer)
    if VERBOSE:
        print("Met", main_stack, aux_stack, variable_name, variables)
    if variable_name in variables:
        main_stack.append(variables[variable_name])
        del variables[variable_name]
    return pointer, main_stack, aux_stack, variables


def phe(pointer, main_stack, aux_stack, variables):
    """
    Phe
    Put aux stack on top of main stack, preserving its order
    """
    if VERBOSE:
        print("Phe", main_stack, aux_stack)
    main_stack += aux_stack
    aux_stack = []
    return pointer, main_stack, aux_stack, variables


def gly(pointer, main_stack, aux_stack, variables):
    """
    Gly
    If the main stack is non-empty, move the top element to the aux stack.
    """
    if VERBOSE:
        print("Gly", main_stack, aux_stack)
    if main_stack:
        aux_stack.append(main_stack.pop())
    return pointer, main_stack, aux_stack, variables


def trp(pointer, main_stack, aux_stack, variables):
    """
    Trp
    Move the top element of the main stack to a variable named by the next
    codon.
    The destination is overwritten.
    If the main stack is empty, the destination becomes empty.
    """
    variable_name, pointer = read_next_codon(pointer)
    if VERBOSE:
        print("Trp", main_stack, aux_stack, variable_name, variables)
    if main_stack:
        variables[variable_name] = main_stack.pop()
    else:
        del variables[variable_name]
    return pointer, main_stack, aux_stack, variables


def ala(pointer, main_stack, aux_stack, variables):
    """
    Ala
    Calculate main top modulo aux top.
    Place the result in the main stack.
    If the main stack is empty, treat it as zero.
    If the aux stack is empty, treat it as one.
    """
    if VERBOSE:
        print("Ala", main_stack, aux_stack)
    # If either list is empty, treat it as zero
    if main_stack:
        a = int(main_stack.pop())
    else:
        a = 0
    if aux_stack and aux_stack[-1] != 0:
        b = int(aux_stack.pop())
    else:
        b = 1
    try:
        main_stack.append(a % b)
    except ZeroDivisionError:
        pass
    return pointer, main_stack, aux_stack, variables


# Polar amino acids: Flow control


def ser(pointer, main_stack, aux_stack, variables):
    """
    Ser
    If the top element of the main stack is <= 0, jump to next occurrence of
    the following codon.
    """
    term, pointer = read_next_codon(pointer)
    if VERBOSE:
        print("Ser", main_stack, aux_stack, term)
    if main_stack and (main_stack[-1] <= 0):
        results = []
        result, success = look_ahead(pointer, term)
        if success:
            results.append(result - pointer)
        if results:
            pointer += min(results) + 1
    return pointer, main_stack, aux_stack, variables


def thr(pointer, main_stack, aux_stack, variables):
    """
    Thr
    If the top element of the main stack is <= 0, jump back to previous
    occurrence of the following codon.
    """
    term, _ = read_next_codon(pointer)
    if VERBOSE:
        print("Thr", main_stack, aux_stack, term)
    if main_stack and (main_stack[-1] <= 0):
        results = []
        result, success = look_back(pointer, term)

        if success:
            results.append(pointer - result)

        if results:
            pointer -= min(results) - 1
        else:
            pointer += 3
    return pointer, main_stack, aux_stack, variables


def tyr(pointer, main_stack, aux_stack, variables):
    """
    Tyr
    If main stack is empty, jump to next occurrence of the following codon.
    """
    term, pointer = read_next_codon(pointer)
    if VERBOSE:
        print("Tyr", main_stack, aux_stack, term)
    if not main_stack:
        results = []
        result, success = look_ahead(pointer, term)
        if success:
            results.append(result - pointer)
        if results:
            pointer += min(results) + 1
    return pointer, main_stack, aux_stack, variables


def gln(pointer, main_stack, aux_stack, variables):
    """
    Gln
    If the main stack is empty, jump back to previous occurrence of the
    following codon.
    """
    term, _ = read_next_codon(pointer)
    if VERBOSE:
        print("Gln", main_stack, aux_stack, term)
    if not main_stack:
        results = []
        result, success = look_back(pointer, term)

        if success:
            results.append(pointer - result)

        if results:
            pointer -= min(results) - 1
        else:
            pointer += 3
    return pointer, main_stack, aux_stack, variables


def asn(pointer, main_stack, aux_stack, variables):
    """
    Asn
    Unconditionally jump to previous occurrence of the next codon.
    """
    term, _ = read_next_codon(pointer)
    if VERBOSE:
        print("Asn", main_stack, aux_stack, term)
    results = []
    result, success = look_back(pointer, term)

    if success:
        results.append(pointer - result)

    if results:
        pointer -= min(results) - 1
    else:
        pointer += 3
    return pointer, main_stack, aux_stack, variables


def cys(pointer, main_stack, aux_stack, variables):
    """
    Cys
    Unconditionally jump to next occurrence of the next codon.
    """
    term, pointer = read_next_codon(pointer)
    if VERBOSE:
        print("Cys", main_stack, aux_stack, term)
    results = []
    result, success = look_ahead(pointer, term)
    if success:
        results.append(result - pointer)
    if results:
        pointer += min(results) + 1
    return pointer, main_stack, aux_stack, variables


# Helper functions


def codon_to_int(codon):
    """
    Convert a quaternary codon to an integer, and return the result.
    """
    codon = codon.lower()
    i = 0
    value = 0
    for i in range(3):
        char = codon[-i-1]
        if char == 'a':
            value += 0
        elif char == 'c':
            value += 1 * (4**i)
        elif char == 'g':
            value += 2 * (4**i)
        elif char == 't':
            value += 3 * (4**i)

    return value


def read_next_codon(pointer):
    """
    Read the next 3-digit codon
    """
    codon = ""
    for _ in range(3):
        codon += CHROMOSOME[pointer % len(CHROMOSOME)].lower()
        pointer += 1
    return codon, pointer


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
            return pointer, True
        pointer += 1
    return pointer, False


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
            return pointer, True
        pointer -= 1
    return pointer, False


# Define genetic code table
GENETIC_CODE = {
    'taa': stop,  # ochre
    'tag': stop,  # amber
    'tga': stop,  # opal

    # Charged amino acids: Single-stack operations

    'cat': his,
    'cac': his,

    'aaa': lys,
    'aag': lys,

    'cgt': arg,
    'cgc': arg,
    'cga': arg,
    'cgg': arg,
    'aga': arg,
    'agg': arg,

    'gaa': glu,
    'gag': glu,

    'gat': asp,
    'gac': asp,

    # Non-polar amino acids: Two-stack operations

    'tta': leu,
    'ttg': leu,
    'ctt': leu,
    'ctc': leu,
    'cta': leu,
    'ctg': leu,

    'att': ile,
    'atc': ile,
    'ata': ile,

    'gtt': val,
    'gtc': val,
    'gta': val,
    'gtg': val,

    'cct': pro,
    'ccc': pro,
    'cca': pro,
    'ccg': pro,

    'atg': met,

    'ttt': phe,
    'ttc': phe,

    'ggt': gly,
    'ggc': gly,
    'gga': gly,
    'ggg': gly,

    'tgg': trp,

    'gct': ala,
    'gcc': ala,
    'gca': ala,
    'gcg': ala,

    # Polar amino acids: Flow control

    'tct': ser,
    'tcc': ser,
    'tca': ser,
    'tcg': ser,
    'agt': ser,
    'agc': ser,

    'act': thr,
    'acc': thr,
    'aca': thr,
    'acg': thr,

    'tat': tyr,
    'tac': tyr,

    'caa': gln,
    'cag': gln,

    'aat': asn,
    'aac': asn,

    'tgt': cys,
    'tgc': cys
}


# Main


def main():
    """
    The main body of the interpreter
    """

    main_stack = []
    aux_stack = []
    variables = {}
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
            if VERBOSE:
                print(codon)

            # Do we know what this codon does?
            if codon in GENETIC_CODE:
                # If so, run the amino acid function
                pointer, main_stack, aux_stack, variables = \
                    GENETIC_CODE[codon](pointer, main_stack, aux_stack,
                                        variables)
        else:
            # If not, look for a start codon
            # If we can't find one, loop forever. This is deliberate.
            pointer, in_gene = look_ahead(pointer, 'atg')
            pointer += 1


VERBOSE = False

# Get code, keeping only A, C, G, and T characters
if len(sys.argv) > 1:
    CHROMOSOME = re.sub(r'[^acgt]', '', sys.argv[1].lower())
else:
    # If no program was specified as an argument, accept from standard input
    while True:
        USER_INPUT = ''.join(i for i in sys.stdin)
        CHROMOSOME = re.sub(r'[^acgt]', '', USER_INPUT.lower())

# Run interpreter
main()
