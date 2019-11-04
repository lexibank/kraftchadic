import attr
from pathlib import Path

from pylexibank import progressbar
from pylexibank.dataset import Dataset as BaseDataset

from clldutils.misc import slug


class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = "kraftchadic"

    def cmd_makecldf(self, args):
        # Add sources
        args.writer.add_sources()

        # Add languages
        language_lookup = args.writer.add_languages(lookup_factory="Name")

        # Add concepts
        concept_lookup = args.writer.add_concepts(
            id_factory=lambda x: x.number + "_" + slug(x.english),
            lookup_factory="Name",
        )

        # Add forms
        for entry in progressbar(
            self.raw_dir.read_csv("clean_data3.tsv", delimiter="\t", dicts=True)
        ):
            args.writer.add_forms_from_value(
                Language_ID=language_lookup[entry["LANGUAGE"]],
                Parameter_ID=concept_lookup[entry["CONCEPT"]],
                Value=entry["VALUE"],
                Source=["Kraft1981"],
            )
