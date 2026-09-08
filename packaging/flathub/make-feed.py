import base64, binascii, json, pathlib, sys

root = pathlib.Path(sys.argv[1])
out = pathlib.Path(sys.argv[2])
entries = []
for sha_file in sorted(root.rglob("*.nupkg.sha512")):
    pid = sha_file.parent.parent.name
    ver = sha_file.parent.name
    fn = f"{pid}.{ver}.nupkg"
    url = f"https://api.nuget.org/v3-flatcontainer/{pid.lower()}/{ver}/{fn}"
    sha512 = binascii.hexlify(base64.b64decode(sha_file.read_text().strip())).decode()
    entries.append({"type": "file", "url": url, "sha512": sha512, "dest": "nuget-sources", "dest-filename": fn})
out.write_text(json.dumps(sorted(entries, key=lambda e: e["dest-filename"]), indent=1))
names = [e["dest-filename"] for e in entries]
print("packages:", len(entries))
print("ILLink:", [n for n in names if "illink" in n])
print("onnxGpuLinux:", [n for n in names if "onnxruntime.gpu.linux" in n])
print("runtime:", sorted(n for n in names if "runtime.linux-x64" in n))
