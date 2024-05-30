import ast
import sys


class ShellCommandChecker(ast.NodeVisitor):
    def __init__(self):
        self.errors = []
        self.imports = {}
        self.sanitized_vars = set()

    def visit_Import(self, node):
        for alias in node.names:
            self.imports[alias.asname if alias.asname else alias.name] = alias.name

    def visit_ImportFrom(self, node):
        module = node.module
        for alias in node.names:
            self.imports[alias.asname if alias.asname else alias.name] = f"{module}.{alias.name}"

    def visit_Assign(self, node):
        # Check if the right-hand side of the assignment is a sanitized value
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute):
            if node.value.func.attr == 'quote' and self.is_shlex_quote(node.value.func.value):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.sanitized_vars.add(target.id)
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
            if node.value.func.id == 'quote' and 'shlex.quote' in self.imports.values():
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.sanitized_vars.add(target.id)
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            if node.func.attr == 'command':
                self.check_command_args(node)
        self.generic_visit(node)

    def check_command_args(self, node):
        for arg in node.args:
            if isinstance(arg, ast.JoinedStr):
                for value in arg.values:
                    if isinstance(value, ast.FormattedValue):
                        if not self.is_sanitized(value.value):
                            self.errors.append((node.lineno, node.col_offset, 'Shell command arguments should be sanitized using shlex.quote', value))

    def is_shlex_quote(self, node):
        # Check if the node represents the shlex.quote function
        if isinstance(node, ast.Name) and node.id in self.imports:
            return self.imports[node.id] == 'shlex.quote'
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            if node.value.id in self.imports and self.imports[node.value.id] == 'shlex':
                return node.attr == 'quote'
        return False

    def is_sanitized(self, node):
        # Check if the node is a call to shlex.quote
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == 'quote' and any(self.imports.get(name) == 'shlex.quote' for name in self.imports):
                return True
        # Check if the node is a variable that has been sanitized
        if isinstance(node, ast.Name):
            if node.id in self.sanitized_vars:
                return True
        return False

    def get_source_segment(self, source, node):
        lines = source.splitlines()
        line = lines[node.lineno - 1]
        start = node.col_offset
        end = start + len(ast.dump(node))
        return line, start, end


def check_file(filename):
    with open(filename, "r", encoding="utf-8") as file:
        source = file.read()
        tree = ast.parse(source, filename=filename)
        checker = ShellCommandChecker()
        checker.visit(tree)
        return checker.errors, source


def main():
    files_with_errors = []
    for filename in sys.argv[1:]:
        errors, source = check_file(filename)
        if errors:
            files_with_errors.append((filename, errors, source))

    if files_with_errors:
        for filename, errors, source in files_with_errors:
            for lineno, col_offset, msg, node in errors:
                line, start, end = ShellCommandChecker().get_source_segment(source, node)
                print(f"{filename}:{lineno}:{col_offset}: {msg}")
                print(line)
                print(' ' * start + '^' * (end - start))
        sys.exit(1)


if __name__ == "__main__":
    main()
