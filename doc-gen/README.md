# Connector Documentation Generator

Generates reference documentation (Markdown) for Ballerina-to-MI generated connectors by parsing UI schemas and XML metadata.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

Basic (offline, uses UI schema helpTip values only):
```bash
python generate_docs.py --input ../.generated/generated --output ../output/asb-connector-reference.md
```

With Ballerina Central field descriptions (requires internet):
```bash
python generate_docs.py --input ../.generated/generated --output ../output/asb-connector-reference.md --fetch-descriptions
```

## Options

| Flag | Description |
|------|-------------|
| `--input, -i` | Path to the generated connector directory (required) |
| `--output, -o` | Output markdown file path (default: `<connectorName>-connector-reference.md`) |
| `--fetch-descriptions` | Fetch field descriptions from Ballerina Central API |
