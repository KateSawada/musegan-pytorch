import os
import yaml
import logging
import argparse


def get_argument_parser(description=None):
    parser = argparse.ArgumentParser(description)
    parser.add_argument("-m", "--model_dir", type=str, default="model",
            help="The directory for a trained model is saved.")
    parser.add_argument("-c", "--conf", dest="configs", default=[], nargs="*",
            help="A list of configuration items. "
                 "An item is a file path or a 'key=value' formatted string. "
                 "The type of a value is determined by applying int(), float(), and str() "
                 "to it sequencially.")
    return parser


class Config:
    def __init__(self, config_file_name):
        super().__setattr__('dict', {})
        self.CONFIG_FILE_NAME = config_file_name

    def __setattr__(self, key, value):
        try:
            super().__getattr__(key)
        except AttributeError:
            self[key] = value
        else:
            raise KeyError("{} is reserved".format(key))

    def __getattr__(self, key):
        try:
            return super().__getattr__(key)
        except AttributeError:
            return self.dict[key]

    def __setitem__(self, key, value):
        if key in self.dict and self.dict[key] != value:
            logging.info("'{}' is set to '{}' instead of '{}'.".format(
                key, self.dict[key], value))
        self.dict[key] = value

    def __getitem__(self, key):
        return self.dict[key]

    def load(self, model_dir, configs, initialize=False, print=True):
        save_config_file = os.path.join(model_dir, self.CONFIG_FILE_NAME)
        if os.path.exists(save_config_file):
            configs = [save_config_file] + configs
        elif not initialize:
            raise ValueError("{} is an invalid model directory".format(model_dir))

        for cfg in configs:
            kv = [s.strip() for s in cfg.split("=", 1)]
            if len(kv) == 1:
                if not os.path.exists(cfg):
                    raise ValueError("The file '{}' doesn't exist.".format(cfg))
                obj = yaml.load(open(cfg).read(), Loader=yaml.FullLoader)
                for k, v in obj.items():
                    self[k] = v
            else:
                k, v = kv
                try:
                    v = int(v)
                except ValueError:
                    try:
                        v = float(v)
                    except ValueError:
                        v_norm = v.lower().strip()
                        if v_norm == 'true':
                            v = True
                        elif v_norm == 'false':
                            v = False
                        elif v_norm == 'null':
                            v = None
                self[k] = v

        if not os.path.exists(save_config_file) and initialize:
            self.save(model_dir)

        if print:
            logging.info("All configurations:\n" + repr(self))

    def save(self, model_dir):
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
        config_yml = yaml.dump(self.dict, default_flow_style=False)
        with open(os.path.join(model_dir, self.CONFIG_FILE_NAME), "w+") as f:
            f.write(config_yml)

    def __repr__(self):
        o = []
        for key in sorted(self.dict):
            o.append("{} = {}".format(key, self.dict[key]))
        return '\n'.join(o)


config = Config('save.yml')
