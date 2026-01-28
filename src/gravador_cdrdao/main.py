from __future__ import annotations

import os
import sys

from gravador_cdrdao.app import iniciar


def main() -> None:
    if os.geteuid() == 0:
        print("O Gravador CDRDAO não deve ser executado como root.")
        sys.exit(1)
    sys.exit(iniciar())


if __name__ == "__main__":
    main()
