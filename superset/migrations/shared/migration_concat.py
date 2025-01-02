import os
import re
import ast


year_of_interest = '2015'

migration_dir = '../versions'

migration_files = os.listdir(migration_dir)

filtered_files = [
    file for file in sorted(migration_files)
    if re.match(f'^{year_of_interest}-', file)
]

upgrades = []
downgrades = []

class FunctionFinder(ast.NodeVisitor):
    def __init__(self, function_name):
        self.function_name = function_name
        self.node = None

    def visit_FunctionDef(self, node):
        if node.name == self.function_name:
            self.node = node
        self.generic_visit(node)

for filename in filtered_files:
    with open(os.path.join(migration_dir, filename), 'r') as file:

        migration_code = file.read()
        parsed_code = ast.parse(migration_code)  

        upgrade_finder = FunctionFinder('upgrade')
        upgrade_finder.visit(parsed_code)
        
        if upgrade_finder.node:
            upgrade_code = ast.get_source_segment(migration_code, upgrade_finder.node).replace("def upgrade():\n", "")
            print(upgrade_code)

        downgrade_finder = FunctionFinder('downgrade')
        downgrade_finder.visit(parsed_code)
        
        if downgrade_finder.node:
            downgrade_code = ast.get_source_segment(migration_code, downgrade_finder.node).replace("def downgrade():\n", "")
            print(downgrade_code)

        if upgrade_code:
            upgrades.append(f"# From {filename}\n{upgrade_code}")
        if downgrade_code:
            downgrades.append(f"# From {filename}\n{downgrade_code}")


final_upgrade = '\n\n\t'.join(upgrades)
final_downgrade = '\n\n\t'.join(reversed(downgrades)) 

consolidation_year = year_of_interest
new_migration_content = f"""
\"""Generated consolidated migration file for {consolidation_year}"\"\"

import sqlalchemy as sa  
from alembic import op 

def upgrade():
    {final_upgrade}

def downgrade():
    {final_downgrade}
"""

new_filename = f'{consolidation_year}_consolidated_migration.py'

with open(os.path.join(migration_dir, new_filename), 'w') as new_file:
    new_file.write(new_migration_content)