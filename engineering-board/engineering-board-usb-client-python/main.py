import json
import sys
from circuit_python_board_manager import CircuitPythonBoardManager
from eng_board_resources import ClientType

from utils import logger

logger.info("Starting usb-client-python")

engBoard = CircuitPythonBoardManager.find_board(ClientType.EngineeringBoard)

if engBoard is None:
    logger.error(f"No CPy board found for {ClientType.EngineeringBoard}")
    sys.exit(1)

systemPower = engBoard.query_system_power()
logger.info(
    f"SystemPower: {json.dumps([systemPower.to_json(systemPower) for systemPower in systemPower], indent=4)}"
)

# Find the systemPower element that has the name "thrusters"
thrusters = next((system for system in systemPower if system.name == "Thrusters"), None)

if thrusters is None:
    logger.error("Thrusters power information not found.")
    sys.exit(1)

logger.info(f"Thrusters Power before: {thrusters.power}")
thrusters.power -= 3

engBoard.set_system_power(systemPower)

systemPower = engBoard.query_system_power()

thrusters = next((system for system in systemPower if system.name == "Thrusters"), None)

if thrusters is None:
    logger.error("Thrusters power information not found.")
    sys.exit(1)

logger.info(f"Thrusters Power after: {thrusters.power}")
