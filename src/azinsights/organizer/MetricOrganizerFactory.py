from organizer.DCGMMetricOrganizer import DCGMMetricOrganizer
from organizer.IBMetricOrganizer import IBMetricOrganizer
from organizer.MetricOrganizer import MetricOrganizer

import logging

logger = logging.getLogger(__name__)

class MetricOrganizerFactory:
    '''Class used to instantiate children of MetricOrganizer'''
    @staticmethod
    def Factory(organizer_type: str = 'DCGM'):
        '''Provides instance of a certain organizer type.
        
        Parameters
        ----------
        organizer_type : str
            A string representing the name of the metric organizer 

        Returns
        -------
        MetricOrganizer
            An instance of a subclass of MetricOrganizer
        
        '''
        logger.debug('Factory')
        organizers = {
            'DCGM': DCGMMetricOrganizer,
            'IB': IBMetricOrganizer
        }
        if organizer_type not in organizers:
            raise Exception('{0} is not a known organizer in MetricOrganizerFactory.'.format(organizer_type))
        return organizers[organizer_type]()
        