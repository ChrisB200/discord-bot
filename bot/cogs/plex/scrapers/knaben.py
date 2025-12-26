import requests

BASE_URL = "https://api.knaben.org/v1"


def format_bytes(num_bytes: int) -> str:
    GB = 1024**3
    MB = 1024**2

    if num_bytes < GB:
        return f"{num_bytes / MB:.1f} MB"
    else:
        return f"{num_bytes / GB:.1f} GB"


class Knaben:
    def __init__(self):
        pass

    def search(self, query, order_by="seeders", size=50):
        res = requests.post(
            BASE_URL,
            json={
                "query": query,
                "order_by": order_by,
                "size": size,
                "hide_unsafe": True,
                "hide_xxx": True,
            },
        )
        return self.filter_results(res.json())

    def filter_results(self, response: dict):
        filtered_results = []
        for result in response["hits"]:
            filtered_results.append(
                {
                    "name": result["title"],
                    "magnet": result["magnetUrl"],
                    "seeders": result["seeders"],
                    "size": format_bytes(int(result["bytes"])),
                }
            )
        return filtered_results
