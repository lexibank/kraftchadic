from pathlib import Path

import pylexibank
from clldutils.misc import slug


class Dataset(pylexibank.Dataset):
    dir = Path(__file__).parent
    id = "kraftchadic"

    def cmd_makecldf(self, args):
        args.writer.add_sources()
        language_lookup = args.writer.add_languages(lookup_factory="Name")
        concept_lookup = args.writer.add_concepts(
            id_factory=lambda x: x.number + "_" + slug(x.english), lookup_factory="Name"
        )

        for entry in pylexibank.progressbar(
            self.raw_dir.read_csv("clean_data.tsv", delimiter="\t", dicts=True)
        ):
            args.writer.add_forms_from_value(
                Language_ID=language_lookup[entry["LANGUAGE"]],
                Parameter_ID=concept_lookup[entry["CONCEPT"]],
                Value=entry["VALUE"],
                Source=["Kraft1981"],
            )
