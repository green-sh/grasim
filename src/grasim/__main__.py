import argparse
import grasim.game as grasim

def start():
    parser = argparse.ArgumentParser("Grasim")
    parser.add_argument("-d", "--dir", help="Set directory of save files", type=str, default=".")

    args = parser.parse_args()

    grasim.start_game(args.dir)

if __name__ == "__main__":
    start()