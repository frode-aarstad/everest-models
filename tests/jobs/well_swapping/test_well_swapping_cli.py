import json
from pathlib import Path

import pytest
from everest_models.jobs.fm_well_swapping.cli import main_entry_point
from everest_models.jobs.shared.io_utils import load_json
from sub_testdata import WELL_SWAPPING as TEST_DATA


def test_well_swapping_main_entrypoint_run(copy_testdata_tmpdir) -> None:
    copy_testdata_tmpdir(TEST_DATA)
    output = "well_swap_output.json"
    main_entry_point(
        [
            "run",
            "-p",
            "priorities.json",
            "-c",
            "constraints.json",
            "-o",
            output,
            "-i",
            "wells.json",
            "well_swap_config.yml",
        ]
    )
    assert Path("expected_output.json").read_bytes() == Path(output).read_bytes()


def test_well_swapping_main_entrypoint_schema(switch_cwd_tmp_path) -> None:
    with pytest.raises(SystemExit, match="0"):
        main_entry_point(["schema", "--init"])

    config = Path("well_swapping_config.yml").read_text()
    assert (
        "# config specification:\n# '...' are REQUIRED fields that needs replacing\n"
    ) in config


def test_well_swapping_main_entrypoint_parse(copy_testdata_tmpdir) -> None:
    copy_testdata_tmpdir(TEST_DATA)
    files = tuple(Path().glob("*.*"))
    with pytest.raises(SystemExit, match="0"):
        main_entry_point(
            [
                "parse",
                "well_swap_config.yml",
            ]
        )
    assert files == tuple(Path().glob("*.*"))


def test_well_swapping_main_entrypoint_parse_fault(
    copy_testdata_tmpdir, capsys: pytest.CaptureFixture
) -> None:
    copy_testdata_tmpdir(TEST_DATA)
    priorities = load_json("priorities.json")
    del priorities["WELL-1"]["1"]
    with open("priorities.json", mode="w") as fp:
        json.dump(priorities, fp)
    files = tuple(Path().glob("*.*"))
    with pytest.raises(SystemExit, match="2"):
        main_entry_point(
            [
                "parse",
                "-p",
                "priorities.json",
                "well_swap_config.yml",
            ]
        )
    assert files == tuple(Path().glob("*.*"))
    _, err = capsys.readouterr()
    assert (
        "parse: error: argument -p/--priorities: All entries must contain the same amount of elements/indexes"
        in err
    )