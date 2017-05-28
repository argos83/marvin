import os


def main(publisher, cfg):
    os.environ['SOME_MARVIN_TEST'] = "%s - %s" % (id(publisher), id(cfg))
