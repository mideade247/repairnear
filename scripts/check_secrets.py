import json
import sys


def main() -> int:
    findings = json.load(sys.stdin)["results"]
    for path, matches in sorted(findings.items()):
        for match in matches:
            print(f"{path}:{match['line_number']}: {match['type']}")
    if findings:
        print("Secret scan failed. Review the reported locations.", file=sys.stderr)
        return 1
    print("Secret scan passed for tracked working-tree files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
