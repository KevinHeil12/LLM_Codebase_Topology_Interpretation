import ast
import random
from gen import DATA_TYPES, generate_code_from_nodes

def modify_codebase(original_code, node_list, adjacency_list, num_changes, use_comments=False):
    """
    Modify the output type of random nodes, and regenerate the code accordingly.
    
    Returns:
        new_code (str): Updated Python code with new output types
        num_changes (int): Number of modifications made
        new_node_list (list): Updated list of nodes with modified output types
        adjacency_list (list): Unchanged
    """
    new_node_list = node_list[:]
    num_nodes = len(new_node_list)
    change_indices = random.sample(range(num_nodes), min(num_changes, num_nodes))

    for i in change_indices:
        name, obj_type, input_type, current_output = new_node_list[i]
        new_output = random.choice([t for t in DATA_TYPES if t != current_output])
        new_node_list[i] = (name, obj_type, input_type, new_output)

    new_code = generate_code_from_nodes(new_node_list, adjacency_list, use_comments=use_comments)
    return new_code, len(change_indices), new_node_list, adjacency_list

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
