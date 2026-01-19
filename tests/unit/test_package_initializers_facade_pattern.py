from __future__ import annotations

import ast
from pathlib import Path


def test_package_initializers_follow_facade_pattern() -> None:
    """Asserts that all dare_framework initializers use the facade pattern.
    
    Rules:
    1. Must have a docstring.
    2. No class or function definitions.
    3. Assignments allowed only for metadata (e.g., __all__, __version__).
    4. Imports allowed for re-exporting.
    """
    repo_root = Path(__file__).resolve().parents[2]
    package_root = repo_root / "dare_framework"
    init_files = sorted(package_root.rglob("__init__.py"))
    assert init_files, "Expected to find dare_framework package initializers"

    violations: list[str] = []
    for path in init_files:
        source = path.read_text(encoding="utf-8")
        if not source.strip():
             # Empty files are okay if they are just placeholders, 
             # but the user wanted docstrings.
             violations.append(f"{path.relative_to(repo_root)}: Missing docstring")
             continue
             
        module = ast.parse(source, filename=str(path))
        body = module.body

        # Rule 1: Must have a docstring
        if not (
            body
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            violations.append(f"{path.relative_to(repo_root)}: Missing docstring at top of file")
            continue

        body = body[1:] # Skip docstring

        for node in body:
            # Rule 2: No class or function definitions
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                violations.append(f"{path.relative_to(repo_root)}: Prohibited definition ({type(node).__name__})")
                continue

            # Rule 3: Assignments allowed only for metadata
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = []
                if isinstance(node, ast.Assign):
                    targets = node.targets
                else:
                    targets = [node.target]
                
                valid_assignment = True
                for target in targets:
                    if isinstance(target, ast.Name):
                        if not (target.id.startswith("__") and target.id.endswith("__")):
                            valid_assignment = False
                    else:
                        valid_assignment = False
                
                if not valid_assignment:
                    violations.append(f"{path.relative_to(repo_root)}: Prohibited assignment (only __all__/__version__ etc allowed)")

            # Rule 4: Imports are allowed (for re-exporting)
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                continue
            
            # Allow metadata assignments and imports, but flag anything else
            if not isinstance(node, (ast.Assign, ast.AnnAssign, ast.Import, ast.ImportFrom)):
                violations.append(f"{path.relative_to(repo_root)}: Prohibited node type ({type(node).__name__})")

    assert not violations, "Package initializers violated facade pattern rules:\n" + "\n".join(violations)
