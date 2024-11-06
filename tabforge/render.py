from pathlib import Path
from textwrap import dedent
from typing import cast
from rich import print
from .error import Error
import jinja2
import re, sys, ctypes
from io import StringIO
from contextlib import redirect_stdout
from jinja2.ext import Extension
from jinja2 import nodes
import copy, os
from . import filters


class PythonExtension(Extension):
    tags = {"python"}

    def __init__(self, environment: jinja2.Environment):
        super().__init__(environment)
        self.capture_stdout = False

    def parse(self, parser):
        # We need this for reporting errors
        lineno = next(parser.stream).lineno
        body = parser.parse_statements(("name:endpython",), drop_needle=True)
        args = [
            nodes.ContextReference(),
            nodes.Const(lineno),
            nodes.Const(parser.filename),
        ]
        return nodes.CallBlock(
            self.call_method("_run_python", args), [], [], body
        ).set_lineno(lineno)

    def _run_python(self, ctx: jinja2.runtime.Context, lineno, filename, caller):
        # Adapted from https://stackoverflow.com/a/55545295
        # 1. Remove access indentation and compile the code.
        code = dedent(caller())
        compiled_code = compile("\n" * (lineno - 1) + code, filename, "exec")
        # 3. Execute the code with the context parents as global and context vars and locals.
        stdout = StringIO()
        try:

            def filter(f):
                # f.__name__
                ctx.environment.filters[f.__name__] = f
                print(f.__name__)
                return f

            ctx.parent["filter"] = filter
            ctx.parent["__file__"] = filename
            sys.path.append(str(Path(filename).parent))
            if self.capture_stdout:
                with redirect_stdout(stdout):
                    exec(compiled_code, copy.copy(ctx.parent), ctx.vars)
            else:
                exec(compiled_code, copy.copy(ctx.parent), ctx.vars)
        except Exception:
            raise
        finally:
            ctx.parent.pop("__file__", None)
            ctx.parent.pop("__name__", None)
        # 4. Get a set of all names in the code.
        code_names = set(compiled_code.co_names)
        # 5. Loop through and update all the locals.
        caller_frame = sys._getframe(2)  # The the executed frame
        var_name_regex = re.compile(r"l_(\d+)_(.+)")
        for local_var_name in caller_frame.f_locals:
            # Look for variables matching the template variable regex.
            if match := re.match(var_name_regex, local_var_name):
                var_name = match.group(2)
                # If the variable's name appears in the code and is in the locals.
                if (var_name in code_names) and (var_name in ctx.vars):
                    # Copy the value to the frame's locals.
                    caller_frame.f_locals[local_var_name] = ctx.vars[var_name]
                    # Do some ctypes vodo to make sure the frame locals are actually updated.
                    ctx.exported_vars.add(var_name)
                    ctypes.pythonapi.PyFrame_LocalsToFast(
                        ctypes.py_object(caller_frame), ctypes.c_int(1)
                    )
        # 6. Return the captured text.
        return stdout.getvalue() if self.capture_stdout else ""


def render_file(input: Path, output: Path, capture_stdout: bool, inject_builtins: bool):
    # Switch to the input file's directory
    curdir = Path(os.curdir).absolute()
    os.chdir(input.parent)
    input = Path(input.name)
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader("."),
        trim_blocks=True,
        block_start_string="<?",
        block_end_string="?>",
        variable_start_string="<?=",
        variable_end_string="?>",
        comment_start_string="<?#",
        comment_end_string="?>",
    )
    # Add builtins to the environment
    if inject_builtins:
        for k, v in __builtins__.items():
            if (
                k.startswith("__")
                or not callable(v)
                or k in ["copyright", "credits", "license", "help"]
            ):
                continue

            if k not in env.globals:
                env.globals[k] = v
    env.filters.update(filters.ALL_FILTERS)
    # Add the Python extension
    env.add_extension(PythonExtension)
    ext = cast(PythonExtension, env.extensions[PythonExtension.identifier])
    ext.capture_stdout = capture_stdout
    # Render the template
    template = env.get_template(str(input))
    try:
        output.write_text(HEADER + "\n" + template.render())
    except jinja2.TemplateError as e:
        raise Error(f'Error rendering "{input}": {e}')
    finally:
        os.chdir(curdir)


HEADER = "% This is an automatically generated file. Do not edit."
