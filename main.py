import csv
import sys


class ProtocolLookup:
    def __init__(self, filename: str):
        self.protocol = self.load("protocol-map.csv")

    def load(self, filename: str) -> dict:
        protocol = {}
        with open(filename, newline="", mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["Decimal"] == "146-252":
                    for p in range(146, 253):
                        protocol[p] = "reserved"
                else:
                    protocol[int(row["Decimal"])] = row["Keyword"].lower()

        return protocol

    def get_string(self, protocol: int) -> str:
        return self.protocol.get(protocol, "unknown")


class Lookup:
    def __init__(self, filename: str):
        self.lookup_map = self.load(filename)

    def load(self, filename: str) -> dict:
        lookup = {}
        with open(filename, newline="", mode="r") as f:
            reader = csv.DictReader(f)
            try:
                for row in reader:
                    dstport = int(row["dstport"])
                    protocol = row["protocol"]
                    tag = row["tag"]
                    lookup[(dstport, protocol)] = tag
            except KeyError as e:
                print(f"Failed to load lookup: {e}")
                sys.exit(1)

        return lookup

    def get_tag(self, dstport: int, protocol: str) -> str:
        return self.lookup_map.get((dstport, protocol), "Untagged")


class LogProcessor:
    def __init__(self, log_file: str, lookup: Lookup, protocol: ProtocolLookup):
        self.log_file = log_file
        self.lookup = lookup
        self.protocol = protocol
        self.tag_mappings = {
            **dict.fromkeys(self.lookup.lookup_map.values(), 0),
            "Untagged": 0,
        }
        self.port_protocol_counts = {}

    def process_flow_logs(self) -> (dict, dict):
        with open(self.log_file, newline="", mode="r") as file:
            for line in file.readlines():
                fields = line.split()
                dstport = int(fields[5])

                protocol_number = int(fields[7])
                protocol = self.protocol.get_string(protocol_number)

                tag = self.lookup.get_tag(dstport, protocol)

                # Update the tag mappings and port protocol counts
                self.tag_mappings[tag] += 1
                self.port_protocol_counts[(dstport, protocol)] = (
                    self.port_protocol_counts.get((dstport, protocol), 0) + 1
                )

        return self.tag_mappings, self.port_protocol_counts


class OutputWriter:
    @staticmethod
    def write_to_output(
        output_file: str, tag_mappings: dict, port_protocol: dict
    ) -> None:
        with open(output_file, newline="", mode="w") as file:
            file.write("Tag Counts:\n\n")
            for tag, count in tag_mappings.items():
                if count > 0:
                    file.write(f"{tag},{count}\n")

            file.write("\nPort/Protocol Combination Counts:\n\n")

            for (port, protocol), count in port_protocol.items():
                file.write(f"{port},{protocol},{count}\n")


if __name__ == "__main__":
    protocol_lookup = ProtocolLookup("protocol-map.csv")
    lookup = Lookup("lookup.csv")
    processor = LogProcessor("input.txt", lookup, protocol_lookup)
    tag_mappings, port_protocol_counts = processor.process_flow_logs()
    OutputWriter.write_to_output("output.txt", tag_mappings, port_protocol_counts)
