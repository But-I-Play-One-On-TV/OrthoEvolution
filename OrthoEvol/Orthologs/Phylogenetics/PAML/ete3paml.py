"""Integration of ETE3 for using PAML's codeml."""
import os
from ete3 import EvolTree, Tree

from OrthoEvol.Tools.otherutils import csvtolist
from OrthoEvol.Tools.logit import LogIt


class ETE3PAML(object):
    """Use ETE3's M1 model to run PAML's codeml for orthology inference."""

    def __init__(self, alignmentfile, speciestree, workdir=''):
        """Initialize main variables/files to be used.

        :param alignmentfile:  Input alignment file in fasta format
        :param speciestree:  A newick formatted species tree.
        :param workdir:  Directory of alignment file and species tree.
                         (Default value = '')
        """
        self.ete3paml_log = LogIt().default(logname="ete3paml", logfile=None)
        self.alignmentfile = alignmentfile
        self.speciestree = speciestree
        self.workdir = workdir

        # Import your species tree
        self._speciestree = Tree(self.speciestree, format=1)
        # TODO import organisms list

        # Import alignment file as string
        alignment_file = open(self.alignmentfile, 'r')
        alignment_str = alignment_file.read()
        self.aln_str = alignment_str
        alignment_file.close()

    def prune_tree(self, organisms):
        """Prune branches for species not in the alignment file.

        Keep branches in the species tree for species in the alignment file
        Some species may not be present in the alignment file due to lack of
        matching with blast or simply the gene not being in the genome.

        :param organisms: A list of organisms in the alignment file.
        """

        if os.path.isfile(organisms):
            organismslist = csvtolist(organisms)
        else:
            organismslist = organisms

        branches2keep = []
        for organism in organismslist:
            if organism in self.aln_str:
                branches2keep.append(organism)
            else:
                self.ete3paml_log.warning('No sequence for %s.' % organism)

            self._speciestree.prune(branches2keep, preserve_branch_length=True)

            # Write the tree to a file
            self._speciestree.write(outfile=os.path.join(self.workdir,
                                                         'temptree.nw'))
            self.ete3paml_log.info('temptree.nw was created.')

    def run(self, pamlsrc, output_folder, model='M1'):
        """Run PAML using ETE.

        The default model is M1 as it is best for orthology inference in
        our case. You can use models `M2`, `M0`, `M3`.

        Ensure that you have the correct path to your codeml binary. It should
        be in the paml `/bin`.

        :param pamlsrc: Path to the codemly binary.
        :param output_folder: The name of the output folder.
        :param model: The model to be used. (Default value = 'M1')
        """

        # Import the newick tree
        tree = EvolTree('temptree.nw')

        # Import the alignment
        tree.link_to_alignment(self.alignmentfile)

        tree.workdir = self.workdir

        # Set the binpath of the codeml binary
        tree.execpath = pamlsrc
        # Run the model M1, M2, M3, or M0
        model_path = model + '.' + output_folder
        tree.run_model(model_path)
        self.ete3paml_log.info('Codeml is generating data in %s.' % model_path)
