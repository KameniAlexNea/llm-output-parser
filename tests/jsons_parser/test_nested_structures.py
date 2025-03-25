import unittest

from llm_output_parser.jsons_parser import parse_jsons


class TestNestedStructures(unittest.TestCase):
    def test_deeply_nested_object(self):
        """Test parsing a deeply nested JSON object"""
        json_str = """
        {
            "person": {
                "name": "John",
                "address": {
                    "street": {
                        "name": "Main St",
                        "number": 123
                    },
                    "city": "Anytown",
                    "country": {
                        "name": "USA",
                        "code": "US"
                    }
                }
            }
        }
        """
        result = parse_jsons(json_str)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["person"]["address"]["street"]["number"], 123)
        self.assertEqual(result[0]["person"]["address"]["country"]["name"], "USA")

    def test_complex_array_nesting(self):
        """Test parsing complex array nesting"""
        json_str = """
        {
            "data": [
                {"id": 1, "values": [10, 20, 30]},
                {"id": 2, "values": [
                    {"x": 5, "y": [1, 2, 3]},
                    {"x": 6, "y": [4, 5, 6]}
                ]}
            ]
        }
        """
        result = parse_jsons(json_str)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["data"][0]["values"], [10, 20, 30])
        self.assertEqual(result[0]["data"][1]["values"][1]["y"], [4, 5, 6])

    def test_mixed_nesting_with_different_types(self):
        """Test parsing with different data types and nesting"""
        json_str = """
        {
            "boolean": true,
            "number": 42.5,
            "string": "hello",
            "null_value": null,
            "array": [1, "two", false, null, {"key": "value"}],
            "object": {
                "nested_array": [1, [2, [3]]],
                "nested_object": {"a": {"b": {"c": "deep"}}}
            }
        }
        """
        result = parse_jsons(json_str)
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0]["boolean"])
        self.assertEqual(result[0]["number"], 42.5)
        self.assertEqual(result[0]["string"], "hello")
        self.assertIsNone(result[0]["null_value"])
        self.assertEqual(result[0]["array"][4]["key"], "value")
        self.assertEqual(result[0]["object"]["nested_array"][1][1][0], 3)
        self.assertEqual(result[0]["object"]["nested_object"]["a"]["b"]["c"], "deep")

    def test_extremely_deeply_nested_json(self):
        """Test parsing extremely deeply nested JSON that approaches parser limits"""
        # Create a deeply nested structure programmatically
        depth = 50  # Very deep nesting

        # Start with the innermost value
        inner_json = '{"value": "center"}'

        # Wrap it multiple times
        for i in range(depth):
            inner_json = f'{{"level_{i}": {inner_json}}}'

        result = parse_jsons(inner_json)
        self.assertEqual(len(result), 1)

        # Navigate to the center and verify
        current = result[0]
        for i in range(depth - 1, -1, -1):
            self.assertIn(f"level_{i}", current)
            current = current[f"level_{i}"]

        self.assertEqual(current["value"], "center")

    def test_complex_heterogeneous_data_structure(self):
        """Test parsing a complex structure with mixed types and irregular nesting"""
        json_str = """
        {
            "metadata": {
                "version": "3.2.1",
                "generated": "2023-08-15T14:38:12Z",
                "source": {
                    "type": "api",
                    "endpoint": "https://api.example.com/v2/data",
                    "parameters": {
                        "limit": 100,
                        "offset": 0,
                        "filters": ["active=true", "category=electronics"]
                    }
                }
            },
            "results": [
                {
                    "id": "PRD-123456",
                    "categories": [
                        ["Electronics", "Computers", "Laptops"],
                        ["Back to School", "Technology"],
                        ["Featured"]
                    ],
                    "specs": {
                        "dimensions": {"width": 12.8, "height": 0.8, "depth": 8.94, "unit": "in"},
                        "weight": {"value": 3.1, "unit": "lbs"},
                        "performance": [
                            {"benchmark": "GeekBench", "scores": [1240, 3580]},
                            {"benchmark": "CineBench", "scores": [{"single": 510, "multi": 2340}]}
                        ]
                    },
                    "market_data": {
                        "us": {
                            "msrp": 1299.99,
                            "sale_price": 1099.99,
                            "currency": "USD",
                            "availability": [
                                {"store_id": "ST-001", "quantity": 23, "reserved": 5},
                                {"store_id": "ST-002", "quantity": 0, "reserved": 0}
                            ]
                        },
                        "eu": {
                            "msrp": 1399.00,
                            "sale_price": 1199.00,
                            "currency": "EUR",
                            "availability": [
                                {"store_id": "ST-103", "quantity": 10, "reserved": 2}
                            ]
                        }
                    }
                },
                {
                    "id": "PRD-789012",
                    "categories": [
                        ["Electronics", "Audio", "Headphones"],
                        ["Bestsellers"]
                    ],
                    "specs": {
                        "dimensions": {"width": 7.5, "height": 6.2, "depth": 3.1, "unit": "in"},
                        "weight": {"value": 0.55, "unit": "lbs"},
                        "performance": [
                            {"benchmark": "AudioFidelity", "scores": [87, 92, 89]},
                            {"benchmark": "BatteryLife", "scores": {"wireless": 28.5, "noise_canceling": 18.2}}
                        ]
                    },
                    "market_data": {
                        "us": {
                            "msrp": 349.99,
                            "sale_price": 299.99,
                            "currency": "USD",
                            "availability": [
                                {"store_id": "ST-001", "quantity": 42, "reserved": 8},
                                {"store_id": "ST-002", "quantity": 15, "reserved": 3}
                            ]
                        }
                    }
                }
            ],
            "pagination": {
                "total_results": 2,
                "page_size": 100,
                "current_page": 1,
                "total_pages": 1,
                "links": {
                    "self": "https://api.example.com/v2/data?limit=100&offset=0",
                    "first": "https://api.example.com/v2/data?limit=100&offset=0",
                    "last": "https://api.example.com/v2/data?limit=100&offset=0"
                }
            }
        }
        """

        result = parse_jsons(json_str)
        self.assertEqual(len(result), 1)

        # Test navigation through the complex structure
        data = result[0]

        # Check metadata
        self.assertEqual(data["metadata"]["version"], "3.2.1")
        self.assertEqual(
            data["metadata"]["source"]["endpoint"], "https://api.example.com/v2/data"
        )
        self.assertEqual(len(data["metadata"]["source"]["parameters"]["filters"]), 2)

        # Check results - laptop
        laptop = data["results"][0]
        self.assertEqual(laptop["id"], "PRD-123456")
        self.assertEqual(laptop["categories"][0][2], "Laptops")
        self.assertEqual(laptop["specs"]["dimensions"]["height"], 0.8)
        self.assertEqual(laptop["specs"]["performance"][1]["scores"][0]["multi"], 2340)
        self.assertEqual(laptop["market_data"]["us"]["availability"][0]["quantity"], 23)
        self.assertEqual(laptop["market_data"]["eu"]["currency"], "EUR")

        # Check results - headphones
        headphones = data["results"][1]
        self.assertEqual(headphones["id"], "PRD-789012")
        self.assertEqual(headphones["categories"][0][2], "Headphones")
        self.assertEqual(headphones["specs"]["performance"][0]["scores"][1], 92)
        self.assertAlmostEqual(
            headphones["specs"]["performance"][1]["scores"]["wireless"], 28.5
        )

        # Check pagination
        self.assertEqual(data["pagination"]["total_results"], 2)
        self.assertEqual(
            data["pagination"]["links"]["last"],
            "https://api.example.com/v2/data?limit=100&offset=0",
        )

    def test_recursive_structure(self):
        """Test parsing a structure with recursive or self-referential patterns"""
        json_str = """
        {
            "name": "Root",
            "children": [
                {
                    "name": "Child 1",
                    "children": [
                        {
                            "name": "Grandchild 1-1",
                            "children": []
                        },
                        {
                            "name": "Grandchild 1-2",
                            "children": [
                                {
                                    "name": "Great-grandchild 1-2-1",
                                    "children": []
                                }
                            ]
                        }
                    ]
                },
                {
                    "name": "Child 2",
                    "children": [
                        {
                            "name": "Grandchild 2-1",
                            "children": [
                                {
                                    "name": "Great-grandchild 2-1-1",
                                    "children": [
                                        {
                                            "name": "Great-great-grandchild 2-1-1-1",
                                            "children": []
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        """

        result = parse_jsons(json_str)
        self.assertEqual(len(result), 1)

        tree = result[0]
        self.assertEqual(tree["name"], "Root")
        self.assertEqual(len(tree["children"]), 2)

        # Navigate to Child 1's branch
        child1 = tree["children"][0]
        self.assertEqual(child1["name"], "Child 1")
        self.assertEqual(len(child1["children"]), 2)

        # Navigate to Grandchild 1-2
        grandchild12 = child1["children"][1]
        self.assertEqual(grandchild12["name"], "Grandchild 1-2")
        self.assertEqual(len(grandchild12["children"]), 1)

        # Navigate to Child 2's branch
        child2 = tree["children"][1]
        self.assertEqual(child2["name"], "Child 2")

        # Navigate to the deepest node: Great-great-grandchild 2-1-1-1
        deepest = child2["children"][0]["children"][0]["children"][0]
        self.assertEqual(deepest["name"], "Great-great-grandchild 2-1-1-1")
        self.assertEqual(len(deepest["children"]), 0)

    def test_json_fragment_extraction(self):
        """Test the parser's ability to extract fragments that might be part of larger JSON structures"""
        # This tests whether fragments are correctly identified or rejected
        json_str = """
        Here are some fragments:
        
        Complete object: {"complete": true}
        
        Incomplete object: {"incomplete":
        
        Fragment with delimiter imbalance: {"imbalanced": [1, 2, 3}
        
        Valid nested fragment: {"outer": {"inner": {"value": 42}}}
        
        Fragment containing a complete object: {"partial": {"complete": {"value": 123}
        """

        result = parse_jsons(json_str)

        # It should find the complete objects/fragments
        complete_found = False
        outer_found = False

        for obj in result:
            if isinstance(obj, dict):
                if "complete" in obj and isinstance(obj["complete"], bool):
                    complete_found = True
                elif "outer" in obj and "inner" in obj["outer"]:
                    outer_found = True

        self.assertTrue(complete_found, "Failed to find the complete object")
        self.assertTrue(outer_found, "Failed to find the valid nested fragment")

        # Check that it doesn't extract invalid fragments
        for obj in result:
            if isinstance(obj, dict):
                # The imbalanced fragment should not be extracted
                self.assertFalse(
                    "imbalanced" in obj,
                    "Parser incorrectly extracted fragment with delimiter imbalance",
                )

    def test_overlapping_structures(self):
        """Test how the parser handles overlapping JSON structures"""
        json_str = """
        Consider these overlapping structures:
        
        {"parent": {"child": {"id": 123, "name": "Test"}}}
        
        {"child": {"id": 123, "name": "Test"}}
        
        And these two separate objects that share a structure:
        
        {"config": {"api": {"url": "https://api.example.com", "key": "abc123"}}}
        
        {"api": {"url": "https://api.example.com", "key": "abc123"}}
        """

        result = parse_jsons(json_str)

        # Verify all structures are found
        parent_found = False
        child_found = False
        config_found = False
        api_found = False

        for obj in result:
            if isinstance(obj, dict):
                if "parent" in obj and "child" in obj["parent"]:
                    parent_found = True
                elif "child" in obj and "id" in obj["child"]:
                    child_found = True
                elif "config" in obj and "api" in obj["config"]:
                    config_found = True
                elif "api" in obj and "url" in obj["api"]:
                    api_found = True

        self.assertTrue(parent_found, "Failed to find parent structure")
        self.assertTrue(child_found, "Failed to find child structure")
        self.assertTrue(config_found, "Failed to find config structure")
        self.assertTrue(api_found, "Failed to find api structure")


if __name__ == "__main__":
    unittest.main()
