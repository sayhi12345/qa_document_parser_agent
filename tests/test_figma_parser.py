import pytest
from modules.figma_parser import collapse_text_nodes, find_node_by_names, aggregate_figma_content


class TestCollapseTextNodes:
    def test_empty_node(self):
        """Test with empty node tree."""
        node = {}
        accumulator = []
        collapse_text_nodes(node, accumulator)
        assert accumulator == []

    def test_text_node_with_content(self):
        """Test with a text node containing content."""
        node = {
            "type": "TEXT",
            "name": "標題",
            "characters": "活動說明"
        }
        accumulator = []
        collapse_text_nodes(node, accumulator)
        assert accumulator == ["標題: 活動說明"]

    def test_text_node_without_name(self):
        """Test text node without name."""
        node = {
            "type": "TEXT",
            "characters": "無名稱文字"
        }
        accumulator = []
        collapse_text_nodes(node, accumulator)
        assert accumulator == ["無名稱文字"]

    def test_nested_nodes(self):
        """Test with nested structure containing text nodes."""
        node = {
            "type": "FRAME",
            "name": "Container",
            "children": [
                {
                    "type": "TEXT",
                    "name": "Title",
                    "characters": "活動標題"
                },
                {
                    "type": "GROUP",
                    "children": [
                        {
                            "type": "TEXT",
                            "characters": "子文字"
                        }
                    ]
                }
            ]
        }
        accumulator = []
        collapse_text_nodes(node, accumulator)
        assert accumulator == ["Title: 活動標題", "子文字"]

    def test_empty_text_ignored(self):
        """Test that empty text content is ignored."""
        node = {
            "type": "TEXT",
            "name": "Empty",
            "characters": "   "
        }
        accumulator = []
        collapse_text_nodes(node, accumulator)
        assert accumulator == []


class TestFindNodeByNames:
    def test_find_at_root(self):
        """Test finding node at root level."""
        node = {
            "name": "活動說明",
            "type": "FRAME"
        }
        result = find_node_by_names(node, ["活動說明", "活動詳情"])
        assert result == node

    def test_find_in_children(self):
        """Test finding node in children."""
        target = {
            "name": "活動說明",
            "type": "FRAME"
        }
        root = {
            "name": "Root",
            "children": [
                {"name": "Other"},
                target
            ]
        }
        result = find_node_by_names(root, ["活動說明"])
        assert result == target

    def test_find_in_nested_children(self):
        """Test finding node in deeply nested structure."""
        target = {
            "name": "活動詳情",
            "type": "TEXT"
        }
        root = {
            "name": "Root",
            "children": [
                {
                    "name": "Level1",
                    "children": [
                        {
                            "name": "Level2",
                            "children": [target]
                        }
                    ]
                }
            ]
        }
        result = find_node_by_names(root, ["活動說明", "活動詳情"])
        assert result == target

    def test_not_found(self):
        """Test when node is not found."""
        root = {
            "name": "Root",
            "children": [
                {"name": "Other1"},
                {"name": "Other2"}
            ]
        }
        result = find_node_by_names(root, ["活動說明"])
        assert result is None

    def test_no_children(self):
        """Test node without children."""
        node = {
            "name": "Leaf",
            "type": "TEXT"
        }
        result = find_node_by_names(node, ["活動說明"])
        assert result is None


class TestAggregateFigmaContent:
    def test_minimal_document(self):
        """Test with minimal Figma JSON structure."""
        figma_json = {
            "document": {
                "type": "DOCUMENT",
                "name": "Test"
            }
        }
        result = aggregate_figma_content(figma_json)
        assert "=== Document Text ===" in result
        assert "（無文字節點）" in result

    def test_with_text_nodes(self):
        """Test with text nodes in document."""
        figma_json = {
            "document": {
                "type": "CANVAS",
                "children": [
                    {
                        "type": "TEXT",
                        "name": "標題",
                        "characters": "測試文字"
                    }
                ]
            }
        }
        result = aggregate_figma_content(figma_json)
        assert "標題: 測試文字" in result
        assert "=== Document Text ===" in result

    def test_with_components(self):
        """Test with components."""
        figma_json = {
            "document": {},
            "components": {
                "1:1": {
                    "name": "Button Component"
                },
                "1:2": {
                    "name": "Card Component"
                }
            }
        }
        result = aggregate_figma_content(figma_json)
        assert "=== Components ===" in result
        assert "元件 1:1: Button Component" in result
        assert "元件 1:2: Card Component" in result

    def test_with_styles(self):
        """Test with styles."""
        figma_json = {
            "document": {},
            "styles": {
                "S:1": {
                    "name": "Primary Color",
                    "styleType": "FILL"
                },
                "S:2": {
                    "name": "Heading",
                    "styleType": "TEXT"
                }
            }
        }
        result = aggregate_figma_content(figma_json)
        assert "=== Styles ===" in result
        assert "樣式 S:1: Primary Color (FILL)" in result
        assert "樣式 S:2: Heading (TEXT)" in result

    def test_complete_structure(self):
        """Test with complete structure including text, components, and styles."""
        figma_json = {
            "document": {
                "children": [
                    {
                        "type": "TEXT",
                        "characters": "活動內容"
                    }
                ]
            },
            "components": {
                "1:1": {"name": "Component1"}
            },
            "styles": {
                "S:1": {"name": "Style1", "styleType": "FILL"}
            }
        }
        result = aggregate_figma_content(figma_json)
        assert "活動內容" in result
        assert "Component1" in result
        assert "Style1" in result
