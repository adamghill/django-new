from pathlib import Path

import libcst as cst


def get_class_name(path: Path, base_class_name: str) -> str | None:
    src = path.read_text()
    module = cst.parse_module(src)

    def dotted_name(expr: cst.BaseExpression) -> str | None:
        if isinstance(expr, cst.Name):
            return expr.value

        parts: list[str] = []
        cur: cst.BaseExpression | None = expr

        while isinstance(cur, cst.Attribute):
            parts.append(cur.attr.value)
            cur = cur.value

        if isinstance(cur, cst.Name):
            parts.append(cur.value)

        if not parts:
            return None

        return ".".join(reversed(parts))

    for stmt in module.body:
        if isinstance(stmt, cst.ClassDef):
            for arg in stmt.bases:
                base = dotted_name(arg.value)

                if base and (
                    base == base_class_name or base.endswith(f".{base_class_name}")
                ):
                    return stmt.name.value

    return None
