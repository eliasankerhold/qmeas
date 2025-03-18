import json
import os
from datetime import datetime

from qmeas.qsample import QSample

class QDict:
    def __init__(self, name: str, file: str):
        self.name = name
        self.file = file
        self._params = {'timestamp': None}

    def __getitem__(self, key: str):
         if key in self._params.keys():
              return self._params[key]
         
         else:
            raise KeyError(f'{key} not found.')

    def __setitem__(self, key: str, val: float):
        if key not in self._params.keys():
            self._params[key] = val
            self.save_params()

        else:
            raise Exception(f"A parameter named '{key}' already exists. To update an existing parameter, use 'update_parameter'.")
        
    def __str__(self):
        s = f'--- {self.name} ---\n'
        for key, val in self._params.items():
            s += f'{key}: {val}\n'

        return s

    def __repr__(self):
        return self.__str__()
    
    def save_params(self):
        self._params['timestamp'] = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        try:
            with open(self.file, 'w') as f:
                json.dump(self._params, f, indent=4)

        except Exception as ex: 
            print(f'Could not save parameters to {self.file}!')
            print(ex)

    def add_parameter(self, key: str, val: float):
        self.__setitem__(key, val)

    def update_parameter(self, key: str, val: float):
        if key in self._params.keys():
            self._params[key] = val
            self.save_params()

        else:
            raise Exception(f"A parameter named '{key}' does not exist. To add a new parameter, use 'add_parameter'.")

    def delete_parameter(self, key: str):
        if key in self._params.keys():
            self._params.pop(key)
            self.save_params()
        
        else:
            raise Exception(f"A parameter named '{key}' does not exist. To add a new parameter, use 'add_parameter'.")


class QBaseParameters(QDict):
    def __init__(self, sample: QSample, name: str, parameters: dict = None):
        super().__init__(name=name, file=os.path.join(sample.work_dir, 'parameters', f'{name.replace(" ", "_")}.txt'))
        self.sample = sample
        self.wrk_dir = os.path.join(sample.work_dir, 'parameters')

        self._params['sample'] = self.sample.sample
        self._params['structure'] = self.sample.structure

        if not os.path.isdir(os.path.join(self.sample.work_dir, 'parameters')):
            os.mkdir(os.path.join(self.sample.work_dir, 'parameters'))

        if parameters is not None:
            for key, val in parameters.items():
                self.add_parameter(key, val)
 

class QLinkedParameters(QDict):
    def __init__(self, base: QBaseParameters, name: str, parameters: dict = None):
        self.base = base
        self.file = os.path.join(self.base.wrk_dir, f'{base.name.replace(" ", "_")}-LINKED-{name.replace(" ", "_")}.txt')

        super().__init__(name=name, file=self.file)
        self._params['base'] = self.base.name
        self._params['base_file'] = self.base.file

        if parameters is not None:
            for key, val in parameters.items():
                self.add_parameter(key, val)

    def __base_param_check(self, key: str):
        if key in self.base._params.keys():
            raise Exception(f'Base parameters cannot be changed from within a linked parameter object.')

    def __getitem__(self, key: str):
        if key in self._params.keys():
            return self._params[key]
        
        elif key in self.base._params.keys():
            return self.base._params[key]
         
        else:
            raise KeyError(f'{key} not found.')
        

    def __setitem__(self, key: str, val: float):
        self.__base_param_check(key)
        
        if key not in self._params.keys():
            self._params[key] = val
            self.save_params()

        else:
            raise Exception(f"A parameter named '{key}' already exists. To update an existing parameter, use 'update_parameter'.")

    def update_parameter(self, key, val):
        self.__base_param_check(key)
        
        if key in self._params.keys():
            self._params[key] = val
            self.save_params()

        else:
            raise Exception(f"A parameter named '{key}' does not exist. To add a new parameter, use 'add_parameter'.")
        
    def delete_parameter(self, key):
        self.__base_param_check(key)

        super().delete_parameter(key)

    def save_params(self):
        self._params['timestamp'] = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        try:
            with open(self.file, 'w') as f:
                json.dump(self._params, f, indent=4)

        except Exception as ex: 
            print(f'Could not save parameters to {self.file}!')
            print(ex)
