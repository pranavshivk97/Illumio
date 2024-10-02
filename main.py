import csv
import sys


class ProtocolLookup:
    """
    Class to handle protocol lookup
    """
    def __init__(self, filename: str):
        self.protocol = self.load("protocol-map.csv")

    def load(self, filename: str) -> dict:
        """
        Loads the protocol lookup, which maps from the protocol number to the protocol name
        :param filename: filename to load the lookup
        :return: dict that stores the protocol mappings
        """
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

    def get_string(self, protocol_number: int) -> str:
        """
        Get the protocol string from the protocol number
        :param protocol_number: the protocol number to get the string for
        :return: protocol string from mapping
        """
        return self.protocol.get(protocol_number, "unknown")


class Lookup:
    """
    Class to handle the lookup table
    """
    def __init__(self, filename: str):
        self.lookup_map = self.load(filename)

    def load(self, filename: str) -> dict:
        """
        Load the lookup table from the csv file and store in a dictionary
        :param filename: the file name to load the lookup table from
        :return: the dictionary that stores the lookup table
        """
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
        """
        Searches the lookup table for the tag based on the destination port and protocol
        :param dstport: the destination port to search for
        :param protocol: the protocol to search for
        :return: the tag found from the lookup table
        """
        return self.lookup_map.get((dstport, protocol), "Untagged")


class LogProcessor:
    """
    Class to process the flow logs
    """
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
        """
        Processes the log file and updates the tag mappings and port protocol counts
        :return: updated tag mappings and port protocol combinations as dictionaries
        """
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
    """
    Class to write the output to a file
    """
    @staticmethod
    def write_to_output(
        output_file: str, tag_mappings: dict, port_protocol_counts: dict
    ) -> None:
        """
        Writes the tag mappings and port protocol counts to the output file
        :param output_file: the output file to write to
        :param tag_mappings: the tag mappings write to the file
        :param port_protocol_counts: the port protocol combinations to write to the file
        """
        with open(output_file, newline="", mode="w") as file:
            file.write("Tag Counts:\n\n")
            for tag, count in tag_mappings.items():
                if count > 0:
                    file.write(f"{tag},{count}\n")

            file.write("\nPort/Protocol Combination Counts:\n\n")

            for (port, protocol), count in port_protocol_counts.items():
                file.write(f"{port},{protocol},{count}\n")


if __name__ == "__main__":
    protocol_lookup = ProtocolLookup("protocol-map.csv")
    lookup = Lookup("lookup.csv")
    processor = LogProcessor("input.txt", lookup, protocol_lookup)
    tag_mappings, port_protocol_counts = processor.process_flow_logs()
    OutputWriter.write_to_output("output.txt", tag_mappings, port_protocol_counts)
