from datetime import datetime

from __version__ import __version__


TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class Build:
    def __init__(self, *, production: bool = False):
        self.production = production
        self.version = __version__

    @staticmethod
    def _generate_version_code() -> int:
        """Generate version code
        Every 3 minutes increase it by +1

        :return: version code
        :rtype: int
        """
        start_time = "2023-01-30 00:00:00"
        start_dev = datetime.strptime(start_time, TIME_FORMAT)
        current_date = datetime.now()
        difference = current_date - start_dev
        return int(difference.total_seconds() / 180)  # add +1 every 3 minutes

    def _write_to_file(self):
        with open("version", "w") as file:
            file.write(self.version)

    def write_version_to_file(self):
        if not self.production:
            version_code = self._generate_version_code()
            build_number = f"-{version_code}"
            self.version = f"{__version__}{build_number}"
        self._write_to_file()


if __name__ == "__main__":
    import argparse

    text = """
    Create build version with build number.
    """
    parser = argparse.ArgumentParser(description=text)
    parser.add_argument("-production", action="store_true", help="Creates a build version for production")
    args = parser.parse_args()

    build = Build(production=args.production)
    build.write_version_to_file()
