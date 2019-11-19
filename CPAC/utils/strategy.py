import os
import six
import warnings
import logging

logger = logging.getLogger('workflow')


class Strategy(object):

    def __init__(self):
        self.resource_pool = {}
        self.leaf_node = None
        self.leaf_out_file = None
        self.name = []

    def append_name(self, name):
        self.name.append(name)

    def get_name(self):
        return self.name

    def set_leaf_properties(self, node, out_file):
        self.leaf_node = node
        self.leaf_out_file = out_file

    def get_leaf_properties(self):
        return self.leaf_node, self.leaf_out_file

    def get_resource_pool(self):
        return self.resource_pool

    def get_nodes_names(self):
        pieces = [n.split('_') for n in self.name]
        assert all(p[-1].isdigit() for p in pieces)
        return ['_'.join(p[:-1]) for p in pieces]

    def get_node_from_resource_pool(self, resource_key):
        try:
            return self.resource_pool[resource_key]
        except:
            logger.error('No node for output: %s', resource_key)
            raise

    def update_resource_pool(self, resources, override=False):
        for key, value in resources.items():
            if key in self.resource_pool and not override:
                raise Exception(
                    'Key %s already exists in resource pool, '
                    'replacing with %s ' % (key, value)
                )
            self.resource_pool[key] = value

    def __getitem__(self, resource_key):
        assert isinstance(resource_key, six.string_types)
        try:
            return self.resource_pool[resource_key]
        except:
            logger.error('No node for output: %s', resource_key)
            raise

    def __contains__(self, resource_key):
        assert isinstance(resource_key, six.string_types)
        return resource_key in self.resource_pool

    def fork(self):
        fork = Strategy()
        fork.resource_pool = dict(self.resource_pool)
        fork.leaf_node = self.leaf_node
        fork.out_file = str(self.leaf_out_file)
        fork.leaf_out_file = str(self.leaf_out_file)
        fork.name = list(self.name)
        return fork

    @staticmethod
    def get_forking_points(strategies):

        forking_points = []

        for strat in strategies:

            strat_node_names = set(strat.get_nodes_names())

            strat_forking = []
            for counter_strat in strategies:
                counter_strat_node_names = set(counter_strat.get_nodes_names())

                strat_forking += list(strat_node_names - counter_strat_node_names)

            strat_forking = list(set(strat_forking))
            forking_points += [strat_forking]

        return forking_points

    @staticmethod
    def get_forking_labels(strategies):

        fork_names = []

        # fork_points is a list of lists, each list containing node names of
        # nodes run in that strat/fork that are unique to that strat/fork
        fork_points = Strategy.get_forking_points(strategies)
        
        for fork_point in fork_points:
            
            fork_point.sort()

            fork_name = []

            for fork in fork_point:
                
                fork_label = ''

                # TODO: reorganize labels
                if 'anat_mni_ants_register' in fork:
                    fork_label = 'anat-ants'
                if 'anat_mni_fnirt_register' in fork:
                    fork_label = 'anat-fnirt'
                if 'anat_mni_flirt_register' in fork:
                    fork_label = 'anat-flirt'
                if 'func_to_epi_ants' in fork:
                    fork_label = 'func-ants'
                if 'func_to_epi_fsl' in fork:
                    fork_label = 'func-fsl'
                if 'func_preproc_afni' in fork:
                    fork_label = 'func-3dautomask'
                if 'func_preproc_fsl' in fork:
                    fork_label = 'func-bet'
                if 'func_preproc_fsl_afni' in fork:
                    fork_label = 'func-bet-3dautomask'    
                if 'anat_refined' in fork:
                    fork_label = 'func-anat-refined'   
                if 'epi_distcorr' in fork:
                    fork_label = 'dist-corr'
                if 'bbreg' in fork:
                    fork_label = 'bbreg'
                
                if 'aroma' in fork:
                    fork_label = 'aroma'
                if 'nuisance' in fork:
                    fork_label = 'nuisance'
                if 'frequency_filter' in fork:
                    fork_label = 'freq-filter'
                
                if 'median' in fork:
                    fork_label = 'median'
                if 'motion_stats' in fork:
                    fork_label = 'motion'
                if 'slice' in fork:
                    fork_label = 'slice'
                if 'anat_preproc_afni' in fork:
                    fork_label = 'anat-afni'
                if 'anat_preproc_bet' in fork:
                    fork_label = 'anat-bet'
                if 'anat_preproc_ants' in fork:
                    fork_label = 'anat-ants'
                if 'anat_preproc_unet' in fork:
                    fork_label = 'anat-unet'

                fork_name += [fork_label]

            fork_names.append('_'.join(sorted(set(fork_name))))

        return dict(zip(strategies, fork_names))
