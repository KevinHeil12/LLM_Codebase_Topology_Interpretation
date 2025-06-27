#!/usr/bin/env python3
"""
A complete Python script that generates a toy codebase with user-defined topology
(chain, branch, or random DAG) and randomly assigned data types, including booleans.
"""

import random
import string
import math
import cmath
from collections import deque

# List of supported data types that can be used for transformations
# These types will be randomly assigned to function inputs and outputs
DATA_TYPES = [
    "int", "float", "list", "dict", "tuple", 
    "set", "str", "complex", "bool"
]

# Dictionary mapping pairs of types (input_type, output_type) to possible transformation code snippets
# Each entry provides one or more code snippets that convert a variable named 'parameter' 
# of input_type to a variable named 'result' of output_type
TRANSFORMATIONS_MAP = {
    ("bool", "int"): [
        "result = 1 if parameter else 0",
        "result = int(parameter)"
    ],
    ("bool", "float"): [
        "result = 1.0 if parameter else 0.0"
    ],
    ("bool", "str"): [
        "result = 'True' if parameter else 'False'"
    ],
    ("bool", "bool"): [
        "result = not parameter"
    ],

    ("int", "int"): [
        "result = parameter + random.randint(1, 10)",
        "result = parameter * 2",
        "result = abs(parameter)"
    ],
    ("int", "float"): [
        "result = float(parameter) / (random.randint(1, 5))",
        "result = math.sqrt(abs(parameter))"
    ],
    ("int", "str"): [
        "result = str(parameter) + '_converted'",
    ],
    ("int", "complex"): [
        "result = complex(parameter, parameter + 1)",
    ],

    ("float", "float"): [
        "result = math.sin(parameter)",
        "result = parameter ** 1.5",
    ],
    ("float", "int"): [
        "result = int(round(parameter))",
    ],
    ("float", "complex"): [
        "result = complex(parameter, parameter / 2.0)",
    ],

    ("list", "int"): [
        "result = len(parameter)",
        ("result = sum(parameter) if all(isinstance(x, (int, float)) "
         "for x in parameter) else len(parameter)")
    ],
    ("list", "float"): [
        ("result = sum(parameter) / len(parameter) if len(parameter) > 0 "
         "else 0.0"),
    ],
    ("list", "list"): [
        "result = parameter[::-1]  # reversed list",
    ],
    ("list", "str"): [
        "result = ','.join(str(x) for x in parameter)",
    ],
    ("list", "set"): [
        "result = set(parameter)",
    ],

    ("dict", "list"): [
        "result = list(parameter.keys())",
    ],
    ("dict", "int"): [
        "result = len(parameter)",
    ],
    ("dict", "str"): [
        "result = f'DictKeys: {list(parameter.keys())}'",
    ],

    ("tuple", "list"): [
        "result = list(parameter)",
    ],
    ("tuple", "int"): [
        "result = len(parameter)",
    ],

    ("set", "int"): [
        "result = len(parameter)",
    ],
    ("set", "str"): [
        ("result = ','.join(str(x) for x in sorted(parameter))"),
    ],

    ("str", "list"): [
        "result = list(parameter)",
    ],
    ("str", "int"): [
        "result = len(parameter)",
    ],
    ("str", "set"): [
        "result = set(parameter)",
    ],
    ("str", "float"): [
        "result = float(len(parameter))",
    ],
    ("str", "str"): [
        "result = parameter.upper()",
    ],

    ("complex", "float"): [
        "result = abs(parameter)",
    ],
    ("complex", "int"): [
        "result = int(abs(parameter))",
    ],
}


def get_random_transformation_code(input_type, output_type):
    """
    Return a code snippet that transforms a variable named 'parameter' from 'input_type' 
    to a variable named 'result' of 'output_type'. If no direct mapping is found in
    TRANSFORMATIONS_MAP, generate a fallback snippet.
    
    Args:
        input_type (str): The source data type (must be one of DATA_TYPES)
        output_type (str): The target data type (must be one of DATA_TYPES)
        
    Returns:
        str: A Python code snippet that transforms 'parameter' to 'result' with appropriate types
    """
    key = (input_type, output_type)
    if key in TRANSFORMATIONS_MAP:
        return random.choice(TRANSFORMATIONS_MAP[key])

    # Fallback logic if no direct match is in TRANSFORMATIONS_MAP:
    if input_type == "bool":
        if output_type == "dict":
            return "result = {'was_true': parameter}"
        else:
            return f"result = {output_type}([parameter])"

    if input_type in ("int", "float", "complex"):
        return f"result = {output_type}(parameter)"

    if input_type == "str":
        if output_type == "dict":
            return "result = {parameter: len(parameter)}"
        return f"result = {output_type}([parameter])"

    if input_type == "list":
        if output_type == "dict":
            return "result = {{i: v for i, v in enumerate(parameter)}}"
        return f"result = {output_type}(parameter)"

    if input_type == "dict":
        if output_type in ("list", "tuple", "set"):
            return f"result = {output_type}(parameter.keys())"
        return "result = str(parameter)  # fallback"

    if input_type == "tuple":
        return f"result = {output_type}(parameter)"

    if input_type == "set":
        if output_type == "dict":
            return "result = {x: True for x in parameter}"
        return f"result = {output_type}(parameter)"

    return "result = None  # fallback default"


def generate_random_literal(data_type):
    """
    Return a small literal in Python syntax consistent with 'data_type'.
    
    Args:
        data_type (str): The data type to generate (must be one of DATA_TYPES)
        
    Returns:
        str: A string representation of a literal value matching the requested type
    """
    if data_type == "int":
        return str(random.randint(1, 20))
    elif data_type == "float":
        return f"{random.uniform(0, 10):.2f}"
    elif data_type == "list":
        return "[1, 2, 3]"
    elif data_type == "dict":
        return "{'key': 42}"
    elif data_type == "tuple":
        return "(10, 20)"
    elif data_type == "set":
        return "{1, 2, 3}"
    elif data_type == "str":
        random_string_content = ''.join(random.choice(string.ascii_lowercase) for _ in range(5))
        return f"'{random_string_content}'"
    elif data_type == "complex":
        return "complex(3, 4)"
    elif data_type == "bool":
        return "True" if random.random() < 0.5 else "False"
    else:
        return "None"


def generate_random_string(length=5):
    """
    Generate a random string of lowercase letters, used for variable names.
    
    Args:
        length (int): Length of the random string to generate
        
    Returns:
        str: A random string of lowercase letters
    """
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))


def generate_random_filler_lines(count_lines):
    """
    Generate 'count_lines' statements that do not affect the final return value,
    for filler/realism.
    
    Args:
        count_lines (int): Number of lines of filler code to generate
        
    Returns:
        list: List of strings, each containing a random variable assignment
    """
    lines = []
    for _ in range(count_lines):
        variable_name = generate_random_string()
        random_value = random.randint(1, 100)
        lines.append(f"{variable_name} = {random_value}")
    return lines


def generate_branching_code_snippet(number_of_branches):
    """
    Generate 'number_of_branches' simple if-else blocks.
    
    Args:
        number_of_branches (int): Number of if-else blocks to generate
        
    Returns:
        list: List of strings representing if-else blocks with random conditions and assignments
    """
    lines = []
    for _ in range(number_of_branches):
        variable_name = generate_random_string()
        lines.append(f"if {random.randint(0, 10)} > 5:")
        lines.append(f"    {variable_name} = '{generate_random_string()}'")
        lines.append("else:")
        lines.append(f"    {variable_name} = '{generate_random_string()}'")
    return lines


def generate_loop_code_snippet(number_of_loops):
    """
    Generate 'number_of_loops' simple for-loop blocks.
    
    Args:
        number_of_loops (int): Number of loop structures to include
        
    Returns:
        list: List of strings representing for loops with empty bodies
    """
    lines = []
    for _ in range(number_of_loops):
        loop_variable = generate_random_string()
        lines.append(f"for {loop_variable} in range({random.randint(1, 5)}):")
        lines.append("    pass  # loop placeholder")
    return lines


def generate_method_body(
    input_type,
    output_type,
    filler_line_count,
    branching_count,
    loop_count,
    dependency_indices,
    node_list
):
    """
    Build a function/method body that:
      1. Expects 'parameter' of type 'input_type'.
      2. Includes random filler lines, branching, and loops.
      3. Calls dependencies (either functions or class run() methods) as needed.
      4. Finally transforms 'parameter' into 'result' of 'output_type' and returns it.
      
    Args:
        input_type (str): Input data type that the method accepts
        output_type (str): Output data type that the method returns
        filler_line_count (int): Number of random filler lines to include
        branching_count (int): Number of branching (if-else) statements to include
        loop_count (int): Number of loop structures to include
        dependency_indices (list): List of indices of other objects this method depends on
        node_list (list): List of all objects with their properties
        
    Returns:
        list: List of strings representing lines of code for the method body
    """
    lines = []

    # Add filler
    lines.extend(generate_random_filler_lines(filler_line_count))

    # Add branching
    lines.extend(generate_branching_code_snippet(branching_count))

    # Add loops
    lines.extend(generate_loop_code_snippet(loop_count))

    # Call each dependency
    for dependency_index in dependency_indices:
        dependency_name, dependency_type, dependency_input_type, dependency_output_type = node_list[dependency_index]
        if dependency_type == "function":
            # We can try passing 'parameter' if it matches the dependency's input type
            if dependency_input_type == input_type:
                lines.append(f"{dependency_name}(parameter)")
            else:
                random_literal = generate_random_literal(dependency_input_type)
                lines.append(f"{dependency_name}({random_literal})")
        else:
            # It's a class
            instance_variable = generate_random_string()
            lines.append(f"{instance_variable} = {dependency_name}()  # instantiate dependency object")
            if dependency_input_type == input_type:
                lines.append(f"{instance_variable}.run(parameter)")
            else:
                random_literal = generate_random_literal(dependency_input_type)
                lines.append(f"{instance_variable}.run({random_literal})")

    # Finally, transform the input 'parameter' into 'result'
    transformation_code = get_random_transformation_code(input_type, output_type)
    lines.append(transformation_code)
    lines.append("return result")

    return lines


def build_adjacency_list(number_of_objects, topology_mode, connectivity):
    """
    Build an adjacency list (parents-only form) ignoring data types:
      - 'chain': 0->1->2->...->(n-1)
      - 'branch': if n>=4, 0->1,0->2,1->3,2->3, rest disconnected
      - 'random': create a random DAG by shuffling the nodes and 
                  for each pair (u, v) with position[u]<position[v], 
                  add edge u->v with probability 'connectivity'.

    Returns adjacency_list[i] = list of indices of parents of i.
    
    Args:
        number_of_objects (int): Number of objects in the dependency graph
        topology_mode (str): Type of dependency structure to create:
            - "chain": Linear chain of dependencies 
            - "branch": Simple branching structure
            - "random": Random dependencies with probability based on connectivity
        connectivity (float): For random topology, probability of creating an edge between objects
        
    Returns:
        list: Adjacency list where adjacency_list[i] contains indices of parents of object i
    """
    adjacency_list = [[] for _ in range(number_of_objects)]

    if topology_mode == "chain":
        # Object i depends on (i-1) for i in [1..n-1]
        for index in range(1, number_of_objects):
            adjacency_list[index].append(index - 1)

    elif topology_mode == "branch":
        # if number_of_objects < 4:
        #     # Fallback to chain if not enough objects
        #     for index in range(1, number_of_objects):
        #         adjacency_list[index].append(index - 1)
        # else:
        #     # 0->1, 0->2, 1->3, 2->3
        #     adjacency_list[1].append(0)
        #     adjacency_list[2].append(0)
        #     adjacency_list[3].append(1)
        #     adjacency_list[3].append(2)
        if number_of_objects < 4:
            # Fallback to chain if not enough objects
            for index in range(1, number_of_objects):
                adjacency_list[index].append(index - 1)
        else:
            # 0->1, 0->2, 1->final_node, 2->final_node
            adjacency_list[1].append(0)
            adjacency_list[2].append(0)

            # Dynamically connect nodes to the final node
            final_node = number_of_objects - 1
            if 1 not in adjacency_list[final_node]:
                adjacency_list[final_node].append(1)
            if 2 not in adjacency_list[final_node]:
                adjacency_list[final_node].append(2)

            # Connect all remaining nodes to at least one parent
            for index in range(3, number_of_objects - 1):
                parent = random.randint(0, index - 1)  # Randomly choose a parent from earlier nodes
                adjacency_list[index].append(parent)

            # Ensure all nodes connect to the final node
            for index in range(number_of_objects - 1):
                if index not in adjacency_list[final_node]:
                    adjacency_list[final_node].append(index)

    else:
        # "random": guaranteed DAG by generating a random topological order first.
        all_nodes = list(range(number_of_objects))
        random.shuffle(all_nodes)
        position = {}
        for idx, node_id in enumerate(all_nodes):
            position[node_id] = idx

        # For each ordered pair (u, v), if position[u] < position[v], 
        # add edge u->v with probability = connectivity
        for u in range(number_of_objects):
            for v in range(number_of_objects):
                if u == v:
                    continue
                if position[u] < position[v]:
                    if random.random() < connectivity:
                        adjacency_list[v].append(u)

    return adjacency_list


def remove_cycles_and_get_topological_order(adjacency_list):
    """
    Perform a Kahn's algorithm for topological sorting. If any nodes remain 
    that never reach in_degree=0 (due to cycles), forcibly remove their edges.
    Returns a list of nodes in a topological order.
    
    Args:
        adjacency_list (list): Adjacency list where adjacency_list[i] lists parents of i
        
    Returns:
        list: Topological ordering of nodes after removing cycles
             (A valid execution order for the dependency graph)
    """
    number_of_objects = len(adjacency_list)
    children_list = [[] for _ in range(number_of_objects)]
    in_degree = [0] * number_of_objects

    # Build children list from the adjacency (parents) list
    for child_index in range(number_of_objects):
        for parent_index in adjacency_list[child_index]:
            children_list[parent_index].append(child_index)
        in_degree[child_index] = len(adjacency_list[child_index])

    queue = deque()
    for index in range(number_of_objects):
        if in_degree[index] == 0:
            queue.append(index)

    topological_order = []
    while queue:
        node_index = queue.popleft()
        topological_order.append(node_index)
        for child_of_node in children_list[node_index]:
            in_degree[child_of_node] -= 1
            if in_degree[child_of_node] == 0:
                queue.append(child_of_node)

    # If some remain out of the topological_order, forcibly remove edges
    remaining = set(range(number_of_objects)) - set(topological_order)
    while remaining:
        stuck_node = remaining.pop()
        adjacency_list[stuck_node].clear()
        topological_order.append(stuck_node)

    return topological_order


def unify_types_based_on_adjacency(node_list, adjacency_list):
    """
    For each node i, ensure that all parents' output_type == i's input_type.
    If multiple parents have conflicting output_types, pick one parent's output_type at random 
    and remove edges from conflicting parents.
    Then choose a random output_type for node i.

    node_list[i] = (object_name, object_type, input_type, output_type)
    
    Args:
        node_list (list): List of (object_name, object_type, input_type, output_type) tuples
        adjacency_list (list): Adjacency list where adjacency_list[i] lists parents of i
        
    Modifies:
        node_list: Updates input_type and output_type for each object to ensure type compatibility
        adjacency_list: May remove edges to resolve type conflicts
    """
    topological_order = remove_cycles_and_get_topological_order(adjacency_list)

    for node_index in topological_order:
        parents = adjacency_list[node_index]
        if len(parents) == 0:
            input_type = random.choice(DATA_TYPES)
        else:
            parent_output_types = [node_list[parent_index][3] for parent_index in parents]
            unique_output_types = set(parent_output_types)
            if len(unique_output_types) == 1:
                input_type = unique_output_types.pop()
            else:
                chosen_type = random.choice(parent_output_types)
                input_type = chosen_type
                # Remove edges from parents that do not match the chosen type
                for parent_index in list(parents):
                    if node_list[parent_index][3] != chosen_type:
                        parents.remove(parent_index)

        object_name, object_type, _, _ = node_list[node_index]
        output_type = random.choice(DATA_TYPES)
        node_list[node_index] = (object_name, object_type, input_type, output_type)


def generate_codebase(
    num_objects=5,
    avg_length=10,
    branching_factor=2,
    loop_factor=1,
    connectivity=0.5,
    topology_mode="random",
    use_semantics=False
):
    """
    Generate a Python codebase with the given number of objects, approximate average lines,
    branching factor, loop factor, connectivity, and topology (chain, branch, or random DAG).

    Returns:
      complete_code (str): A single string containing all the generated Python code.
      node_list (list): Each element is (object_name, object_type, input_type, output_type).
      adjacency_list (list): adjacency_list[i] = list of parent indices for node i.
    """

    # 1) Build a parent-based adjacency list ignoring data types
    adjacency_list = build_adjacency_list(num_objects, topology_mode, connectivity)

    # 2) Possibly remove cycles if any exist
    remove_cycles_and_get_topological_order(adjacency_list)

    # 3) Create placeholders for node definitions
    node_list = []
    for index in range(num_objects):
        chosen_type = random.choice(["function", "class"])
        if use_semantics:
            parents = adjacency_list[index]
            if not parents:
                suffix = "start"
            elif len(parents) == 1:
                suffix = f"from_{parents[0]}"
            else:
                suffix = "_".join(str(p) for p in sorted(parents))
                suffix = f"merge_{suffix}"
            chosen_name = f"{'function' if chosen_type == 'function' else 'class'}_{suffix}"
        else:
            chosen_name = f"{chosen_type.capitalize()}_{index}"
        node_list.append((chosen_name, chosen_type, None, None))

    # 4) Unify the data types based on adjacency
    unify_types_based_on_adjacency(node_list, adjacency_list)

    # 5) Generate code objects in a final topological order
    topological_order = remove_cycles_and_get_topological_order(adjacency_list)
    code_sections = []

    # Build the actual function/class definitions
    for index, (object_name, object_type, input_type, output_type) in enumerate(node_list):
        estimated_lines = max(1, int(random.gauss(avg_length, avg_length * 0.2)))

        if object_type == "function":
            header = f"def {object_name}(parameter):"
            filler_line_count = max(0, estimated_lines - branching_factor - loop_factor)
            body_lines = generate_method_body(
                input_type,
                output_type,
                filler_line_count,
                branching_factor,
                loop_factor,
                adjacency_list[index],
                node_list
            )
            indented_body = "\n".join("    " + line for line in body_lines)
            code_definition = header + "\n" + indented_body + "\n"
            code_sections.append(code_definition)

        else:
            # Class
            class_header = f"class {object_name}:"
            class_lines = []

            init_header = "    def __init__(self):"
            init_body = ["pass  # minimal constructor"]
            class_lines.append(init_header)
            class_lines.extend("        " + line for line in init_body)

            # Primary run() method
            run_header = "    def run(self, parameter):"
            filler_for_run = max(0, estimated_lines // 2 - branching_factor - loop_factor)
            run_body_lines = generate_method_body(
                input_type,
                output_type,
                filler_for_run,
                branching_factor,
                loop_factor,
                adjacency_list[index],
                node_list
            )
            run_body_lines = ["        " + line for line in run_body_lines]
            class_lines.append(run_header)
            class_lines.extend(run_body_lines)

            # Extra methods for realism
            number_of_extra_methods = random.randint(1, 3)
            for extra_method_index in range(number_of_extra_methods):
                extra_input_type = random.choice(DATA_TYPES)
                extra_output_type = random.choice(DATA_TYPES)
                extra_method_header = f"    def method_{extra_method_index}(self, parameter):"
                filler_for_extra = max(0, estimated_lines // 3 - branching_factor - loop_factor)
                extra_method_body_lines = generate_method_body(
                    extra_input_type,
                    extra_output_type,
                    filler_for_extra,
                    branching_factor,
                    loop_factor,
                    [],  # no external dependencies for these extra methods
                    node_list
                )
                extra_method_body_lines = ["        " + line for line in extra_method_body_lines]
                class_lines.append(extra_method_header)
                class_lines.extend(extra_method_body_lines)

            class_definition = class_header + "\n" + "\n".join(class_lines) + "\n"
            code_sections.append(class_definition)

    # Build the main() function that runs in topological order
    main_lines = [
        "def main():",
        "    import math, cmath, random",
        "    results = {}",
    ]
    for node_index in topological_order:
        object_name, object_type, input_type, output_type = node_list[node_index]
        parents = adjacency_list[node_index]

        if not parents:
            # No parents => generate a random literal for input_type
            literal_value = generate_random_literal(input_type)
            main_lines.append(f"    parameter_value = {literal_value}  # object {node_index} input")
        else:
            # Use the first parent's output
            first_parent = parents[0]
            main_lines.append(f"    parameter_value = results[{first_parent}]  # from first parent")

        if object_type == "function":
            main_lines.append(f"    output_value = {object_name}(parameter_value)")
        else:
            instance_variable_name = f"instance_{node_index}"
            main_lines.append(f"    {instance_variable_name} = {object_name}()")
            main_lines.append(f"    output_value = {instance_variable_name}.run(parameter_value)")

        main_lines.append(f"    results[{node_index}] = output_value")
        main_lines.append("")

    main_lines.append("    print('Execution complete. Results:')")
    main_lines.append("    for key, value in results.items():")
    main_lines.append("        print(f'Object {key} output = {value}')")

    main_function_code = "\n".join(main_lines)
    entry_point_code = """\
if __name__ == "__main__":
    main()
"""

    complete_code = "\n".join(code_sections) + "\n" + main_function_code + "\n" + entry_point_code
    return complete_code, node_list, adjacency_list


def main():
    """
    An example usage of the generate_codebase function, printing out
    the generated code, node list, and adjacency list.
    """
    code_output, nodes_data, adjacency_data = generate_codebase(
        num_objects=5,
        avg_length=5,
        branching_factor=1,
        loop_factor=1,
        connectivity=1.0,         # full connectivity for "random" DAG
        topology_mode="random"
    )

    print("=== GENERATED CODE ===")
    print(code_output)
    print("\n=== NODE LIST (name, type, input_type, output_type) ===")
    for index, node_info in enumerate(nodes_data):
        print(index, node_info)
    print("\n=== ADJACENCY LIST ===")
    for index, parent_list in enumerate(adjacency_data):
        print(f"Object {index} depends on: {parent_list}")


if __name__ == "__main__":
    main()
