from alembic import command
from alembic.config import Config
from pathlib import Path

def run():
  root=Path(__file__).resolve().parents[3]
  cfg=Config(str(root / "alembic.ini"))
  cfg.set_main_option("script_location",str(root / "alembic"))
  command.upgrade(cfg,"head")

if __name__=="__main__":
  run()