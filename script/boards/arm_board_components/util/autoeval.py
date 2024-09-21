def autoeval(run):
    def wrapper(*args, **kwargs):
        import m5, json, os, sys
        from pathlib import Path

        here = Path(__file__)
        to_append = str(here.resolve().parent.parent.parent)
        sys.path.append(to_append)

        params = dict()
        arg_names = run.__code__.co_varnames[: run.__code__.co_argcount]
        for arg_name, arg_value in zip(arg_names, args):
            params[arg_name] = arg_value
        for kwarg_name, kwarg_value in kwargs.items():
            params[kwarg_name] = kwarg_value
        with open(
            os.path.join(m5.options.outdir, "params.json"), "w"
        ) as par_ser:
            json.dump(params, par_ser, indent=2)

        run(*args, **kwargs)

    return wrapper
