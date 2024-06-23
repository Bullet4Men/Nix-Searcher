#!/usr/bin/env python3

import requests
import argparse
from rich.tree import Tree
from rich.console import Console
from rich.spinner import Spinner

headers = {
    'Authorization': 'Basic YVdWU0FMWHBadjpYOGdQSG56TDUyd0ZFZWt1eHNmUTljU2g=',
    'Content-Type': 'application/json',
    'Referer': 'https://search.nixos.org/packages?',
}

def get_json(**kwargs) -> dict:
    package_set_filter = []
    package_set_value = kwargs.get("package_set")
    if package_set_value:
        package_set_filter.append({
            "term":{
                "package_attr_set": {
                    "_name": "filter_bucket_package_attr_set",
                    "value": package_set_value
                },
            }
        })

    license_filter = []
    license_value = kwargs.get("license")
    if license_value:
        license_filter.append({
            "term": {
                "package_license_set": {
                    "_name": "filter_bucket_package_license_set",
                    "value": license_value
                }
            }
        })

    maintainer_filter = []
    maintainer_value = kwargs.get("maintainer")
    if maintainer_value:
        maintainer_filter.append({
            "term": {
                "package_maintainers_set": {
                    "_name": "filter_bucket_package_maintainers_set",
                    "value": maintainer_value
                }
            }
        })

    platform_filter = []
    platform_value = kwargs.get("platform")
    if platform_value:
        platform_filter.append({
            "term": {
                "package_platforms": {
                    "_name": "filter_bucket_package_platforms",
                    "value": platform_value
                }
            }
        })

    json_data = {
        "from": kwargs.get("begin"),
        "size": kwargs.get("size"),
        "query": {
            "bool": {
                "filter": [
                    {"term": {"type": {"value": "package", "_name": "filter_packages"}}},
                    {"bool": {"must": [
                        {"bool": {"should": package_set_filter}},
                        {"bool": {"should": license_filter}},
                        {"bool": {"should": maintainer_filter}},
                        {"bool": {"should": platform_filter}}
                    ]}}
                ],
                "must": [
                    {"dis_max": {
                        "queries": [
                            {"multi_match": {
                                "query": kwargs.get("package"),
                                "fields": [
                                    "package_attr_name^9",
                                    "package_pname^6",
                                    "package_description^1.3"
                                ]
                            }},
                            {"wildcard": {
                                "package_attr_name": {
                                    "value": f"*{kwargs.get('package')}*",
                                    "case_insensitive": True
                                }
                            }}
                        ]
                    }}
                ]
            }
        }
    }
                
    response = requests.post(f'https://search.nixos.org/backend/latest-42-nixos-{kwargs["channel"]}/_search', headers=headers, json=json_data)

    return response.json()

def check_sort_order(value):
    if value.lower() not in ['asc', 'desc']:
        raise argparse.ArgumentTypeError("Sort order must be 'asc' or 'desc'")
    return value.lower()


if __name__ == "__main__":
    sort_by_help_msg = """Field to sort by:
_score - Rating of match between the query and the result.
package_pname - Package name.
package_pversion - Package version.
package_attr_name - Attribute name of the package.
package_maintainers - Package maintainers.
package_license - Package license.
package_description - Description of the package.
package_homepage - Home page of the package.
package_system - Target system (for example, x86_64-linux).
package_platforms - Supported platforms.
package_position - The position of the package in the repository.
package_longDescription - Long description of the package.
package_outputs - Package outputs (eg bin, lib).
package_broken - The status of the package (for example, broken or not).
package_insecure - Security status of the package.
package_unfree - License status (for example, free or non-free).
    """

    parser = argparse.ArgumentParser(description="NixOS packages search", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("package", help="The package to search", type=str)
    parser.add_argument("--size", help="Number of results to return", type=int, default=50)
    parser.add_argument("--begin", help="Starting position of results", type=int, default=0)
    parser.add_argument("--channel", help="NixOS channel to search in", type=str, default="24.05")
    parser.add_argument("--sort-by", help=sort_by_help_msg, type=str, default="_score")
    parser.add_argument("--sort-order", help="Sort order (asc/desc)", type=check_sort_order, default="desc")
    parser.add_argument("--package-set", help="Filter by package set", type=str, default=None)
    parser.add_argument("--license", help="Filter by package license", type=str, default=None)
    parser.add_argument("--maintainer", help="Filter by package maintainer", type=str, default=None)
    parser.add_argument("--platform", help="Filter by platform", type=str, default=None)
    parser.add_argument("--info", help="Show detailed info about the package", action="store_true")
    args = parser.parse_args()

    console = Console()

    if args.info:
        kwargs = {"package": args.package, "channel": args.channel}
        kwargs["begin"] = 0
        kwargs["size"] = 50
        kwargs["sort_by"] = "_score"
        kwargs["sort_order"] = "desc"

        with console.status("[bold green]Making request...", spinner="clock"):
            json_response = get_json(**kwargs)
    
        if (len(json_response.get('hits', {}).get('hits', [])) == 0):
            print(f"Error: Package \"{args.package}\" not found!")

        for package in json_response.get('hits', {}).get('hits', []):
            package_info = package.get('_source', {})
            if package_info.get("package_pname") == args.package:
                tree = Tree(f"[green]Package name[/]: {package_info.get('package_pname')}", guide_style="underline2")
                tree.add(f"[blue]Description[/]: {package_info.get('package_description')}")
                tree.add(f"[blue]Version[/]: {package_info.get('package_pversion')}")
                mainteiners = ', '.join([f"{entry['name']}" for entry in package_info.get('package_maintainers')])
                tree.add(f"[blue]Maintainers[/]: {mainteiners}")
                licenses = '; '.join(f"{entry['fullName']}" for entry in package_info.get('package_license'))
                tree.add(f"[blue]License[/]: {licenses}")
                homepages = " ".join(package_info.get('package_homepage'))
                tree.add(f"[blue]Homepage[/]: [steel_blue1 u]{homepages}")
                tree.add(f"[blue]Supported Platforms[/]: {', '.join(package_info.get('package_platforms', []))}")
                tree.add(f"[blue]Status[/]: {'[bright_red]Broken' if package_info.get('package_broken') else '[bright_green]OK'}")
                tree.add(f"[blue]Security Status[/]: {'[bright_red]Insecure' if package_info.get('package_insecure') else '[bright_green]Secure'}")
                programs = ', '.join(package_info.get('package_programs', []))
                tree.add(f"[blue]Package programs[/]: {None if len(programs) == 0 else programs}")
                tree.add(f"[blue]License Status[/]: {'[bright_yellow]Unfree' if package_info.get('package_unfree') else '[yellow3]Free'}")
                tree.add(f"[blue]Long Description[/]: {package_info.get('package_longDescription')}")
                tree.add(f"[blue]Outputs[/]: [bright_cyan]{', '.join(package_info.get('package_outputs'))}")
                console.print(tree)
        else:
            print(f"Error: Package \"{args.package}\" not found!")
    else:
        kwargs = vars(args)

        with console.status("[bold green]Making request...", spinner="clock"):
            json_response = get_json(**kwargs)

        if (len(json_response.get('hits', {}).get('hits', [])) == 0):
            print(f"Error: Package \"{args.package}\" not found!")    

        for package in json_response.get('hits', {}).get('hits', []):
            package_info = package.get('_source')

            tree = Tree(f"[green]Package name[/]: {package_info.get('package_pname')}")
            tree.add(f"[blue]Description[/]: {package_info.get('package_description')}")
            tree.add(f"[blue]Version[/]: {package_info.get('package_pversion')}")
            console.print(tree)
    
