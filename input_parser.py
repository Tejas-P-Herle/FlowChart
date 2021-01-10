class InputParser:
    def __init__(self, fp, center=1):
        self.fp = fp
        self.center = center

    def parse_connections(self, connections, j):
        if connections == [""]:
            return []
        
        for i in range(len(connections)):
            txt = ""
            b_id = connections[i]
            if ":" in connections[i]:
                b_id, txt = connections[i].split(":")
            if "." in b_id:
                from_, to = b_id.split(".", 2)
                if from_ == to:
                    connections[i] = [j+int(to), txt]
                else:
                    connections[i] = [b_id, txt]
            elif b_id.isdigit():
                connections[i] = [int(b_id), txt]
        return connections

    def get_brs(self, conns, j):
        brs = []
        for c in conns:
            if isinstance(c[0], int) and c[0] > j:
                brs.append(c)
        return brs

    def instruct(self, flow_chart):
        all_connections = []
        pos = {}
        for j, (block_type, text, conns) in enumerate(self.read_blocks()):
            conns = self.parse_connections(conns, j)
            if j in pos:
                centers, rows = pos[j]
                center, flow_chart.row = sum(centers)/len(centers), max(rows)
            else:
                center = self.center
            block = flow_chart.draw(block_type, text, center)

            flow_chart.row = block.corners[2][1] + flow_chart.spacing
            br = self.get_brs(conns, j)
            c = (center * 2) / (len(br)+1)
            for k, conn in enumerate(br):
                if conn[0] not in pos:
                    pos[conn[0]] = [[], []]
                pos[conn[0]][0].append(c * (k + 1))
                pos[conn[0]][1].append(flow_chart.row)
            all_connections.append(conns)

        for i, connections in enumerate(all_connections):
            for connection in connections:
                if isinstance(connection[0], int):
                    flow_chart.connect(flow_chart.blocks[i],
                                       flow_chart.blocks[connection[0]],
                                       connection[1])
                elif isinstance(connection[0], str):
                    flow_chart.connect(flow_chart.blocks[i], *connection)

    def read_blocks(self):
        for ln in self.fp:
            if not ln.strip():
                break
            block_data = ln.split("~", 2)
            if len(block_data) == 2:
                block_type, text = [x.strip() for x in block_data]
                text = text.replace("\\n", "\n")
                if block_type not in ["end", "stop"]:
                    yield block_type, text, ["1.1"]
                else:
                    yield block_type, text, []

            else:
                block_type, text, connections = [x.strip() for x in block_data]
                text = text.replace("\\n", "\n")
                connections = [x.strip() for x in connections.split("~")]
                yield block_type, text, connections

