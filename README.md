# FlowChart

About:
Helps make a programming algorithm FlowChart by inputing minimal instructions.

Example:
Instructions to make a simple factorial program are,
start~START
io~Input i
process~fact = 1
loop~for j = 1 to i
process~fact*=j
connector~i~1.1~-2.-2
io~print fact
stop~STOP

Each segment of the instruction is seperated by a tilde(~)
The First Segment indicates the block type [Supported Block Types: start, stop, process, io, loop, connector, decision]
The Second Segment indicates the text in the block
The Third to Nth Segment indicate the connections the block has. (Defaulted to next block)

Installation:
1. Clone this git repo
2. Install libraries by running command
```
python3 -m pip install -r requirements.txt
```

Usage:
Run make_pdf.py script with appropriate arguments to make a pdf file of all input algorithms
Run algorithm.py script to make a single flow chart image with algorithm written next to it
Use flow_chart.py to make a single flow chart image
