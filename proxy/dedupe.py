def dedupe(file):
    proxies = []
    duplicates = 0
    with open(file, "r") as f:
        for line in f:
            proxy = line.replace("\n", "")
            if proxy not in proxies:
                proxies.append(proxy)
            else:
                duplicates += 1
    with open(file, "w") as f:
        for proxy in proxies:
            f.write(proxy + "\n")
    print(f"Removed {duplicates} duplicates")

if __name__ == "__main__":
    dedupe("output.txt")