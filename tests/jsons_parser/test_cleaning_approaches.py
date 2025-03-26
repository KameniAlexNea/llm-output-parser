import unittest

from llm_output_parser.jsons_parser import parse_jsons


class TestCleaningApproaches(unittest.TestCase):
    def test_json_with_comments(self):
        """Test parsing JSON with JavaScript-style comments"""
        json_str = """
        {
            "name": "Product", // This is the product name
            "price": 29.99, /* This is 
            a multi-line comment */
            "inStock": true
        }
        """
        result = parse_jsons(json_str)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Product")
        self.assertEqual(result[0]["price"], 29.99)
        self.assertTrue(result[0]["inStock"])

    def test_json_with_trailing_commas(self):
        """Test parsing JSON with trailing commas (not standard JSON)"""
        json_str = """
        {
            "items": [
                "apple",
                "banana",
                "orange",
            ],
            "settings": {
                "active": true,
                "visible": false,
            }
        }
        """
        result = parse_jsons(json_str)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["items"], ["apple", "banana", "orange"])
        self.assertTrue(result[0]["settings"]["active"])
        self.assertFalse(result[0]["settings"]["visible"])

    def test_json_with_control_characters(self):
        """Test parsing JSON with literal control characters"""
        json_str = '{"message": "Line 1\nLine 2\tTabbed"}'
        result = parse_jsons(json_str)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["message"], "Line 1\nLine 2\tTabbed")

    def test_json_with_mixed_issues(self):
        """Test parsing JSON with multiple issues that require cleaning"""
        json_str = """
        {
            // Configuration
            "server": "example.com",
            "ports": [
                80,
                443,
                8080,
            ],
            "active": true,
            /* Debug mode should be
               disabled in production */
            "debug": false,
        }
        """
        result = parse_jsons(json_str)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["server"], "example.com")
        self.assertEqual(result[0]["ports"], [80, 443, 8080])
        self.assertTrue(result[0]["active"])
        self.assertFalse(result[0]["debug"])

    def test_complex_json_with_multiline_comments(self):
        """Test parsing JSON with complex multiline comments in various positions"""
        json_str = """
        {
            /* This is a header comment
               that spans multiple lines
               and contains various characters: !@#$%^&*() */
            "config": {
                // Database connection settings
                "database": {
                    "host": "db.example.com", /* Primary host */
                    "port": 5432, // Standard PostgreSQL port
                    "username": "admin",
                    /* Security note:
                       Passwords should be stored in environment variables
                       and not in configuration files */ 
                    "password": "PLACEHOLDER",
                    "options": {
                        "timeout": 30, /* Connection timeout in seconds
                                         Increase this value for slow networks */
                        "ssl": true // Always use SSL
                    }
                },
                /* API Server settings
                   These control the web server configuration */
                "server": {
                    "host": "0.0.0.0", // Listen on all interfaces
                    "port": 8080,
                    "workers": 4, // Number of worker processes
                    /* Worker calculation:
                       Based on CPU cores (8) / 2 = 4 */
                    "rate_limit": {
                        "enabled": true,
                        // Limit configuration
                        "requests_per_minute": 60, /* Default rate limit
                                                     Can be overridden per-user */
                        "burst": 10 // Allow small bursts
                    }
                },
                /* Feature flags
                   Control which features are enabled */
                "features": {
                    "new_dashboard": true, // Released in v2.5
                    "beta_reporting": false, // Coming in v2.6
                    /* The AI features are still experimental
                       Use with caution */
                    "ai_suggestions": false,
                    "themes": [
                        "light", /* Default */
                        "dark", // Popular choice
                        "high_contrast" /* Accessibility option
                                           Required for WCAG compliance */
                    ]
                }
            }
        }
        """

        result = parse_jsons(json_str)
        self.assertEqual(len(result), 1)

        config = result[0]["config"]

        # Verify database config
        self.assertEqual(config["database"]["host"], "db.example.com")
        self.assertEqual(config["database"]["port"], 5432)
        self.assertEqual(config["database"]["options"]["timeout"], 30)
        self.assertTrue(config["database"]["options"]["ssl"])

        # Verify server config
        self.assertEqual(config["server"]["host"], "0.0.0.0")
        self.assertEqual(config["server"]["workers"], 4)
        self.assertEqual(config["server"]["rate_limit"]["requests_per_minute"], 60)

        # Verify features
        self.assertTrue(config["features"]["new_dashboard"])
        self.assertFalse(config["features"]["beta_reporting"])
        self.assertEqual(len(config["features"]["themes"]), 3)
        self.assertEqual(config["features"]["themes"][2], "high_contrast")

    def test_json_with_exotic_trailing_commas(self):
        """Test JSON with trailing commas in various complex nested structures"""
        json_str = """
        {
            "arrays": {
                "empty": [],
                "single": [
                    1,
                ],
                "multiple": [
                    "one",
                    "two",
                    "three",
                ],
                "nested": [
                    [
                        1,
                        2,
                    ],
                    [
                        3,
                        4,
                    ],
                ],
            },
            "objects": {
                "empty": {},
                "simple": {
                    "key": "value",
                },
                "nested": {
                    "level1": {
                        "level2": {
                            "level3": "deep",
                        },
                    },
                },
            },
            "mixed": {
                "arrays_in_objects": {
                    "data": [
                        {"id": 1, "name": "Item 1",},
                        {"id": 2, "name": "Item 2",},
                    ],
                },
                "objects_in_arrays": [
                    {"key1": "value1",},
                    {"key2": "value2",},
                ],
                "complex": [
                    {
                        "data": [
                            1,
                            2,
                            3,
                        ],
                        "metadata": {
                            "type": "numbers",
                            "count": 3,
                        },
                    },
                ],
            },
        }
        """

        result = parse_jsons(json_str)
        self.assertEqual(len(result), 1)

        data = result[0]

        # Test arrays section
        self.assertEqual(len(data["arrays"]["empty"]), 0)
        self.assertEqual(data["arrays"]["single"], [1])
        self.assertEqual(data["arrays"]["multiple"], ["one", "two", "three"])
        self.assertEqual(data["arrays"]["nested"], [[1, 2], [3, 4]])

        # Test objects section
        self.assertEqual(data["objects"]["empty"], {})
        self.assertEqual(data["objects"]["simple"]["key"], "value")
        self.assertEqual(
            data["objects"]["nested"]["level1"]["level2"]["level3"], "deep"
        )

        # Test mixed section
        self.assertEqual(len(data["mixed"]["arrays_in_objects"]["data"]), 2)
        self.assertEqual(
            data["mixed"]["arrays_in_objects"]["data"][1]["name"], "Item 2"
        )
        self.assertEqual(data["mixed"]["objects_in_arrays"][0]["key1"], "value1")
        self.assertEqual(data["mixed"]["complex"][0]["data"], [1, 2, 3])
        self.assertEqual(data["mixed"]["complex"][0]["metadata"]["type"], "numbers")

    def test_mixed_coding_styles_and_issues(self):
        """Test JSON with a mix of different coding styles and issues that need cleaning"""
        json_str = """
        {
            // General configuration
            "appName": "SuperApp", /* This is the main application name */

            // Database settings with trailing commas
            "database": {
                "hosts": [
                    "primary.db.example.com",  // Primary host
                    "secondary.db.example.com",  // Failover host
                    "dr.db.example.com",  // Disaster recovery
                ],
                "credentials": {
                    "username": "db_user",
                    // Password should be encrypted
                    "password": "encrypted:abcdefg",
                },
                "pooling": {
                    "min": 5,
                    "max": 50,
                    "timeout": 30,  // In seconds
                },
            },

            /* User interface settings
               These control the frontend appearance */
            "ui": {
                "theme": "auto",  // Options: light, dark, auto
                "animations": true,
                "sidebar": {
                    "position": "left",  // left or right
                    "collapsed": false,
                    /* These items will appear
                       in the sidebar navigation */
                    "menu_items": [
                        {
                            "id": "dashboard",
                            "icon": "home",
                            "label": "Dashboard",
                            "acl": ["user", "admin"],
                        },
                        {
                            "id": "reports",
                            "icon": "chart",
                            "label": "Reports and Analytics",  // Note the literal newline here
                            "acl": ["analyst", "admin"],
                        },
                        {
                            "id": "settings",
                            "icon": "gear",
                            "label": "Settings",
                            "acl": ["admin"],
                        },
                    ],
                },
                "dialog": {
                    "default_buttons": [
                        "ok",
                        "cancel",
                    ],
                },
            },

            // System limits
            "limits": {
                "requests_per_minute": 100,
                /* The file size limit
                   is in megabytes */
                "max_file_size": 25,
                "max_records_per_page": 500,
            },
        }
        """

        result = parse_jsons(json_str)
        self.assertEqual(len(result), 1)

        data = result[0]

        # Check basic fields
        self.assertEqual(data["appName"], "SuperApp")

        # Check database settings with trailing commas removed
        self.assertEqual(len(data["database"]["hosts"]), 3)
        self.assertEqual(data["database"]["hosts"][2], "dr.db.example.com")
        self.assertEqual(data["database"]["credentials"]["username"], "db_user")
        self.assertEqual(data["database"]["pooling"]["timeout"], 30)

        # Check UI settings with complex comments and literal newlines
        self.assertEqual(data["ui"]["theme"], "auto")
        self.assertEqual(len(data["ui"]["sidebar"]["menu_items"]), 3)
        self.assertEqual(
            data["ui"]["sidebar"]["menu_items"][0]["acl"], ["user", "admin"]
        )

        # Check system limits section
        self.assertEqual(data["limits"]["requests_per_minute"], 100)
        self.assertEqual(data["limits"]["max_file_size"], 25)

    def test_mixed_cleaning_needs(self):
        """Test parsing JSON that requires multiple cleaning approaches simultaneously"""
        json_str = """
        {
            // Config with multiple issues
            "server": {
                "hosts": [
                    "primary.example.com", // Primary
                    "secondary.example.com", // Backup
                ],
                "ports": [80, 443,],  /* Standard ports */
                "timeout": 30
            },
            "features": {
                "logging": true,
                /* Detailed configuration
                   for the logging system */
                "log_level": "info",  // One of: debug, info, warn, error
                "log_format": "json",
                "retention": {
                    "days": 30,
                    "max_size": "2GB",  // Size with unit
                }
            },
            "auth": {
                "provider": "oauth2",
                "settings": {
                    "client_id": "app_client",
                    "scope": "read write",  // Space-separated scopes
                    "token_expiry": 3600,  // In seconds
                }
            }
        }
        """

        result = parse_jsons(json_str)
        self.assertEqual(len(result), 1)

        # Verify the parser handled multiple cleaning issues correctly
        self.assertEqual(len(result[0]["server"]["hosts"]), 2)
        self.assertEqual(result[0]["server"]["ports"], [80, 443])
        self.assertEqual(result[0]["features"]["log_level"], "info")
        self.assertEqual(result[0]["features"]["retention"]["max_size"], "2GB")
        self.assertEqual(result[0]["auth"]["settings"]["scope"], "read write")

    def test_progressive_cleaning_approach(self):
        """Test if the parser uses progressively more aggressive cleaning approaches as needed"""
        # This tests whether the parser tries simple cleaning first before more aggressive approaches
        test_cases = [
            # Case 1: Valid JSON, no cleaning needed
            ('{"simple":true}', True),
            # Case 2: Simple trailing comma, light cleaning needed
            ('{"items":[1,2,3,]}', True),
            # Case 3: Comments, moderate cleaning needed
            ('{"debug":true,/*comment*/}', True),
            # Case 4: Complex mix requiring aggressive cleaning
            (
                """
            {
                // Settings
                "verbose": true,
                "levels": [
                    "low",
                    "medium", // Default
                    "high",
                ],
            }
            """,
                True,
            ),
            # Case 5: Beyond repair, should fail
            ('{"broken": [1,2,', False),
            # Case 6: Control characters requiring special handling
            ('{"message":"Hello\nWorld"}', True),
        ]

        for i, (json_str, should_succeed) in enumerate(test_cases):
            with self.subTest(f"Progressive cleaning case {i+1}"):
                try:
                    result = parse_jsons(json_str)
                    if should_succeed:
                        self.assertEqual(len(result), 1, "Expected 1 JSON object")
                    else:
                        self.fail(f"Case {i+1} should have failed but succeeded")
                except ValueError:
                    if should_succeed:
                        self.fail(f"Case {i+1} should have succeeded but failed")
                    # If we're here and should_succeed is False, the test passes


if __name__ == "__main__":
    unittest.main()
