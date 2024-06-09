{ pkgs ? import <nixpkgs> {} }:

pkgs.stdenv.mkDerivation {
  pname = "nix-searcher";
  version = "1.0";

  src = ./.; 

  nativeBuildInputs = [
    pkgs.autoPatchelfHook
  ];

  buildInputs = [
    pkgs.zlib
  ];

  installPhase = ''
    runHook preInstall
    mkdir -p $out/bin
    cp ./dist/nix-searcher $out/bin
    runHook postInstall
  '';

  meta = with pkgs.lib; {
    description = "NixOS packages search";
    license = licenses.gpl3;
    platforms = platforms.linux;
  };
}
