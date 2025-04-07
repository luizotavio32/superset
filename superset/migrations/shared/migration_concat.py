import os
import re
import ast
from typing import Tuple


year_of_interest = '2016'

migration_dir = '../versions'

migration_files = os.listdir(migration_dir)

filtered_files = [
    file for file in sorted(migration_files)
    if re.match(f'^{year_of_interest}-', file)
]

upgrades = []
downgrades = []
classes_string = ''

class ImportFinder(ast.NodeVisitor):
    def __init__(self):
       
        self.imports = []
        self.from_imports = []

    def visit_Import(self, node):
        
        for alias in node.names:
            if (alias.name, alias.asname) not in self.imports:
                self.imports.append((alias.name, alias.asname))
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        module = node.module if node.module is not None else ""
        for alias in node.names:
            if (module, alias.name, alias.asname) not in self.from_imports:
                self.from_imports.append((module, alias.name, alias.asname))
        self.generic_visit(node)

class FunctionFinder(ast.NodeVisitor):
    def __init__(self, function_name):
        self.function_name = function_name
        self.node = None

    def visit_FunctionDef(self, node):
        if node.name == self.function_name:
            self.node = node
        self.generic_visit(node)

class ClassVisitor(ast.NodeVisitor):
    def __init__(self, source_code):
        self.source_code = source_code
        self.classes = []

    def get_source_segment(self, node):
        return ast.get_source_segment(self.source_code, node)
    
    def visit_ClassDef(self, node):
        class_source = self.get_source_segment(node)
        self.classes.append((node.name, class_source))
        self.generic_visit(node)

def generate_imports_string(imports: list, from_imports: list) -> str:

    import_string = ""

    for module, alias in imports:
        if alias:
            import_string += f"import {module} as {alias}\n"
        else:
            import_string += f"import {module}\n"

    for module, symbol, alias in from_imports:
        if alias:
            import_string += f"from {module} import {symbol} as {alias}\n"
        else:
            import_string += f"from {module} import {symbol}\n"

    return import_string

def generate_classes_string(classes):
    """
    Combine class definitions into a single string.

    Parameters:
    - classes: A list of tuples, each containing the class name and its source code.

    Returns:
    - A string containing all class definitions.
    """
    class_definitions = []
    for _, class_source in classes:
        class_definitions.append(class_source)
    return "\n\n".join(class_definitions)

import_finder = ImportFinder()

for filename in filtered_files:
    with open(os.path.join(migration_dir, filename), 'r') as file:


        migration_code = file.read()
        parsed_code = ast.parse(migration_code)

        import_finder.visit(parsed_code)  

        class_finder = ClassVisitor(migration_code)
        class_finder.visit(parsed_code)

        upgrade_finder = FunctionFinder('upgrade')
        upgrade_finder.visit(parsed_code)
        
        if upgrade_finder.node:
            upgrade_code = ast.get_source_segment(migration_code, upgrade_finder.node).replace("def upgrade():\n", "")
            
        downgrade_finder = FunctionFinder('downgrade')
        downgrade_finder.visit(parsed_code)
        
        if downgrade_finder.node:
            downgrade_code = ast.get_source_segment(migration_code, downgrade_finder.node).replace("def downgrade():\n", "")

        if len(class_finder.classes) > 0:
            classes_string += '\n\n' + generate_classes_string(classes=class_finder.classes)

        if upgrade_code:
            upgrades.append(f"# From {filename}\n{upgrade_code}")
        if downgrade_code:
            downgrades.append(f"# From {filename}\n{downgrade_code}")

import_string = generate_imports_string(imports=import_finder.imports, from_imports=import_finder.from_imports)
final_upgrade = '\n\n\t'.join(upgrades)
final_downgrade = '\n\n\t'.join(reversed(downgrades)) 

consolidation_year = year_of_interest
new_migration_content = f"""
\"""Consolidated migration file for {consolidation_year}"\"\"

{import_string}
{classes_string}

def upgrade():
    {final_upgrade}

def downgrade():
    {final_downgrade}
"""

new_filename = f'{consolidation_year}_consolidated_migration.py'

with open(os.path.join(migration_dir, new_filename), 'w') as new_file:
    new_file.write(new_migration_content)