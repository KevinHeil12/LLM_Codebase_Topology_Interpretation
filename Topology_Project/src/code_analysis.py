import ast
import random

def modify_codebase(code_str: str, num_changes: int = 1):
    """
    Randomly rewrites up to num_changes call-sites in code_str, but
    it will **never** introduce a bare identifier called run().

    Returns
    -------
    modified_code : str   the new source
    changes_made  : int   how many calls were actually rewritten
    """
    tree = ast.parse(code_str)

    # ── 1. Collect module-level function names ───────────────────────────
    candidate_names = set()

    class FunctionCollector(ast.NodeVisitor):
        """
        Records   def foo(...):         (module level only)
        Ignores   class C:  def bar(...):
        """
        def __init__(self):
            self.in_class = 0

        def visit_ClassDef(self, node):
            self.in_class += 1
            self.generic_visit(node)
            self.in_class -= 1

        def visit_FunctionDef(self, node):
            if self.in_class == 0 and node.name not in {"main", "run"}:
                candidate_names.add(node.name)
            # still visit body, but we don’t collect nested defs
            self.generic_visit(node)

    FunctionCollector().visit(tree)
    pool = list(candidate_names)                     # random.choice needs list
    if len(pool) < 2:                                # nothing sensible to swap
        return code_str, 0

    # ── 2. Rewrite call-sites ────────────────────────────────────────────
    class CallRewriter(ast.NodeTransformer):
        def __init__(self, pool, limit):
            self.pool   = pool
            self.limit  = limit
            self.made   = 0

        def visit_Call(self, node):
            if self.made >= self.limit:
                return self.generic_visit(node)

            # rewrite only bare-name calls that already target a pool func
            if isinstance(node.func, ast.Name) and node.func.id in self.pool:
                old = node.func.id
                choices = [n for n in self.pool if n != old]
                if choices:
                    node.func.id = random.choice(choices)
                    self.made += 1
            return self.generic_visit(node)

    rewriter = CallRewriter(pool, num_changes)
    new_tree = rewriter.visit(tree)
    ast.fix_missing_locations(new_tree)

    return ast.unparse(new_tree), rewriter.made

def extract_graph(code_str):
    """
    Parse code_str to AST, collect:
      - nodes: all top-level FunctionDef and ClassDef names
      - edges: [(parent, child)] whenever child’s body calls parent
    Returns (nodes_list, adjacency_list_as_dicts).
    """
    tree = ast.parse(code_str)

    class GraphBuilder(ast.NodeVisitor):
        """
        Builds a call graph.
        • Nodes  = every top-level def or class name.
        • Edge   (parent, child) is added when child calls parent.
        • Special rule: a bare call to  run()  inside a class body counts as a
            call to *that class*, not to a literal node called "run".
        """
        def __init__(self):
            self.node_types    = {}          # name -> "function" | "class"
            self.edges         = []          # list[(parent, child)]
            self.instance_maps = {}          # container -> {var -> class}
            self.current       = None        # where we are right now
            self.class_stack   = []          # nested class names

        # ── class definitions ──────────────────────────────────────────────
        def visit_ClassDef(self, node):
            self.node_types[node.name] = "class"
            self.class_stack.append(node.name)

            prev, self.current = self.current, node.name
            self.instance_maps[self.current] = {}
            self.generic_visit(node)
            self.current = prev
            self.class_stack.pop()

        # ── functions / methods ────────────────────────────────────────────
        def visit_FunctionDef(self, node):
            # ── CASE 1: method inside a class ────────────────────────────────
            if self.class_stack:
                # Do *not* create a new node; keep using the class name
                # that is already at the top of the stack.
                self.generic_visit(node)          # still traverse the body
                return                            # early-exit

            # ── CASE 2: top-level function ──────────────────────────────────
            self.node_types[node.name] = "function"
            prev, self.current = self.current, node.name
            self.instance_maps[self.current] = {}
            self.generic_visit(node)
            self.current = prev

        # ── variable = ClassName() ─────────────────────────────────────────
        def visit_Assign(self, node):
            if (self.current and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Name)):
                cls = node.value.func.id
                if self.node_types.get(cls) == "class":
                    inst = node.targets[0].id
                    self.instance_maps[self.current][inst] = cls
            self.generic_visit(node)

        # ── function / method calls ────────────────────────────────────────
        def visit_Call(self, node):
            if not self.current:                 # skip top-level expressions
                return self.generic_visit(node)

            # ── 1) bare identifier call  foo(...)
            if isinstance(node.func, ast.Name):
                callee = node.func.id
                if callee == "run" and self.class_stack:      # ← inside a class
                    callee = self.class_stack[-1]             #   map to class
                # keep bare-function run() at top level as "run"
                if callee in self.node_types:
                    self.edges.append((callee, self.current))

            # ── 2) attribute call  inst.run(...)
            elif isinstance(node.func, ast.Attribute) and node.func.attr == "run":
                parent_cls = None

                # (a) try to resolve inst ➜ class via instance_maps
                if isinstance(node.func.value, ast.Name):
                    inst = node.func.value.id
                    parent_cls = self.instance_maps[self.current].get(inst)

                # (b) fallback: if we’re *inside* a class method and the call is
                #     self.run()  or SomeOtherObj.run() that couldn’t be resolved,
                #     use the *enclosing class* instead of literal "run"
                if not parent_cls and self.class_stack:
                    parent_cls = self.class_stack[-1]

                if parent_cls and parent_cls in self.node_types:
                    self.edges.append((parent_cls, self.current))

            self.generic_visit(node)

    builder = GraphBuilder()
    builder.visit(tree)

    nodes = list(builder.node_types.keys())
    adjacency = [
        {"from": parent, "to": child} for parent, child in builder.edges
    ]
    return nodes, adjacency


def modify_and_extract(code_str, num_changes=1):
    """
    Performs both the AST-based call mutation and then re‑extracts the
    updated node list and adjacency list.
    Returns:
      modified_source (str),
      changes_made (int),
      nodes (List[str]),
      adjacency (List[{"from": str, "to": str}])
    """
    modified_source, changes = modify_codebase(code_str, num_changes)
    nodes, adjacency = extract_graph(modified_source)
    return modified_source, changes, nodes, adjacency