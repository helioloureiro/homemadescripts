#! /usr/bin/env -S uv run --script
#
# /// script
# dependencies = [
#    "uvicorn",
#    "fastapi"
# ]
# ///

import argparse
import sys
import subprocess
import logging
import json
import re

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
import uvicorn


DEFAULTS = {"port": 9090, "path": "/metrics"}
__version__ = "0.1.0"

logger = logging.getLogger(__file__)
consoleOutputHandler = logging.StreamHandler()
formatter = logging.Formatter(
    fmt="[%(asctime)s] (%(levelname)s) %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
consoleOutputHandler.setFormatter(formatter)
logger.addHandler(consoleOutputHandler)
logger.setLevel(logging.INFO)


def shellExec(command: str) -> str:
    "run a command and return its output"
    try:
        # result = subprocess.getoutput(command, errors=subprocess.DEVNULL)
        result = subprocess.check_output(
            command, stderr=subprocess.DEVNULL, encoding="utf-8"
        )
        logger.debug(f"shellExec: {result}")
        return result
    except Exception as e:
        logger.error(f"Error executing shell command '{command}': {e}")
        return f"Error: {e}"


class SensorMetrics:
    open_metrics: dict = {}

    def generateMetrics(self) -> list:
        self.dataReset()
        sensors_output = shellExec(["sensors", "-j"])
        logger.debug(f"sensors: {sensors_output}")
        sensorsJSON = json.loads(sensors_output)
        # sensorsJSON = {
        #     "thinkpad-isa-0000": {
        #         "Adapter": "ISA adapter",
        #         "fan1": {"fan1_input": 2786.000},
        #         "CPU": {"temp1_input": 69.000},
        #         "GPU": {},
        #         "temp3": {"temp3_input": 69.000},
        #         "temp4": {"temp4_input": 0.000},
        #         "temp5": {"temp5_input": 69.000},
        #         "temp6": {"temp6_input": 69.000},
        #         "temp7": {"temp7_input": 69.000},
        #         "temp8": {},
        #     }
        # }
        self.getOpenMetrics([], sensorsJSON)

        return []

    def dataReset(self):
        self.open_metrics = {}

    def getOpenMetrics(self, header: list, data_dict: dict):
        if isinstance(data_dict, dict):
            for k, v in data_dict.items():
                logger.debug(f"k={k}, v={v}")
                if isinstance(v, dict):
                    self.getOpenMetrics(header + [k], v)
                else:
                    logger.debug(
                        f"Value is not dictionary: header={header}, k={k}, v={v}"
                    )
                    try:
                        v = float(v)
                    except ValueError:
                        logger.debug(f"invalid value: {v}")
                        continue
                    metric_head = self.generateMetricHeader(header, k)
                    metric_description = " ".join(header)
                    metric_description += f" {k}"

                    if metric_head in self.open_metrics:
                        logger.error(f"metric name '{metric_head}' already exists")

                    self.open_metrics[metric_head] = {
                        "value": v,
                        "description": metric_description,
                    }
                    logger.debug(
                        f"Adding: metric_head={metric_head}, value={v}, description='{metric_description}'"
                    )
        else:
            logger.debug(f"Not dictionary: header={header}, data_dict={data_dict}")

    def generateMetricHeader(self, header: list, key: str) -> str:
        metric_header = "_".join(header)
        metric_header = re.sub(" ", "_", metric_header)
        return f"{metric_header}_{key}"


if __name__ == "__main__":
    parse = argparse.ArgumentParser(
        description="Script to expose the sensors as open metrics"
    )
    parse.add_argument(
        "--port", type=int, default=DEFAULTS["port"], help="Port to listen"
    )
    parse.add_argument(
        "--path", default=DEFAULTS["path"], help="The path to serve the metrics"
    )

    parse.add_argument(
        "--version",
        action=argparse.BooleanOptionalAction,
        help="Print version and exit",
    )
    parse.add_argument(
        "--printout",
        action=argparse.BooleanOptionalAction,
        help="Print the exposed metrics found in the system",
    )

    parse.add_argument("--loglevel", default="info", help="Logging level")

    args = parse.parse_args()

    if args.loglevel != "info":
        logger.setLevel(args.loglevel.upper())

    if args.version is True:
        print(sys.argv[0], __version__)
        sys.exit(0)

    if args.printout is True:
        mts = SensorMetrics()
        mts.generateMetrics()
        for k, v in mts.open_metrics.items():
            description = v["description"]
            print(f"#HELP {k} {description}")
            print(f"#TYPE {k} gauge")
            print(f"{k}: {v['value']}")
        sys.exit(0)

    app = FastAPI()

    @app.get(args.path, response_class=PlainTextResponse)
    async def metrics():
        logger.info(f"serving web page on {args.path}")
        mts = SensorMetrics()
        mts.generateMetrics()
        resp = list()
        for k, v in mts.open_metrics.items():
            description = v["description"]
            resp.append(f"#HELP {k} {description}")
            resp.append(f"#TYPE {k} gauge")
            resp.append(f"{k}: {v['value']}")
        return "\n".join(resp)

    logger.info(f"starting service on port {args.port}")
    uvicorn.run(app, host="127.0.0.1", port=args.port)
