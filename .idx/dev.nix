# To learn more about how to use Nix to configure your environment
# see: https://developers.google.com/idx/guides/customize-idx-env
{ pkgs, ... }: {
  # Which nixpkgs channel to use.
  channel = "stable-24.05";

  # Use https://search.nixos.org/packages to find packages
  packages = [
    pkgs.python3
    pkgs.postgresql # Allows use of the 'psql' command-line tool
  ];

  # Enable the PostgreSQL database service in the background
  services.postgres.enable = true;

  # IDX-specific configuration
  idx = {
    # Search for extensions on https://open-vsx.org/
    extensions = [
      "ms-python.python"
      "rangav.vscode-thunder-client"
    ];

    workspace = {
      # Runs when a workspace is first created
      onCreate = {
        install = "python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt";
        default.openFiles = [ "README.md" "app.py" ];
      };

      # Runs when a workspace is (re)started
      onStart = {
        # Use the shell script to ensure the venv is activated
        run-server = "./devserver.sh";
      };
    };

    # Defines preview configurations for the web server.
    # Note: The correct structure is idx.previews.previews
    previews = {
      enable = true;
      previews = {
        web = {
          command = ["./devserver.sh"];
          manager = "web";
        };
      };
    };
  };
}