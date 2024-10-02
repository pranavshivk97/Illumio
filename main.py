# version account_id interface_id srcaddr dstaddr srcport dstport protocol packets bytes start end action log_status vpc-id subnet-id instance-id tcp-flags
import csv


def load_lookup(filename: str) -> dict:
    lookup = {}
    with open(filename, newline="", mode="r") as f:
        reader = csv.DictReader(f)
        try:
            for row in reader:
                dstport = int(row["dstport"])
                protocol = int(row["protocol"])
                tag = row["tag"]
                lookup[(dstport, protocol)] = tag
        except KeyError as e:
            print(f"Error: {e}")
    return lookup


if __name__ == "__main__":
    lookup = load_lookup("lookup.csv")
