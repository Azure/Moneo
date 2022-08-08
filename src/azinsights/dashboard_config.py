from configparser import ConfigParser
from shutil import copyfile
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

SOURCE_PREFIXES = ['ProfilingCounters', 'DeviceCounters', 'InfiniBandNetworkCounters']
TEXT_REPLACEMENTS = {'sub_id': '<Subscription-ID>', 'resource_group': '<Resource-Group>', 'app_insights': '<Application-Insights>'}

def get_config_info():
    logger.info('get_config_info')
    config_parser = ConfigParser()
    config_parser.read('config.ini')
    azure_configs = config_parser['azure']
    return azure_configs['subscription_id'], azure_configs['resource_group'], azure_configs['application_insights']

def main():
    logger.info('main')
    sub_id, resource_group, app_insights = get_config_info()
    for prefix in SOURCE_PREFIXES: 
        source = prefix + 'Template' + '.json'
        dest = prefix + '.json'
        copyfile(source, dest)
        logger.debug('Copied {0} into {1}'.format(source, dest))
        with open(file=dest, mode='r+') as dest_file:
            text = dest_file.read()
            text = text.replace(TEXT_REPLACEMENTS['sub_id'], sub_id)
            text = text.replace(TEXT_REPLACEMENTS['resource_group'], resource_group)
            text = text.replace(TEXT_REPLACEMENTS['app_insights'], app_insights)
            dest_file.seek(0)
            dest_file.truncate()
            dest_file.write(text)
            logger.debug('Finished writing into {0}'.format(dest)) 

if __name__ == '__main__':
    main() 