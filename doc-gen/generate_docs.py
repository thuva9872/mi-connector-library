#!/usr/bin/env python3
"""Generate connector reference documentation from Ballerina-to-MI generated connector metadata."""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional

import requests

# ---------------------------------------------------------------------------
# Type mapping from UI schema inputType to documentation type
# ---------------------------------------------------------------------------
INPUT_TYPE_MAP = {
    "string": "String",
    "stringOrExpression": "String",
    "combo": "Enum",
    "boolean": "Boolean",
    "checkbox": "Boolean",
    "connection": "Connection",
    "number": "Number",
}


def map_input_type(input_type: str) -> str:
    return INPUT_TYPE_MAP.get(input_type, "String")


# ---------------------------------------------------------------------------
# Ballerina Central docs fetcher
# ---------------------------------------------------------------------------
class BallerinaCentralFetcher:
    """Fetch parameter/record field descriptions from Ballerina Central API."""

    API_URL = "https://api.central.ballerina.io/2.0/docs/{org}/{module}/{version}"
    REGISTRY_URL = "https://api.central.ballerina.io/2.0/registry/packages/{org}/{module}"

    def __init__(self, org: str, module: str, version: str):
        self.org = org
        self.module = module
        self.version = self._resolve_version(org, module, version)
        self._descriptions: Dict[str, str] = {}
        self._fetched = False

    def _resolve_version(self, org: str, module: str, version: str) -> str:
        """Resolve a short version (e.g. '3') to a full version (e.g. '3.9.1')."""
        if version.count(".") >= 2:
            return version  # Already a full version
        try:
            url = self.REGISTRY_URL.format(org=org, module=module)
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            versions = resp.json()
            # Find the latest version matching the major version prefix
            matching = [v for v in versions if v.startswith(version + ".") or v == version]
            if matching:
                resolved = matching[0]  # First is latest (descending order)
                print(f"  Resolved version {version} -> {resolved}")
                return resolved
        except Exception as e:
            print(f"  Warning: Could not resolve version {version}: {e}")
        return version

    def _fetch(self):
        if self._fetched:
            return
        self._fetched = True
        url = self.API_URL.format(org=self.org, module=self.module, version=self.version)
        print(f"  Fetching Ballerina Central docs from: {url}")
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"  Warning: Failed to fetch Ballerina Central docs: {e}")
            return

        modules = data.get("docsData", {}).get("modules", [])
        for mod in modules:
            # Extract record field descriptions
            for record in mod.get("records", []):
                record_name = record.get("name", "")
                for field in record.get("fields", []):
                    field_name = field.get("name", "")
                    desc = field.get("description", "").strip()
                    if desc:
                        # Store as both qualified and unqualified
                        self._descriptions[f"{record_name}.{field_name}"] = desc
                        # Also store unqualified for simple lookups
                        if field_name not in self._descriptions:
                            self._descriptions[field_name] = desc

            # Extract client method parameter descriptions
            for client in mod.get("clients", []):
                for method in client.get("methods", []):
                    method_name = method.get("name", "")
                    for param in method.get("parameters", []):
                        param_name = param.get("name", "")
                        desc = param.get("description", "").strip()
                        if desc:
                            self._descriptions[f"{method_name}.{param_name}"] = desc
                            if param_name not in self._descriptions:
                                self._descriptions[param_name] = desc
                    # Also check return type descriptions
                    ret_params = method.get("returnParameters")
                    if isinstance(ret_params, dict):
                        ret_desc = ret_params.get("description", "")
                        if ret_desc:
                            self._descriptions[f"{method_name}.return"] = ret_desc.strip()

        print(f"  Loaded {len(self._descriptions)} field descriptions from Ballerina Central")

    def get_description(self, field_name: str, method_name: str = "") -> str:
        self._fetch()
        # Try method-qualified first, then plain field name
        if method_name:
            desc = self._descriptions.get(f"{method_name}.{field_name}", "")
            if desc:
                return desc
        return self._descriptions.get(field_name, "")


# ---------------------------------------------------------------------------
# Connector metadata parsers
# ---------------------------------------------------------------------------

def parse_connector_xml(connector_xml_path: str) -> dict:
    """Parse connector.xml to extract connector name, display name, description."""
    tree = ET.parse(connector_xml_path)
    root = tree.getroot()

    component = root.find("component")
    connector_name = component.get("name", "") if component is not None else ""
    display_name_el = root.find("displayName")
    display_name = display_name_el.text if display_name_el is not None else connector_name

    description = ""
    if component is not None:
        desc_el = component.find("description")
        if desc_el is not None and desc_el.text:
            description = html.unescape(desc_el.text)

    # Extract component dependencies
    dependencies = []
    if component is not None:
        for dep in component.findall("dependency"):
            dep_name = dep.get("component", "")
            if dep_name and dep_name != "config":
                dependencies.append(dep_name)

    return {
        "name": connector_name,
        "displayName": display_name,
        "description": description,
        "dependencies": dependencies,
    }


def parse_component_xml(component_xml_path: str) -> dict:
    """Parse a component.xml to extract operation display names and descriptions."""
    tree = ET.parse(component_xml_path)
    root = tree.getroot()

    operations = {}
    for sub in root.findall(".//subComponents/component"):
        name = sub.get("name", "")
        display_el = sub.find("displayName")
        desc_el = sub.find("description")
        operations[name] = {
            "displayName": display_el.text if display_el is not None else name,
            "description": html.unescape(desc_el.text) if desc_el is not None and desc_el.text else "",
        }
    return operations


def parse_operation_xml(operation_xml_path: str) -> dict:
    """Parse an operation XML template to extract org/module/version info."""
    tree = ET.parse(operation_xml_path)
    root = tree.getroot()
    ns = {"ns": "http://ws.apache.org/ns/synapse"}

    info = {}
    class_el = root.find(".//ns:sequence/ns:class", ns)
    if class_el is not None:
        for prop in class_el.findall("ns:property", ns):
            prop_name = prop.get("name", "")
            prop_value = prop.get("value", "")
            if prop_name in ("orgName", "moduleName", "version"):
                info[prop_name] = prop_value
    return info


def extract_attributes(elements: list, group_prefix: str = "") -> list[dict]:
    """Recursively extract attributes from UI schema elements."""
    attrs = []
    for el in elements:
        el_type = el.get("type", "")
        value = el.get("value", el)

        if el_type == "attribute":
            attr = {
                "name": value.get("name", ""),
                "displayName": value.get("displayName", ""),
                "inputType": value.get("inputType", ""),
                "defaultValue": value.get("defaultValue", ""),
                "required": value.get("required", False),
                "helpTip": value.get("helpTip", ""),
                "comboValues": value.get("comboValues", []),
                "enableCondition": value.get("enableCondition", []),
                "group": group_prefix,
            }
            attrs.append(attr)
        elif el_type == "attributeGroup":
            group_name = value.get("groupName", "")
            sub_elements = value.get("elements", [])
            # Skip the top-level "General" and "Output" wrappers for grouping,
            # but use sub-group names like "Auto Delete On Idle", "Application Properties"
            if group_name in ("General",):
                attrs.extend(extract_attributes(sub_elements, group_prefix))
            elif group_name in ("Input Variables",):
                attrs.extend(extract_attributes(sub_elements, group_prefix))
            elif group_name == "Output":
                attrs.extend(extract_attributes(sub_elements, "Output"))
            else:
                new_prefix = f"{group_prefix} > {group_name}" if group_prefix else group_name
                attrs.extend(extract_attributes(sub_elements, new_prefix))
    return attrs


def parse_ui_schema(schema_path: str) -> dict:
    """Parse a UI schema JSON file."""
    with open(schema_path) as f:
        data = json.load(f)

    is_connection = "connectionName" in data
    result = {
        "connectorName": data.get("connectorName", ""),
        "title": data.get("title", ""),
        "help": data.get("help", ""),
        "isConnection": is_connection,
    }

    if is_connection:
        result["connectionName"] = data.get("connectionName", "")
    else:
        result["operationName"] = data.get("operationName", "")

    elements = data.get("elements", [])
    result["attributes"] = extract_attributes(elements)

    return result


# ---------------------------------------------------------------------------
# Markdown generation
# ---------------------------------------------------------------------------

def format_required(val) -> str:
    if isinstance(val, str):
        return "Yes" if val.lower() == "true" else "No"
    return "Yes" if val else "No"


def build_description(attr: dict, fetcher: BallerinaCentralFetcher | None, method_name: str = "") -> str:
    """Build a rich description for a parameter."""
    desc = attr.get("helpTip", "").strip()

    # Try to enrich from Ballerina Central if description is empty
    if not desc and fetcher:
        field_name = attr["name"]
        # Strip group prefixes (e.g., "autoDeleteOnIdle.seconds" -> "seconds" with record context)
        desc = fetcher.get_description(field_name, method_name)
        if not desc and "." in field_name:
            # Try the base field name
            base = field_name.split(".")[-1]
            desc = fetcher.get_description(base, method_name)

    # Add combo values to description
    combo_values = attr.get("comboValues", [])
    if combo_values:
        values_str = ", ".join(f"<code>{v}</code>" for v in combo_values)
        if desc:
            desc += f"<br/><b>Possible values</b>: {values_str}"
        else:
            desc = f"<b>Possible values</b>: {values_str}"

    return desc if desc else "-"


def generate_param_table(attrs: list[dict], fetcher: BallerinaCentralFetcher | None,
                         method_name: str = "") -> str:
    """Generate an HTML parameter table from a list of attributes."""
    rows = []
    for attr in attrs:
        # Skip connection ref attributes in operation docs
        if attr["inputType"] == "connection":
            continue

        name = attr["displayName"] or attr["name"]
        element = attr["name"]
        param_type = map_input_type(attr["inputType"])
        desc = build_description(attr, fetcher, method_name)
        default = attr["defaultValue"] if attr["defaultValue"] else "-"
        required = format_required(attr["required"])

        # Add group context to display name if in a sub-group
        group = attr.get("group", "")
        if group and group not in ("Output",):
            name = f"{name}<br/><small>({group})</small>"

        rows.append(f"""<tr>
<td>{name}</td>
<td>{element}</td>
<td>{param_type}</td>
<td>{desc}</td>
<td>{default}</td>
<td>{required}</td>
</tr>""")

    table = """<table>
<tr>
<th>Parameter Name</th>
<th>Element</th>
<th>Type</th>
<th>Description</th>
<th>Default Value</th>
<th>Required</th>
</tr>
""" + "\n".join(rows) + "\n</table>"
    return table


def generate_sample_xml(connector_name: str, operation_name: str, attrs: list[dict]) -> str:
    """Generate a sample XML configuration for an operation."""
    # Filter to input params only (skip connection, output)
    input_params = [a for a in attrs
                    if a["inputType"] != "connection"
                    and a["name"] not in ("responseVariable", "overwriteBody")
                    and a.get("group", "") != "Output"
                    and a.get("required")]

    lines = [f'<{connector_name}.{operation_name} configKey="CONNECTION_NAME">']
    for attr in input_params:
        param_name = attr["name"]
        lines.append(f"    <{param_name}>{{$ctx:{param_name}}}</{param_name}>")
    lines.append(f"    <responseVariable>{connector_name}_{operation_name}_1</responseVariable>")
    lines.append(f"    <overwriteBody>false</overwriteBody>")
    lines.append(f"</{connector_name}.{operation_name}>")
    return "\n".join(lines)


def generate_connection_sample_xml(connector_name: str, connection_name: str,
                                   attrs: list[dict]) -> str:
    """Generate a sample XML init config for a connection type."""
    lines = [f'<{connector_name}.init>']
    lines.append(f'    <connectionType>{connection_name}</connectionType>')
    for attr in attrs:
        if attr["name"] in ("connectionName",):
            continue
        if attr.get("required") and str(attr.get("required")).lower() == "true":
            param_name = attr["name"]
            lines.append(f"    <{param_name}>{{$ctx:{param_name}}}</{param_name}>")
    lines.append(f'</{connector_name}.init>')
    return "\n".join(lines)


def indent_block(text: str, spaces: int = 4) -> str:
    """Indent every line of text by the given number of spaces."""
    prefix = " " * spaces
    return "\n".join(prefix + line if line.strip() else line for line in text.split("\n"))


# ---------------------------------------------------------------------------
# Main generation logic
# ---------------------------------------------------------------------------

def generate_docs(input_dir: str, output_path: str, fetch_descriptions: bool = False):
    """Main entry point: parse all metadata and generate the reference doc."""

    print(f"Reading connector metadata from: {input_dir}")

    # 1. Parse connector.xml
    connector_xml = os.path.join(input_dir, "connector.xml")
    if not os.path.exists(connector_xml):
        print(f"Error: connector.xml not found at {connector_xml}")
        sys.exit(1)
    connector_info = parse_connector_xml(connector_xml)
    connector_name = connector_info["name"]
    print(f"  Connector: {connector_name} ({connector_info['displayName']})")

    # 2. Get org/module/version from any operation XML for Ballerina Central
    org_name, module_name, module_version = "", "", ""
    for dep in connector_info["dependencies"]:
        comp_dir = os.path.join(input_dir, dep)
        if os.path.isdir(comp_dir):
            for f in os.listdir(comp_dir):
                if f.endswith(".xml") and f != "component.xml":
                    info = parse_operation_xml(os.path.join(comp_dir, f))
                    if info.get("orgName"):
                        org_name = info["orgName"]
                        module_name = info["moduleName"]
                        module_version = info["version"]
                        break
            if org_name:
                break
    print(f"  Ballerina module: {org_name}/{module_name}/{module_version}")

    # 3. Initialize Ballerina Central fetcher
    fetcher = None
    if fetch_descriptions and org_name and module_name and module_version:
        fetcher = BallerinaCentralFetcher(org_name, module_name, module_version)

    # 4. Parse all UI schemas
    uischema_dir = os.path.join(input_dir, "uischema")
    connection_schemas = []
    operation_schemas = []

    for fname in sorted(os.listdir(uischema_dir)):
        if not fname.endswith(".json"):
            continue
        schema = parse_ui_schema(os.path.join(uischema_dir, fname))
        if schema["isConnection"]:
            connection_schemas.append(schema)
        else:
            operation_schemas.append(schema)

    print(f"  Found {len(connection_schemas)} connection types, {len(operation_schemas)} operations")

    # 5. Parse component.xml files for operation descriptions
    all_op_descriptions = {}
    for dep in connector_info["dependencies"]:
        comp_xml = os.path.join(input_dir, dep, "component.xml")
        if os.path.exists(comp_xml):
            ops = parse_component_xml(comp_xml)
            all_op_descriptions.update(ops)

    # 6. Group operations by component
    component_operations: dict[str, list] = {}
    for schema in operation_schemas:
        op_name = schema.get("operationName", "")
        # e.g. "Administrator_createQueue" -> component="Administrator"
        parts = op_name.split("_", 1)
        component = parts[0] if len(parts) > 1 else ""
        if component not in component_operations:
            component_operations[component] = []
        component_operations[component].append(schema)

    # 7. Build the markdown document
    md = []

    # Title
    md.append(f"# {connector_info['displayName'].upper()} Connector Reference\n")
    md.append(f"The following configurations allow you to work with the "
              f"{connector_info['displayName'].upper()} Connector.\n")

    # Overview (from connector.xml description)
    if connector_info["description"]:
        md.append(connector_info["description"])
        md.append("")

    # Connection Configurations
    md.append("## Connection Configurations\n")
    md.append("The following connection types are available:\n")

    for conn in connection_schemas:
        conn_name = conn.get("connectionName", "")
        conn_title = conn.get("title", conn_name)
        attrs = conn["attributes"]

        # Extract method name for Ballerina Central lookup
        # e.g. "asb_MessageSender" -> client init params
        method_name = conn_name.split("_")[-1] if "_" in conn_name else ""

        md.append(f'??? note "{conn_title}"')
        help_text = conn.get("help", "").strip()
        if help_text:
            # Strip HTML tags for clean text
            clean_help = re.sub(r'<[^>]+>', '', help_text).strip()
            md.append(indent_block(clean_help))
            md.append("")

        table = generate_param_table(attrs, fetcher, method_name)
        md.append(indent_block(table))
        md.append("")

        # Sample config
        sample = generate_connection_sample_xml(connector_name, conn_name, attrs)
        md.append(indent_block("**Sample configuration**"))
        md.append(indent_block("```xml"))
        md.append(indent_block(sample))
        md.append(indent_block("```"))
        md.append("")

    # Operations
    md.append("## Operations\n")
    md.append("The following operations allow you to work with the "
              f"{connector_info['displayName'].upper()} Connector. "
              "Click an operation name to see parameter details and samples on how to use it.\n")

    for component_name in connector_info["dependencies"]:
        ops = component_operations.get(component_name, [])
        if not ops:
            continue

        md.append(f"### {component_name}\n")

        for schema in ops:
            op_name = schema.get("operationName", "")
            op_title = schema.get("title", op_name)
            attrs = schema["attributes"]

            # Get description from component.xml
            op_desc_info = all_op_descriptions.get(op_name, {})
            op_description = op_desc_info.get("description", "")
            help_text = schema.get("help", "").strip()

            # Extract the Ballerina function name for Central lookup
            func_name = op_name.split("_")[-1] if "_" in op_name else op_name

            md.append(f'??? note "{op_title}"')

            # Add help text (operation description)
            if help_text:
                # Clean up the help text - keep the text description, format code blocks
                md.append(indent_block(help_text))
                md.append("")

            # Parameter table
            table = generate_param_table(attrs, fetcher, func_name)
            md.append(indent_block(table))
            md.append("")

            # Sample XML config
            sample = generate_sample_xml(connector_name, op_name, attrs)
            md.append(indent_block("**Sample configuration**"))
            md.append(indent_block("```xml"))
            md.append(indent_block(sample))
            md.append(indent_block("```"))
            md.append("")

    # Write output
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(output_path, "w") as f:
        f.write("\n".join(md))

    print(f"\nDocumentation generated at: {output_path}")
    print(f"  Connections: {len(connection_schemas)}")
    print(f"  Operations: {len(operation_schemas)}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate connector reference documentation from generated connector metadata."
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to the generated connector directory (e.g., .generated/generated)"
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output markdown file path (default: <connectorName>-connector-reference.md)"
    )
    parser.add_argument(
        "--fetch-descriptions",
        action="store_true",
        default=False,
        help="Fetch field descriptions from Ballerina Central (requires internet)"
    )
    args = parser.parse_args()

    input_dir = os.path.abspath(args.input)
    if not os.path.isdir(input_dir):
        print(f"Error: Input directory not found: {input_dir}")
        sys.exit(1)

    # Determine output path
    if args.output:
        output_path = os.path.abspath(args.output)
    else:
        # Parse connector name for default output filename
        connector_xml = os.path.join(input_dir, "connector.xml")
        if os.path.exists(connector_xml):
            info = parse_connector_xml(connector_xml)
            output_path = os.path.abspath(f"{info['name']}-connector-reference.md")
        else:
            output_path = os.path.abspath("connector-reference.md")

    generate_docs(input_dir, output_path, fetch_descriptions=args.fetch_descriptions)


if __name__ == "__main__":
    main()
