# NixOS Package Searcher

This is a command-line tool for searching NixOS packages.

## Installation

1. Clone this repository.
2. Navigate to the cloned directory.
8. `nix-env -if default.nix`

## Usage

nix-searcher [options] package

### Positional Arguments

- `package`: The name of the package to search for.

### Options

- `-h, --help`: Show help message and exit.
- `--size SIZE`: Number of results to return.
- `--begin BEGIN`: Starting position of results.
- `--channel CHANNEL`: NixOS channel to search in.
- `--sort-by SORT_BY`: Field to sort by (see options for available fields).
- `--sort-order SORT_ORDER`: Sort order (asc/desc).
- `--package-set PACKAGE_SET`: Filter by package set.
- `--license LICENSE`: Filter by package license.
- `--maintainer MAINTAINER`: Filter by package maintainer.
- `--platform PLATFORM`: Filter by platform.
- `--info`: Show detailed info about the package.

### Sorting Fields

- `_score`: Rating of match between the query and the result.
- `package_pname`: Package name.
- `package_pversion`: Package version.
- `package_attr_name`: Attribute name of the package.
- `package_maintainers`: Package maintainers.
- `package_license`: Package license.
- `package_description`: Description of the package.
- `package_homepage`: Home page of the package.
- `package_system`: Target system (e.g., x86_64-linux).
- `package_platforms`: Supported platforms.
- `package_position`: The position of the package in the repository.
- `package_longDescription`: Long description of the package.
- `package_outputs`: Package outputs (e.g., bin, lib).
- `package_broken`: The status of the package (e.g., broken or not).
- `package_insecure`: Security status of the package.
- `package_unfree`: License status (e.g., free or non-free).

## Examples

Search for a package named "example" and display detailed information:

`nix-searcher --info example`

Search for a package named "example" in the unstable channel and sort the results by package version in descending order:

`nix-searcher --channel unstable --sort-by package_pversion --sort-order desc example`

Search for a package named "example" maintained by "John Doe" and display detailed information:

`nix-searcher --maintainer "John Doe" --info example`

Search for a package named "example" available for the "x86_64-linux" platform:

`nix-searcher --platform x86_64-linux example`

# TODO
 - [ ] Enhance error handling.
 - [x] Make installation easier.
 - [ ] Add search by flakes, options.

## License

This project is licensed under the GPL-3.0 License.

