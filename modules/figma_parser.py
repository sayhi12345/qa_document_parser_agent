from typing import Any, Dict, List, Optional


def collapse_text_nodes(node: Dict[str, Any], accumulator: List[str]) -> None:
    node_type = node.get("type", "")
    name = node.get("name", "")
    if node_type == "TEXT":
        characters = node.get("characters", "")
        text_content = characters.strip()
        if text_content:
            accumulator.append(f"{name}: {text_content}" if name else text_content)
    for child in node.get("children", []) or []:
        collapse_text_nodes(child, accumulator)


def find_node_by_names(node: Dict[str, Any], names: List[str]) -> Optional[Dict[str, Any]]:
    if node.get("name") in names:
        return node

    children = node.get("children", [])
    if not children:
        return None

    for child in children:
        found = find_node_by_names(child, names)
        if found:
            return found
    return None


def aggregate_figma_content(figma_json: Dict[str, Any]) -> str:
    document = figma_json.get("document", {})
    components = figma_json.get("components", {})
    styles = figma_json.get("styles", {})
    text_fragments: List[str] = []
    collapse_text_nodes(document, text_fragments)

    component_info = "\n".join(
        f"元件 {k}: {v.get('name', '')}"
        for k, v in components.items()
        if isinstance(v, dict)
    )
    style_info = "\n".join(
        f"樣式 {k}: {v.get('name', '')} ({v.get('styleType', '')})"
        for k, v in styles.items()
        if isinstance(v, dict)
    )

    sections = [
        "=== Document Text ===",
        "\n".join(text_fragments) or "（無文字節點）",
    ]
    if component_info:
        sections.extend(["=== Components ===", component_info])
    if style_info:
        sections.extend(["=== Styles ===", style_info])
    return "\n".join(sections)
