#!/usr/bin/env python3

import sys
from PIL import Image
from algorithm import Page


sheet = (2480, 3508)


def print_usage(extra_msg="", exit_code=64):
    print("Usage: ./make_pdf.py ouput_path -a algo_paths... -i inst_paths...",
          file=sys.stderr)
    if extra_msg:
        print(extra_msg, file=sys.stderr)
    sys.exit(exit_code)


def get_args(args):
    if not args:
        print_usage()
    output_path = args.pop(0)
    if output_path[0] == "-" or not output_path.endswith(".pdf"):
        print_usage()
    
    options = {"-i": [], "-a": [], "-s": []}
    
    files = options[args.pop(0)]
    for arg in args:
        if arg in options:
            files = options[arg]
        else:
            files.append(arg)
    return output_path, options


def main():
    images = []
    program_name = sys.argv.pop(0)
    output_path, args = get_args(sys.argv)
    algos, insts = args["-a"], args["-i"]

    if len(algos) != len(insts):
        print_usage("Algorithm and Instruction Files don't match up", 65)
    
    for j, (algo_path, inst_path) in enumerate(zip(algos, insts)):
        page = Page(algo_path, "RGB", sheet, color="white")
        page.beautify()
        page.add_flow_chart(inst_path, sheet[0]//2, sheet[1])
        page.add_algorithm(sheet[0]//2, 0)
        
        if args["-s"]:
            if "{}" in args["-s"][0]:
                page.im.save(args["-s"][0].format(j+1))
            else:
                if args["-s"][0] and args["-s"][0][-1] == "/":
                    args["-s"][0] = args["-s"][0][:-1]
                page.im.save(args["-s"][0]+"/{}.png".format(j+1))
        images.append(page.im)

    im = images.pop(0)
    im.save(output_path ,resolution=100.0, save_all=True, append_images=images)


if __name__ == "__main__":
    main()

