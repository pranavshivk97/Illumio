# version account_id interface_id srcaddr dstaddr srcport dstport protocol packets bytes start end action log_status vpc-id subnet-id instance-id tcp-flags
import csv

def load_protocol_lookup(filename: str) -> dict:
    protocol = {}
    with open(filename, newline="", mode="r") as f:
        reader = csv.DictReader(f)
        try:
            for row in reader:
                if row["Decimal"] == "146-252":
                    for p in range(146, 253):
                        protocol[p] = "reserved"
                    continue
                protocol[int(row["Decimal"])] = row["Keyword"].lower()
        except KeyError as e:
            print(f"Error: {e}")
    return protocol

def load_lookup(filename: str) -> dict:
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
            print(f"Error: {e}")
    return lookup

def process_flow_logs(log_file: str, lookup: dict, protocol_map: dict) -> dict:
    tag_mappings = {key: 0 for key in lookup.values()}
    tag_mappings["Untagged"] = 0
    print(tag_mappings)
    with open(log_file, newline="", mode="r") as f:
        lines = f.readlines()

        for line in lines:
            fields = line.split()
            dstport = int(fields[5])
            protocol = protocol_map.get(int(fields[7]))
            if (dstport, protocol) in lookup:
                tag = lookup[(dstport, protocol)]
                print(f"Tag: {tag}")
                tag_mappings[tag] += 1
            else:
                print("No tag found")
                tag_mappings["Untagged"] += 1



    return tag_mappings

def write_to_output(output_file: str, tag_mappings: dict) -> None:
    with open(output_file, newline="", mode="w") as f:
        f.write("Tag Counts:\n\n")
        for tag, count in tag_mappings.items():
            f.write(f"{tag}, {count}\n")

        f.write("\nPort/Protocol Combination Counts:\n")


if __name__ == "__main__":
    protocol_lookup = load_protocol_lookup("protocol-map.csv")
    print(protocol_lookup)
    lookup = load_lookup("lookup.csv")
    print(lookup)
    tag_mappings = process_flow_logs("input.txt", lookup, protocol_lookup)
    print(tag_mappings)
    write_to_output("output.txt", tag_mappings)

