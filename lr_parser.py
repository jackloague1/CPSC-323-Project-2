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
        # self.record_history()  # Record history after each operation

    def pop(self):
        if not self.is_empty():
            popped = self.items.pop()
            # self.record_history()  # Record history after each operation
            return popped

    def peek(self):
        return self.items[-1] if not self.is_empty() else None

    def is_empty(self):
        return len(self.items) == 0

    def record_history(self, token=None, action=None):
        # This method records the state of the stack, input, and action
        # token and action are optional arguments to record the current processing token and action taken
        current_state = {
            'step': len(self.history) + 1,  # steps are usually 1-based
            'stack': self.items.copy(),  # Copy the current stack state
            'input': token if token is not None else [],  # Make sure this is a list
            'action': action
        }
        self.history.append(current_state)
    def __str__(self):
        return str(self.items)

    def get_history(self):
        # Returns the recorded history
        return self.history


parsing_table = {
    0: {'ACTION': {'id': 'S5', '+': None, '*': None, '(': 'S4', ')': None, '$': None},
        'GOTO': {'E': 1, 'T': 2, 'F': 3}},
    1: {'ACTION': {'id': None, '+': 'S6', '*': None, '(': None, ')': None, '$': 'acc'},
        'GOTO': {}},
    2: {'ACTION': {'id': None, '+': 'R2', '*': 'S7', '(': None, ')': 'R2', '$': 'R2'},
        'GOTO': {'E': None, 'T': None, 'F': None}},  # Assuming no GOTO transitions for this state
    3: {'ACTION': {'id': None, '+': 'R4', '*': 'R4', '(': None, ')': 'R4', '$': 'R4'},
        'GOTO': {}},
    4: {'ACTION': {'id': 'S5', '+': None, '*': None, '(': 'S4', ')': None, '$': None},
        'GOTO': {'E': 8, 'T': 2, 'F': 3}},
    5: {'ACTION': {'id': None, '+': 'R6', '*': 'R6', '(': None, ')': 'R6', '$': 'R6'},
        'GOTO': {}},
    6: {'ACTION': {'id': 'S5', '+': None, '*': None, '(': 'S4', ')': None, '$': None},
        'GOTO': {'T': 9, 'F': 3}},
    7: {'ACTION': {'id': 'S5', '+': None, '*': None, '(': 'S4', ')': None, '$': None},
        'GOTO': {'F': 10}},
    8: {'ACTION': {'id': None, '+': 'S6', '*': None, '(': None, ')': 'S11', '$': None},
        'GOTO': {}},
    9: {'ACTION': {'id': None, '+': 'R1', '*': 'S7', '(': None, ')': 'R1', '$': 'R1'},
        'GOTO': {}},
    10: {'ACTION': {'id': None, '+': 'R3', '*': 'R3', '(': None, ')': 'R3', '$': 'R3'},
         'GOTO': {}},
    11: {'ACTION': {'id': None, '+': 'R5', '*': 'R5', '(': None, ')': 'R5', '$': 'R5'},
         'GOTO': {}},
}


# LR Parsing Table
parsing_tabl = {
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

def tokenize(expression):
    tokens = []
    token = ''
    for char in expression:
        if char in {'+', '*', '(', ')', '$'}:
            if token:  # add the token that was being built up if there is one
                tokens.append(token)
                token = ''  # reset the token
            tokens.append(char)  # add the single-character token
        else:
            token += char  # build up a token
    if token:  # add the last token if there is one
        tokens.append(token)
    return tokens
def parse_line(tokens, parsing_table, cfg, stack):
    idx = 0  # To keep track of the current token index

    while idx < len(tokens):
        state = stack.peek()
        token = tokens[idx]
        action_dict = parsing_table[state]['ACTION']
        action = action_dict.get(token)

        if action is None:
            # Record the syntax error and raise an exception
            stack.record_history(tokens[idx:], "Syntax error")
            break
            # raise ParseError(f"Syntax error at token '{token}' in state {state}")

        # Record the current state before taking an action
        stack.record_history(tokens[idx:], f"Action: {action}")

        # Handle shift actions
        if action.startswith('S'):
            stack.push(token)  # Shift the token
            stack.push(int(action[1:]))  # Shift to the state indicated by the action
            idx += 1  # Move to the next token

        # Handle reduce actions
        elif action.startswith('R'):
            production_index = int(action[1:])
            lhs, rhs = cfg[production_index]
            # Pop the stack for each symbol in the RHS of the production
            for _ in range(len(rhs) * 2):  # Pop both state and symbol for each RHS symbol
                stack.pop()
            # Look up the next state to go to from the GOTO part of the parsing table
            goto_dict = parsing_table[stack.peek()]['GOTO']
            goto_state = goto_dict.get(lhs)
            if goto_state is None:
                stack.record_history(tokens[idx:], f"No GOTO state for {lhs}")
                raise ParseError(f"No GOTO state for {lhs} in state {state}")
            stack.push(lhs)  # Push the LHS of the production
            stack.push(goto_state)  # Push the state from the GOTO table

        # Handle accept actions
        elif action == 'acc':
            stack.record_history(tokens[idx:], "Accept")
            return "Accepted", stack.get_history()

    # If we exit the loop normally, it means the string was rejected
    stack.record_history(tokens[idx:], "Reject")
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
        tokens = tokenize(line)  # Use the new tokenizer function
        stack = ParsingStack()  # Create a new stack for each line of input
        try:
            result, history = parse_line(tokens, parsing_table, cfg, stack)
            # Write the result and history to the output file
            with open(output_file, 'a') as f:
                for entry in history:
                    stack_repr = ' '.join(map(str, entry['stack']))  # Format stack as string
                    input_repr = ' '.join(entry['input'])  # Format remaining input as string
                    f.write(f"{entry['step'] : <20}{stack_repr : <20}{input_repr : <20}{entry['action'] : <20}\n")
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
