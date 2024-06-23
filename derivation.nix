{ python3Packages }:
with python3Packages;
buildPythonApplication {
  pname = "nix-searcher";
  version = "1.1";

  propagatedBuildInputs = [ rich requests ];

  src = ./src;

  postInstall = ''
    mv "$out/bin/main.py" "$out/bin/nix-searcher"
  '';
}

