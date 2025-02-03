{
  description = "Flake for Jira Kanban board generator";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = {nixpkgs, ...}: let
    system = "x86_64-linux";
    pkgs = import nixpkgs {inherit system;};
    pythonEnv = pkgs.python3.withPackages (ps: with ps; [requests]);
    jira_kanban = pkgs.stdenv.mkDerivation {
      pname = "jira-kanban";
      version = "1.0.0";
      src = ./.;
      buildInputs = [pythonEnv];

      installPhase = ''
        mkdir -p $out/bin
        cp jira_kanban.py $out/bin/jira-kanban
        chmod +x $out/bin/jira-kanban
        sed -i "1i #!${pythonEnv}/bin/python3" $out/bin/jira-kanban
      '';

      meta = with pkgs.lib; {
        description = "Executable for fetching Jira tickets and generating an Obsidian MD kanban board";
        license = licenses.mit;
        platforms = platforms.all;
      };
    };
  in {
    defaultPackage.${system} = jira_kanban;
  };
}
