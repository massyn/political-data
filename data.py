import os
import logging
import yaml
import csv

try:
    import colorama
    colorama.init()
except ImportError:
    os.system('')  # Enables ANSI escape characters in terminal on Windows

class ColorFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[41m', # Red background
    }
    RESET = '\033[0m'

    def format(self, record):
        # Center the levelname in a field of width 8
        levelname = record.levelname.center(8)
        color = self.COLORS.get(record.levelname.strip(), '')
        record.levelname = f"{color}{levelname}{self.RESET}"
        return super().format(record)

handler = logging.StreamHandler()
handler.setFormatter(ColorFormatter('%(asctime)s - %(levelname)s %(message)s'))
logging.basicConfig(level=logging.INFO, handlers=[handler])

class Data:
    def __init__(self):
        self.database = './data'    # the folder where we store our data schema
        pass

    def jurisdictions(self):
        '''
            Find all the jurisdictions in our database
        '''
        result = []
        for i in os.listdir(self.database):
            if os.path.isdir(f"{self.database}/{i}"):
                result.append(i)

        return result

    def indicators(self,jurisdiction):
        '''
            Find all the indicators for our jurisdiction
        '''
        schema = {
            'title' : None,
            'category' : [ 'Government','Cost of Living','Housing','Safety & Crime','Health','Education','Employment','Economy'],
            'frequency' : ['Month','Quarter','Annual','3 Year'],
            'source' : None,
            'description' : None,
            'schema' : {}
        }

        result = []
        for i in os.listdir(f"{self.database}/{jurisdiction}"):
            if os.path.isdir(f"{self.database}/{jurisdiction}/{i}"):
                if os.path.exists(f"{self.database}/{jurisdiction}/{i}/indicator.yaml"):
                    with open(f"{self.database}/{jurisdiction}/{i}/indicator.yaml",'rt',encoding='utf-8') as y:
                        indicator = yaml.safe_load(y)

                        # check missing fields
                        for f in schema:
                            if not f in indicator:
                                logging.error(f"Indicator {i} is missing the '{f}' field")
                            else:
                                if schema[f] is None and not isinstance(indicator[f],str):
                                    logging.error(f"Indicator {i} field '{f}' should be a string")
                                if isinstance(schema[f],list) and indicator[f] not in schema[f]:
                                    logging.error(f"Indicator {i} field '{f}' is '{indicator[f]}' when it should be one of the following : '{';'.join(schema[f])}'")
                                if isinstance(schema[f],dict) and not isinstance(indicator[f],dict):
                                    logging.error(f"Indicator {i} field '{f}' is expecting a dictionary, and we did not get a dictionary")
                    
                        result.append({
                            'id' : i,
                            'title' : indicator.get('title','error'),
                            'category' : indicator.get('category','error'),
                            'frequency' : indicator.get('frequency','error'),
                            'source' : indicator.get('source','error'),
                            'schema' : indicator.get('schema',{}),
                            'graph' : indicator.get('graph',False),
                            'data' : self.result(jurisdiction,i,is_latest=True)['data']
                        })
                else:
                    logging.error(f"Indicator {i} is missing an indicator.yaml file")

        return result
        
    def result(self,jurisdiction,indicator,is_latest=True):
        '''
            Find the data for the specific indicator
        '''
        output = []
        indicator_meta = {}
        if os.path.exists(f"{self.database}/{jurisdiction}/{indicator}/indicator.yaml"):
            with open(f"{self.database}/{jurisdiction}/{indicator}/indicator.yaml",'rt',encoding='utf-8') as y:
                indicator_meta = yaml.safe_load(y)

                if os.path.exists(f"{self.database}/{jurisdiction}/{indicator}/data.csv"):              
                    with open(f"{self.database}/{jurisdiction}/{indicator}/data.csv", 'rt',encoding='utf-8') as csvfile:
                        reader = csv.DictReader(csvfile)
                        if is_latest:
                            max_date = None
                            max_row = {}
                            for row in reader:
                                if max_date == None:
                                    max_date = row['date']
                                    max_row = row
                                if row['date'] > max_date:
                                    max_date = row['date']
                                    max_row = row
                            output.append(max_row)
                        else:
                            for row in reader:
                                output.append(row)

                else:
                    logging.error(f"Indicator {indicator} is missing a data.csv file")

        else:
            logging.error(f"Indicator {indicator} is missing an indicator.yaml file")

        return { 'indicator' : indicator_meta, 'data' : output }

if __name__ == '__main__':
    D = Data()

    for j in D.jurisdictions():
        logging.info(f"Jurisdiction ==> {j}")
        for i in D.indicators(j):
            logging.info(f"   Indicator ==> {i['title']} ({i['id']})")
            res = D.result(j,i['id'],True)

            for v in i['schema']:
                logging.info(f"                 {i['schema'][v]} ({v}) = {res['data'][0].get(v,' *** missing **')}")
