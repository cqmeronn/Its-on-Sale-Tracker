"""Script to initialise the database by creating all tables defined in the models."""

from pipeline.common.db import engine
from pipeline.common.db import Base
from pipeline.common import models

def main():
    Base.metadata.create_all(bind=engine)
    print("Created tables")

if __name__ == "__main__":
    main()
