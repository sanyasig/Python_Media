import configparser
import  os

config = 0;

def read_config():
    config = configparser.ConfigParser()
    config.read(os.path.expanduser('~') + '/settings.ini')
    print(config.sections())
    return config


def get_config(type):
    config = read_config()
    return {
        'youtube': config['youtube'],
        'b': 2,
        'pc' : config['pc'],
    }[type]



