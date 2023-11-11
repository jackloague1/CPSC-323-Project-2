import sys
import re

# Read input from a file
def read_input_file(filename):
    with open(filename, 'r') as file:
        return file.read().strip().splitlines()

def write_output_file(filename, data):
    with open(filename, 'w') as file:
        file.write(data + '\n')

class ParsingStack:
    def __init__(self):
        self.items = [0]  # Initialize the stack with the start state
        self.history = []  # Initialize history for recording steps

    def push(self, item):
        self.items.append(item)
        self.record_history()  # Record history after each operation

    def pop(self):
        if not self.is_empty():
            popped = self.items.pop()
            self.record_history()  # Record history after each operation
            return popped

    def peek(self):
        return self.items[-1] if not self.is_empty() else None

    def is_empty(self):
        return len(self.items) == 0

    def record_history(self, token=None, action=None):
        # This method records the state of the stack, input, and action
        # token and action are optional arguments to record the current processing token and action taken
        current_state = {'step': len(self.history),
                         'stack': self.items[:],
                         'input': token,
                         'action': action}
        self.history.append(current_state)

    def __str__(self):
        return str(self.items)

    def get_history(self):
        # Returns the recorded history
        return self.history


# LR Parsing Table
parsing_table = {
    0: {'id': 'S5', '+': None, '*': None, '(': 'S4', ')': None, '$': None, 'E': 1, 'T': 2, 'F': 3},
    1: {'id': None, '+': 'S6', '*': None, '(': None, ')': None, '$': 'acc', 'E': None, 'T': None, 'F': None},
    2: {'id': None, '+': 'R2', '*': 'S7', '(': None, ')': 'R2', '$': 'R2', 'E': None, 'T': None, 'F': None},
    3: {'id': None, '+': 'R4', '*': 'R4', '(': None, ')': 'R4', '$': 'R4', 'E': None, 'T': None, 'F': None},
    4: {'id': 'S5', '+': None, '*': None, '(': 'S4', ')': None, '$': None, 'E': 8, 'T': 2, 'F': 3},
    5: {'id': None, '+': 'R6', '*': 'R6', '(': None, ')': 'R6', '$': 'R6', 'E': None, 'T': None, 'F': None},
    6: {'id': 'S5', '+': None, '*': None, '(': 'S4', ')': None, '$': None, 'E': None, 'T': 9, 'F': 3},
    7: {'id': 'S5', '+': None, '*': None, '(': 'S4', ')': None, '$': None, 'E': None, 'T': None, 'F': 10},
    8: {'id': None, '+': 'S6', '*': None, '(': None, ')': 'S11', '$': None, 'E': None, 'T': None, 'F': None},
    9: {'id': None, '+': 'R1', '*': 'S7', '(': None, ')': 'R1', '$': 'R1', 'E': None, 'T': None, 'F': None},
    10: {'id': None, '+': 'R3', '*': 'R3', '(': None, ')': 'R3', '$': 'R3', 'E': None, 'T': None, 'F': None},
    11: {'id': None, '+': 'R5', '*': 'R5', '(': None, ')': 'R5', '$': 'R5', 'E': None, 'T': None, 'F': None},
}

# CFG Production Rules
cfg = {
    1: ('E', ['E', '+', 'T']),  # Production 1
    2: ('E', ['T']),            # Production 2
    3: ('T', ['T', '*', 'F']),  # Production 3
    4: ('T', ['F']),            # Production 4
    5: ('F', ['(', 'E', ')']),  # Production 5
    6: ('F', ['id']),           # Production 6
}


# FIRST sets for each non-terminal
first_sets = {
    'E': ['(', 'id'],
    'T': ['(', 'id'],
    'F': ['(', 'id'],
}

# FOLLOW sets for each non-terminal
follow_sets = {
    'E': ['+', ')', '$'],
    'T': ['+', '*', ')', '$'],
    'F': ['+', '*', ')', '$'],
}



class ParseError(Exception):
    """Exception raised for errors in the parsing process."""
    pass

def parse_line(tokens, parsing_table, cfg, stack):
    idx = 0  # To keep track of the current token index

    while idx < len(tokens):
        state = stack.peek()
        token = tokens[idx]
        action = parsing_table.get(state, {}).get(token)

        # Handle syntax errors
        if action is None:
            stack.record_history(tokens[idx:], "Syntax error")
            raise ParseError(f"Syntax error at token '{token}' in state {state}")

        # Handle shift actions
        if action.startswith('S'):
            stack.push(token)  # Push token
            stack.push(int(action[1:]))  # Push state
            idx += 1  # Move to the next token
            stack.record_history(tokens[idx:], f"Shift {token}")

        # Handle reduce actions
        elif action.startswith('R'):
            production_index = int(action[1:])
            lhs, rhs = cfg[production_index]
            for _ in range(len(rhs)):  # Pop symbols and states
                stack.pop()  # Pop state
                stack.pop()  # Pop symbol
            # Look up the next state to go to from the GOTO part of the parsing table
            goto_state = parsing_table[stack.peek()]['GOTO'][lhs]
            stack.push(lhs)  # Push LHS of production
            stack.push(goto_state)  # Push new state
            stack.record_history(tokens[idx:], f"Reduce by {lhs} -> {' '.join(rhs)}")

        # Handle accept actions
        elif action == 'acc':
            stack.record_history(tokens[idx:], "Accept")
            return "Accepted", stack.get_history()

    # If the function hasn't returned by now, there's been an error
    return "Rejected", stack.get_history()


def parse_input(input_lines, parsing_table, cfg):
    parsed_results = []
    for line in input_lines:
        try:
            result = parse_line(line, parsing_table, cfg)
            parsed_results.append(result)
        except ParseError as e:
            parsed_results.append(str(e))
    return parsed_results

def main(input_file, output_file):
    input_lines = read_input_file(input_file)
    for line in input_lines:
        tokens = line.split()  # Or use a custom tokenizer if needed
        stack = ParsingStack()  # Create a new stack for each line of input
        try:
            result, history = parse_line(tokens, parsing_table, cfg, stack)
            # Write the result and history to the output file
            with open(output_file, 'a') as f:
                for entry in history:
                    f.write(f"{entry['step']}\t{entry['stack']}\t{entry['input']}\t{entry['action']}\n")
                f.write(f"{result}\n\n")
        except ParseError as e:
            with open(output_file, 'a') as f:
                f.write(str(e) + '\n')

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python lr_parser.py <inputfile> <outputfile>")
    else:
        input_file_path = sys.argv[1]
        output_file_path = sys.argv[2]
        main(input_file_path, output_file_path)
