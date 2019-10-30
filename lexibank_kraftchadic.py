import attr
from pathlib import Path

from pylexibank import progressbar
from pylexibank.dataset import Dataset as BaseDataset

# import lingpy
# from clldutils.misc import slug
# from clldutils.path import Path
# from clldutils.text import strip_chars
# from pycldf.sources import Source
# from pylexibank.providers import qlc


class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = "kraftchadic"

    def cmd_makecldf(self, args):
        # Add sources
        args.writer.add_sources()

        # Add languages
        language_lookup = args.writer.add_languages(lookup_factory="Name")

        # Add concepts
        concept_lookup = {}
        for concept in self.concepts:
            args.writer.add_concept(
                ID=concept["ID"],
                Name=concept["Name"],
                Concepticon_ID=concept["Concepticon_ID"],
                Concepticon_Gloss=concept["Concepticon_Gloss"],
            )

            concept_lookup[concept["Name"]] = concept["ID"]

        # Add forms
        for entry in progressbar(
            self.raw_dir.read_csv("clean_data.tsv", delimiter="\t", dicts=True)
        ):
            args.writer.add_forms_from_value(
                Language_ID=language_lookup[entry["language"]],
                Parameter_ID=concept_lookup[entry["concept"]],
                Value=entry["value"],
                Source=["Kraft1981"],
            )
