import unittest
import json
import os
from llm_output_parser.jsons_parser import parse_jsons

class TestIntegration(unittest.TestCase):
    def test_llm_response_with_explanation_and_json(self):
        """Test parsing LLM response with explanation and a JSON object"""
        llm_response = '''
        Based on your requirements, here's a recipe for chocolate chip cookies:

        ```json
        {
            "recipe": {
                "name": "Chocolate Chip Cookies",
                "ingredients": [
                    "2 1/4 cups flour",
                    "1 tsp baking soda",
                    "1 cup butter",
                    "3/4 cup sugar",
                    "3/4 cup brown sugar",
                    "2 eggs",
                    "1 tsp vanilla",
                    "2 cups chocolate chips"
                ],
                "instructions": [
                    "Preheat oven to 375°F",
                    "Mix dry ingredients",
                    "Cream butter and sugars, add eggs and vanilla",
                    "Combine all ingredients and add chocolate chips",
                    "Drop spoonfuls onto baking sheet",
                    "Bake for 9-11 minutes"
                ],
                "prep_time": "15 minutes",
                "cook_time": "11 minutes"
            }
        }
        ```

        Let me know if you'd like any modifications to this recipe!
        '''
        
        result = parse_jsons(llm_response)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["recipe"]["name"], "Chocolate Chip Cookies")
        self.assertEqual(len(result[0]["recipe"]["ingredients"]), 8)
        self.assertEqual(len(result[0]["recipe"]["instructions"]), 6)

    def test_llm_response_with_multiple_code_formats(self):
        """Test parsing LLM response with JSON in different formats"""
        llm_response = '''
        Here are three different data formats:

        1. A person object:
        ```json
        {"name": "John", "age": 30}
        ```

        2. A list of colors:
        ```
        ["red", "green", "blue"]
        ```

        3. A configuration object:
        {
          "debug": true,
          "logLevel": "info",
          "timeout": 30
        }
        '''
        
        result = parse_jsons(llm_response)
        self.assertEqual(len(result), 3)
        self.assertIn({"name": "John", "age": 30}, result)
        self.assertIn(["red", "green", "blue"], result)
        self.assertIn({"debug": True, "logLevel": "info", "timeout": 30}, result)

    def test_overlapping_json_extraction(self):
        """Test that overlapping JSON objects are handled correctly"""
        llm_response = '''
        Here's a configuration: {"config": {"inner": {"settings": [1, 2, 3]}}}
        
        The inner part: {"settings": [1, 2, 3]}
        '''
        
        result = parse_jsons(llm_response)
        # Should extract both objects but remove any that completely overlap
        self.assertGreaterEqual(len(result), 1)
        
        # The complete config should be present
        complete_config_present = False
        for r in result:
            if isinstance(r, dict) and "config" in r:
                complete_config_present = True
                break
        
        self.assertTrue(complete_config_present)

    def test_realistic_chatgpt_api_response(self):
        """Test parsing a realistic ChatGPT API response with embedded JSON"""
        llm_response = '''
        I've analyzed your financial data and prepared a comprehensive report:

        ```json
        {
            "financial_summary": {
                "income": {
                    "total": 285000.00,
                    "breakdown": {
                        "salary": 185000.00,
                        "investments": 72000.00,
                        "rental_income": 28000.00
                    },
                    "year_over_year_change": 0.058
                },
                "expenses": {
                    "total": 176500.00,
                    "breakdown": {
                        "housing": 72000.00,
                        "taxes": 51800.00,
                        "transportation": 12400.00,
                        "food": 18200.00,
                        "entertainment": 8600.00,
                        "insurance": 13500.00
                    },
                    "year_over_year_change": 0.034
                },
                "savings": {
                    "total": 108500.00,
                    "saving_rate": 0.381,
                    "year_over_year_change": 0.097
                },
                "investments": {
                    "portfolio_value": 682000.00,
                    "asset_allocation": {
                        "stocks": 0.65,
                        "bonds": 0.20,
                        "real_estate": 0.10,
                        "cash": 0.05
                    },
                    "performance": {
                        "ytd_return": 0.079,
                        "1yr_return": 0.112,
                        "5yr_annualized": 0.088
                    }
                },
                "debt": {
                    "total": 320000.00,
                    "breakdown": {
                        "mortgage": 285000.00,
                        "car_loan": 22000.00,
                        "credit_cards": 3000.00,
                        "other": 10000.00
                    },
                    "debt_to_income_ratio": 1.123
                }
            },
            "analysis": {
                "strengths": [
                    "Strong saving rate (38.1%) well above the recommended 20%",
                    "Healthy asset allocation appropriate for your age",
                    "Mortgage represents 89% of total debt, which is considered 'good debt'"
                ],
                "weaknesses": [
                    "Credit card debt should be eliminated given your income level",
                    "Emergency fund only covers 3 months of expenses - recommend increasing to 6 months"
                ],
                "recommendations": [
                    {
                        "priority": "high",
                        "action": "Pay off credit card balance of $3,000",
                        "impact": "Save $540 in interest annually and improve credit score"
                    },
                    {
                        "priority": "medium",
                        "action": "Increase emergency fund by $36,000",
                        "impact": "Achieve 6 months of expense coverage for greater security"
                    },
                    {
                        "priority": "medium",
                        "action": "Increase retirement contributions by 5%",
                        "impact": "Additional $9,250 annually toward retirement"
                    },
                    {
                        "priority": "low",
                        "action": "Diversify stock holdings across more sectors",
                        "impact": "Reduce volatility while maintaining similar returns"
                    }
                ]
            },
            "retirement_projection": {
                "current_age": 35,
                "retirement_age": 65,
                "life_expectancy": 90,
                "current_retirement_savings": 420000.00,
                "projected_retirement_savings": 4850000.00,
                "annual_retirement_income": 194000.00,
                "retirement_income_replacement_ratio": 0.68,
                "scenarios": [
                    {
                        "name": "Current path",
                        "savings_at_retirement": 4850000.00,
                        "monthly_retirement_income": 16166.67
                    },
                    {
                        "name": "Increased savings (additional 5%)",
                        "savings_at_retirement": 5920000.00,
                        "monthly_retirement_income": 19733.33
                    },
                    {
                        "name": "Early retirement (age 55)",
                        "savings_at_retirement": 2840000.00,
                        "monthly_retirement_income": 9466.67
                    }
                ]
            }
        }
        ```

        Based on this analysis, I'd be happy to discuss specific strategies for addressing the recommendations or answer any questions about your financial position.

        Would you like me to prepare a monthly budget that aligns with these findings?
        '''
        
        result = parse_jsons(llm_response)
        self.assertEqual(len(result), 1)
        
        financial_data = result[0]
        
        # Check deep nested values
        self.assertEqual(financial_data["financial_summary"]["income"]["total"], 285000.00)
        self.assertEqual(financial_data["financial_summary"]["expenses"]["breakdown"]["housing"], 72000.00)
        self.assertEqual(len(financial_data["analysis"]["strengths"]), 3)
        self.assertEqual(financial_data["analysis"]["recommendations"][0]["priority"], "high")
        self.assertEqual(financial_data["retirement_projection"]["scenarios"][1]["name"], "Increased savings (additional 5%)")
        self.assertEqual(financial_data["retirement_projection"]["scenarios"][1]["monthly_retirement_income"], 19733.33)

    def test_json_with_large_array_of_complex_objects(self):
        """Test parsing a JSON with a large array of complex objects"""
        # Generate a large test JSON
        test_items = []
        for i in range(100):  # 100 complex objects
            test_items.append({
                "id": f"ITEM-{i:04d}",
                "timestamp": f"2023-08-{(i % 31) + 1:02d}T{(i % 24):02d}:{(i % 60):02d}:00Z",
                "metrics": {
                    "value1": i * 1.5,
                    "value2": i * i * 0.01,
                    "ratio": 0.5 + (i % 10) * 0.05
                },
                "tags": [f"tag{j}" for j in range(1, (i % 5) + 3)],
                "status": ["pending", "active", "completed", "failed"][i % 4],
                "nested": {
                    "level1": {
                        "level2": {
                            "level3": {
                                "data": [i, i+1, i+2],
                                "flag": i % 2 == 0
                            }
                        }
                    }
                }
            })
        
        large_json = {"items": test_items, "count": len(test_items), "page": 1, "total_pages": 1}
        json_str = json.dumps(large_json)
        
        result = parse_jsons(json_str)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["count"], 100)
        self.assertEqual(len(result[0]["items"]), 100)
        self.assertEqual(result[0]["items"][42]["id"], "ITEM-0042")
        self.assertAlmostEqual(result[0]["items"][42]["metrics"]["value1"], 42 * 1.5)
        self.assertEqual(result[0]["items"][99]["nested"]["level1"]["level2"]["level3"]["data"], [99, 100, 101])

    def test_concurrent_json_extraction_simulation(self):
        """Test the parser's ability to extract multiple JSONs from a complex, interleaved text"""
        llm_response = '''
        Here are three completely different datasets that you requested:

        First, the user analytics:
        ```json
        {
          "user_analytics": {
            "active_users": 12458,
            "new_registrations": 2380,
            "churn_rate": 0.042,
            "average_session_time": 18.3,
            "top_features": [
              {"feature": "Dashboard", "usage_percent": 87.2},
              {"feature": "Reports", "usage_percent": 64.5},
              {"feature": "Social Sharing", "usage_percent": 41.8}
            ]
          }
        }
        ```

        Now, let me simulate an environment with multiple JSON objects embedded in an unstructured text.
        
        The product catalog data includes:
        {
          "products": [
            {"id": "P001", "name": "Premium Widget", "price": 29.99, "in_stock": true},
            {"id": "P002", "name": "Basic Widget", "price": 19.99, "in_stock": true},
            {"id": "P003", "name": "Super Widget", "price": 49.99, "in_stock": false}
          ]
        }
        
        This might be followed by some config data like:
        
        ```
        {
          "api_config": {
            "endpoints": {
              "users": "/api/v2/users",
              "products": "/api/v2/products",
              "orders": "/api/v2/orders"
            },
            "rate_limits": {
              "per_second": 10,
              "per_minute": 100,
              "per_hour": 1000
            },
            "authentication": {
              "type": "OAuth2",
              "token_endpoint": "/oauth/token",
              "expiration": 3600
            }
          }
        }
        ```

        And here's something complex with some unusual formatting and
        overlapping data:
        
        The system {"settings": {"theme": "dark", "notifications": true}} 
        should be compatible with user preferences. 
        
        For user profiles with:
        [
          {"id": 101, "name": "Alice", "preferences": {"theme": "light", "fontSize": "medium"}},
          {"id": 102, "name": "Bob", "preferences": {"theme": "dark", "fontSize": "large"}}
        ]

        Special event data:
        {
          "event": {
            "id": "EVT-2023-08-15",
            "title": "Summer Conference",
            "date": "2023-08-15T09:00:00Z",
            "location": {
              "venue": "Grand Hotel",
              "address": {
                "street": "123 Example St",
                "city": "San Francisco",
                "state": "CA",
                "postal": "94101"
              },
              "gps": {"lat": 37.7749, "lng": -122.4194}
            },
            "attendees": 327,
            "sessions": [
              {
                "id": "SS-001",
                "title": "Welcome Keynote",
                "speaker": "Jane Smith",
                "time": "09:30:00",
                "duration": 60
              },
              {
                "id": "SS-002",
                "title": "Future of Technology",
                "speaker": "John Doe",
                "time": "11:00:00",
                "duration": 45
              }
            ]
          }
        }

        All of these JSON objects should be properly extracted despite the mixed formatting and surrounding text.
        '''
        
        result = parse_jsons(llm_response)
        self.assertGreaterEqual(len(result), 5)  # Should find at least 5 distinct JSON objects
        
        # Create easy lookup to verify objects by distinctive fields
        user_analytics = None
        products = None
        api_config = None
        settings = None
        user_profiles = None
        event = None
        
        for obj in result:
            if isinstance(obj, dict):
                if "user_analytics" in obj:
                    user_analytics = obj
                elif "products" in obj and isinstance(obj["products"], list):
                    products = obj
                elif "api_config" in obj:
                    api_config = obj
                elif "settings" in obj:
                    settings = obj
                elif "event" in obj:
                    event = obj
            elif isinstance(obj, list) and len(obj) > 0 and "preferences" in obj[0]:
                user_profiles = obj
        
        # Verify that we found the main objects
        self.assertIsNotNone(user_analytics, "Failed to extract user analytics JSON")
        self.assertIsNotNone(products, "Failed to extract products JSON")
        self.assertIsNotNone(api_config, "Failed to extract API config JSON")
        self.assertIsNotNone(settings, "Failed to extract settings JSON")
        self.assertIsNotNone(user_profiles, "Failed to extract user profiles JSON")
        self.assertIsNotNone(event, "Failed to extract event JSON")
        
        # Verify specific nested values to ensure proper extraction
        self.assertEqual(user_analytics["user_analytics"]["active_users"], 12458)
        self.assertEqual(products["products"][2]["name"], "Super Widget")
        self.assertEqual(api_config["api_config"]["rate_limits"]["per_hour"], 1000)
        self.assertEqual(settings["settings"]["theme"], "dark")
        self.assertEqual(user_profiles[1]["name"], "Bob")
        self.assertEqual(event["event"]["sessions"][1]["title"], "Future of Technology")
        self.assertEqual(event["event"]["location"]["gps"]["lat"], 37.7749)

    def test_multiple_json_formats_in_one_response(self):
        """Test the parser with a realistic LLM response containing multiple JSON formats"""
        llm_response = '''
        # Analysis of Your Request

        Based on your query, I've prepared several examples demonstrating different ways JSON might appear in LLM responses:

        ## Example 1: Structured Analysis
        ```json
        {
          "request_analysis": {
            "intent": "data_visualization",
            "entities": ["sales", "regional", "quarterly"],
            "confidence": 0.92
          }
        }
        ```

        ## Example 2: A Sample Dataset
        Here's a small dataset you could use:
        [
          {"region": "North", "q1": 45000, "q2": 63000, "q3": 58000, "q4": 72000},
          {"region": "South", "q1": 51000, "q2": 48000, "q3": 53000, "q4": 61000},
          {"region": "East", "q1": 38000, "q2": 42000, "q3": 43000, "q4": 39000},
          {"region": "West", "q1": 69000, "q2": 73000, "q3": 88000, "q4": 91000}
        ]

        ## Example 3: Configuration Options
        For the visualization tool, I recommend these settings:

        ```
        {
          "chart_type": "stacked_bar",
          "colors": ["#3366CC", "#DC3912", "#FF9900", "#109618"],
          "show_legend": true,
          "responsive": true,
          "animation": {
            "duration": 500,
            "easing": "ease-out"
          }
        }
        ```

        ## Example 4: Alternative Data Format
        You might also consider using this nested format:
        {"data": {"regions": {
          "North": {"q1": 45000, "q2": 63000, "q3": 58000, "q4": 72000},
          "South": {"q1": 51000, "q2": 48000, "q3": 53000, "q4": 61000},
          "East": {"q1": 38000, "q2": 42000, "q3": 43000, "q4": 39000},
          "West": {"q1": 69000, "q2": 73000, "q3": 88000, "q4": 91000}
        }}}

        ## Example 5: Code Sample
        Here's how you might use this in a JavaScript visualization:

        ```javascript
        const config = {
          type: "bar",  // chart type
          data: {
            labels: ["Q1", "Q2", "Q3", "Q4"],
            datasets: [
              {
                label: "North",
                data: [45000, 63000, 58000, 72000]
              },
              // other regions...
            ]
          }
        };
        ```

        Does this help with your visualization needs?
        '''
        
        result = parse_jsons(llm_response)
        self.assertGreaterEqual(len(result), 4)
        
        # Create trackers for each expected JSON
        intent_analysis = None
        dataset = None
        chart_config = None
        nested_data = None
        
        # Find each expected JSON
        for obj in result:
            if isinstance(obj, dict):
                if "request_analysis" in obj:
                    intent_analysis = obj
                elif "chart_type" in obj:
                    chart_config = obj
                elif "data" in obj and "regions" in obj["data"]:
                    nested_data = obj
            elif isinstance(obj, list) and len(obj) > 0 and "region" in obj[0]:
                dataset = obj
                
        # Test that we found each expected object
        self.assertIsNotNone(intent_analysis, "Failed to extract intent analysis")
        self.assertIsNotNone(dataset, "Failed to extract dataset array")
        self.assertIsNotNone(chart_config, "Failed to extract chart configuration")
        self.assertIsNotNone(nested_data, "Failed to extract nested data format")
        
        # Additional checks on the content
        self.assertEqual(intent_analysis["request_analysis"]["intent"], "data_visualization")
        self.assertEqual(len(dataset), 4)
        self.assertEqual(dataset[3]["region"], "West")
        self.assertTrue(chart_config["show_legend"])
        self.assertEqual(nested_data["data"]["regions"]["East"]["q3"], 43000)

    def test_real_world_extraction_scenarios(self):
        """Test parser with realistic extraction scenarios that might occur in applications"""
        test_cases = [
            # Case 1: JSON inside an API response simulation
            ('''
            HTTP/1.1 200 OK
            Content-Type: application/json
            
            {"status":"success","data":{"user_id":12345,"token":"abc123"}}
            ''', 1),
            
            # Case 2: JSON in HTML-like context
            ('''
            <div class="response">
              <pre>{"success":true,"count":42}</pre>
              <p>The operation completed successfully</p>
            </div>
            ''', 1),
            
            # Case 3: Multiple JSON objects in logging-like format
            ('''
            [2023-08-15 14:32:10] INFO: Request received {"method":"GET","path":"/api/user/123"}
            [2023-08-15 14:32:11] DEBUG: Processing {"user_id":123,"permissions":["read","write"]}
            [2023-08-15 14:32:12] INFO: Response sent {"status":200,"body":{"name":"John","email":"john@example.com"}}
            ''', 3),
            
            # Case 4: JSON in SQL-like statement
            ('''
            INSERT INTO logs (timestamp, data) VALUES (
              '2023-08-15 15:45:23',
              '{"event":"user_login","user_id":456,"ip":"192.168.1.1","success":true}'
            );
            ''', 1),
            
            # Case 5: Malformed JSON in real-world context with recovery possible
            ('''
            The API returned a malformed response: 
            {"status":"error",
             "message":"Database timeout",
             "retry_after":30,
             // This field is deprecated
             "error_code":5004,
            }
            ''', 1)
        ]
        
        for i, (input_str, expected_count) in enumerate(test_cases):
            with self.subTest(f"Real-world case {i+1}"):
                result = parse_jsons(input_str)
                self.assertGreaterEqual(len(result), expected_count, 
                                      f"Expected at least {expected_count} JSON objects, got {len(result)}")

if __name__ == '__main__':
    unittest.main()
